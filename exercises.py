import re
import os
import logging
import itertools
import hashlib

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import deferred

from app import App
import datetime
import models
import request_handler
import util
import points
import layer_cache
from badges import util_badges, last_action_cache, custom_badges
from phantom_users import util_notify
from custom_exceptions import MissingExerciseException

@layer_cache.cache(layer=layer_cache.Layers.InAppMemory)
def exercise_template():
    path = os.path.join(os.path.dirname(__file__), "khan-exercises/exercises/khan-exercise.html")

    contents = ""
    f = open(path)

    if f:
        try:
            contents = f.read()
        finally:
            f.close()

    if not len(contents):
        raise MissingExerciseException("Missing exercise template")

    return contents

@layer_cache.cache_with_key_fxn(lambda exercise: "exercise_html_%s" % exercise.name, layer=layer_cache.Layers.InAppMemory)
def exercise_contents(exercise):
    path = os.path.join(os.path.dirname(__file__), "khan-exercises/exercises/%s.html" % exercise.name)

    contents = ""
    f = open(path)

    if f:
        try:
            contents = f.read()
        finally:
            f.close()

    if not len(contents):
        raise MissingExerciseException("Missing exercise content for exid '%s'" % exercise.name)

    re_data_require = re.compile("^<html.*(data-require=\".*\").*>", re.MULTILINE)
    match_data_require = re_data_require.search(contents)
    data_require = match_data_require.groups()[0] if match_data_require else ""

    re_body_contents = re.compile("<body>(.*)</body>", re.DOTALL)
    match_body_contents = re_body_contents.search(contents)
    body_contents = match_body_contents.groups()[0]

    re_script_contents = re.compile("<script>(.*?)</script>", re.DOTALL)
    list_script_contents = re_script_contents.findall(contents)
    script_contents = ";".join(list_script_contents)

    sha1 = hashlib.sha1(contents).hexdigest()

    if not len(body_contents):
        raise MissingExerciseException("Missing exercise body in content for exid '%s'" % exercise.name)

    return (body_contents, script_contents, data_require, sha1)

def reset_streak(user_data, user_exercise):
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.reset_streak()
        user_exercise.put()

        return user_exercise

def attempt_problem(user_data, user_exercise, problem_number, attempt_number, attempt_content, sha1, seed, completed, hint_used, time_taken):

    if user_exercise and user_exercise.belongs_to(user_data):

        dt_now = datetime.datetime.now()
        exercise = user_exercise.exercise_model

        user_exercise.last_done = dt_now
        user_exercise.seconds_per_fast_problem = exercise.seconds_per_fast_problem
        user_exercise.summative = exercise.summative

        user_data.last_activity = user_exercise.last_done
        
        # If a non-admin tries to answer a problem out-of-order, just ignore it
        if problem_number != user_exercise.total_done+1 and not users.is_current_user_admin():
            # Only admins can answer problems out of order.
            raise Exception("Problem number out of order")

        if len(sha1) <= 0:
            raise Exception("Missing sha1 hash of problem content.")

        if len(seed) <= 0:
            raise Exception("Missing seed for problem content.")

        if len(attempt_content) > 500:
            raise Exception("Attempt content exceeded maximum length.")

        # Build up problem log for deferred put
        problem_log = models.ProblemLog(
                key_name = "problemlog_%s_%s_%s" % (user_data.key_email, user_exercise.exercise, problem_number),
                user = user_data.user,
                exercise = user_exercise.exercise,
                problem_number = problem_number,
                time_taken = time_taken,
                time_done = dt_now,
                hint_used = hint_used,
                correct = completed and (attempt_number == 1),
                sha1 = sha1,
                seed = seed,
                count_attempts = attempt_number,
                attempts = [attempt_content],
        )

        if exercise.summative:
            problem_log.exercise_non_summative = exercise.non_summative_exercise(problem_number).name

        # If this is the first attempt, update review schedule appropriately
        if attempt_number == 1:
            user_exercise.schedule_review(completed)

        if completed:

            user_exercise.total_done += 1

            proficient = user_data.is_proficient_at(user_exercise.exercise)

            if problem_log.correct:

                suggested = user_data.is_suggested(user_exercise.exercise)
                points_possible = points.ExercisePointCalculator(user_exercise, suggested, proficient)

                problem_log.points_earned = points_possible
                user_data.add_points(points_possible)

                user_exercise.total_correct += 1
                user_exercise.streak += 1
                user_exercise.longest_streak = max(user_exercise.longest_streak, user_exercise.streak)

                if user_exercise.streak >= exercise.required_streak and not proficient:
                    user_exercise.set_proficient(True, user_data)
                    user_data.reassess_if_necessary()

                    problem_log.earned_proficiency = True
                    
            util_badges.update_with_user_exercise(
                user_data, 
                user_exercise, 
                include_other_badges = True, 
                action_cache=last_action_cache.LastActionCache.get_cache_and_push_problem_log(user_data, problem_log))

            # Update phantom user notifications
            util_notify.update(user_data, user_exercise)

        else:

            if user_exercise.streak == 0:
                # 2+ in a row wrong -> not proficient
                user_exercise.set_proficient(False, user_data)

            user_exercise.reset_streak()

        # Manually clear exercise's memcache since we're throwing it in a bulk put
        user_exercise.clear_memcache()

        # Bulk put
        db.put([user_data, user_exercise])

        # Defer the put of ProblemLog for now, as we think it might be causing hot tablets
        # and want to shift it off to an automatically-retrying task queue.
        # http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
        deferred.defer(models.commit_problem_log, problem_log, _queue="problem-log-queue")

        return user_exercise

class ExerciseAdmin(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        user = models.UserData.current().user
        query = models.Exercise.all().order('name')
        exercises = query.fetch(1000)

        template_values = {'App' : App, 'exercises': exercises}

        self.render_template('exerciseadmin.html', template_values)

class EditExercise(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        exercise_name = self.request.get('name')
        if exercise_name:
            query = models.Exercise.all().order('name')
            exercises = query.fetch(1000)

            main_exercise = None
            for exercise in exercises:
                if exercise.name == exercise_name:
                    main_exercise = exercise

            query = models.ExerciseVideo.all()
            query.filter('exercise =', main_exercise.key())
            exercise_videos = query.fetch(50)

            template_values = {
                'exercises': exercises,
                'exercise_videos': exercise_videos,
                'main_exercise': main_exercise,
                'saved': self.request_bool('saved', default=False),
                }

            self.render_template("editexercise.html", template_values)

class UpdateExercise(request_handler.RequestHandler):
    
    def post(self):
        self.get()

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        user = models.UserData.current().user

        exercise_name = self.request.get('name')
        if not exercise_name:
            self.response.out.write("No exercise submitted, please resubmit if you just logged in.")
            return

        query = models.Exercise.all()
        query.filter('name =', exercise_name)
        exercise = query.get()
        if not exercise:
            exercise = models.Exercise(name=exercise_name)
            exercise.prerequisites = []
            exercise.covers = []
            exercise.author = user
            exercise.summative = self.request_bool("summative", default=False)
            path = os.path.join(os.path.dirname(__file__), exercise_name + '.html')

        v_position = self.request.get('v_position')
        h_position = self.request.get('h_position')
        short_display_name = self.request.get('short_display_name')

        add_video = self.request.get('add_video')
        delete_video = self.request.get('delete_video')
        add_playlist = self.request.get('add_playlist')
        delete_playlist = self.request.get('delete_playlist')

        exercise.prerequisites = []
        for c_check_prereq in range(0, 1000):
            prereq_append = self.request_string("prereq-%s" % c_check_prereq, default="")
            if prereq_append and not prereq_append in exercise.prerequisites:
                exercise.prerequisites.append(prereq_append)

        exercise.covers = []
        for c_check_cover in range(0, 1000):
            cover_append = self.request_string("cover-%s" % c_check_cover, default="")
            if cover_append and not cover_append in exercise.covers:
                exercise.covers.append(cover_append)

        if v_position:
            exercise.v_position = int(v_position)

        if h_position:
            exercise.h_position = int(h_position)

        if short_display_name:
            exercise.short_display_name = short_display_name

        exercise.live = self.request_bool("live", default=False)

        if not exercise.is_saved():
            # Exercise needs to be saved before checking related videos.
            exercise.put()

        video_keys = []
        for c_check_video in range(0, 1000):
            video_append = self.request_string("video-%s" % c_check_video, default="")
            if video_append and not video_append in video_keys:
                video_keys.append(video_append)

        query = models.ExerciseVideo.all()
        query.filter('exercise =', exercise.key())
        existing_exercise_videos = query.fetch(1000)

        existing_video_keys = []
        for exercise_video in existing_exercise_videos:
            existing_video_keys.append(exercise_video.video.key())
            if not exercise_video.video.key() in video_keys:
                exercise_video.delete()
        
        for video_key in video_keys:
            if not video_key in existing_video_keys:
                exercise_video = models.ExerciseVideo()
                exercise_video.exercise = exercise
                exercise_video.video = db.Key(video_key)
                exercise_video.exercise_order = models.VideoPlaylist.all().filter('video =',exercise_video.video).get().video_position
                exercise_video.put()

        exercise.put()
        
        #Start ordering
        ExerciseVideos = models.ExerciseVideo.all().filter('exercise =', exercise.key()).fetch(1000)
        playlists = []
        for exercise_video in ExerciseVideos:
            playlists.append(models.VideoPlaylist.get_cached_playlists_for_video(exercise_video.video))
        
        if playlists:
            
            playlists = list(itertools.chain(*playlists))
            titles = map(lambda pl: pl.title, playlists)
            playlist_sorted = []
            for p in playlists:
                playlist_sorted.append([p, titles.count(p.title)])
            playlist_sorted.sort(key = lambda p: p[1])
            playlist_sorted.reverse()
                
            playlists = []
            for p in playlist_sorted:
                playlists.append(p[0])
            playlist_dict = {}
            exercise_list = []
            playlists = list(set(playlists))
            for p in playlists:
                playlist_dict[p.title]=[]
                for exercise_video in ExerciseVideos:
                    if p.title  in map(lambda pl: pl.title, models.VideoPlaylist.get_cached_playlists_for_video(exercise_video.video)):
                        playlist_dict[p.title].append(exercise_video)
                        # ExerciseVideos.remove(exercise_video)

                if playlist_dict[p.title]:
                    playlist_dict[p.title].sort(key = lambda e: models.VideoPlaylist.all().filter('video =', e.video).filter('playlist =',p).get().video_position)
                    exercise_list.append(playlist_dict[p.title])
        
            if exercise_list:
                exercise_list = list(itertools.chain(*exercise_list))
                for e in exercise_list:
                    e.exercise_order = exercise_list.index(e)
                    e.put()


        self.redirect('/editexercise?saved=1&name=' + exercise_name)

