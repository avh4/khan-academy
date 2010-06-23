#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi
import os
import datetime
import time
import random
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api import memcache
import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine
import qbrary


class UserExercise(db.Model):

    user = db.UserProperty()
    exercise = db.StringProperty()
    streak = db.IntegerProperty()
    longest_streak = db.IntegerProperty()
    first_done = db.DateTimeProperty(auto_now_add=True)
    last_done = db.DateTimeProperty()
    total_done = db.IntegerProperty()
    last_review = db.DateTimeProperty(default=datetime.datetime.min)
    review_interval_secs = db.IntegerProperty(default=86400)

    _USER_EXERCISE_KEY_FORMAT = "UserExercise.all().filter('user = '%s')"
    @staticmethod
    def get_for_user_use_cache(user):
        user_exercises_key = UserExercise._USER_EXERCISE_KEY_FORMAT % user.nickname()
        user_exercises = memcache.get(user_exercises_key)
        if user_exercises is None:
            query = UserExercise.all()
            query.filter('user =', user)
            user_exercises = query.fetch(200)
            memcache.set(user_exercises_key, user_exercises)
        return user_exercises
    
    def put(self):
        user_exercises_key = UserExercise._USER_EXERCISE_KEY_FORMAT % self.user.nickname()
        memcache.delete(user_exercises_key)
        db.Model.put(self)
    
    def get_review_interval(self):
        review_interval = datetime.timedelta(seconds=self.review_interval_secs)
        return review_interval

    def schedule_review(self, correct, now=datetime.datetime.now()):
        # if the user is not now and never has been proficient, don't schedule a review
        if (self.streak + correct) < 10 and self.longest_streak < 10:
            return
        review_interval = self.get_review_interval()
        if correct and self.last_review != datetime.datetime.min:
            time_since_last_review = now - self.last_review
            if time_since_last_review >= review_interval:
                review_interval = time_since_last_review * 2
        if not correct:
            review_interval = review_interval // 3
        if correct:
            self.last_review = now
        else:
            self.last_review = datetime.datetime.min
        self.review_interval_secs = review_interval.days * 86400 + review_interval.seconds
        
    def set_proficient(self, proficient):
        if not proficient and self.longest_streak < 10:
            # Not proficient and never has been so nothing to do
            return
        query = UserData.all()
        query.filter('user =', self.user)
        user_data = query.get()
        if user_data is None:
            user_data = UserData(user=self.user, last_login=datetime.datetime.now(), proficient_exercises=[], suggested_exercises=[], assigned_exercises=[])
        if proficient:
            if self.exercise not in user_data.proficient_exercises:
                    user_data.proficient_exercises.append(self.exercise)
                    user_data.need_to_reassess = True
                    user_data.put()
        else:
            if self.exercise in user_data.proficient_exercises:
                    user_data.proficient_exercises.remove(self.exercise)
                    user_data.need_to_reassess = True
                    user_data.put()

class Exercise(db.Model):

    name = db.StringProperty()
    prerequisites = db.StringListProperty()
    covers = db.StringListProperty()
    v_position = db.IntegerProperty()
    h_position = db.IntegerProperty()
    
    _EXERCISES_KEY = "Exercise.all()"    
    @staticmethod
    def get_all_use_cache():
        exercises = memcache.get(Exercise._EXERCISES_KEY)
        if exercises is None:
            query = Exercise.all().order('h_position')
            exercises = query.fetch(200)
            memcache.set(Exercise._EXERCISES_KEY, exercises)
        return exercises

    def put(self):
        memcache.delete(Exercise._EXERCISES_KEY)
        db.Model.put(self)


class UserData(db.Model):

    user = db.UserProperty()
    joined = db.DateTimeProperty(auto_now_add=True)
    last_login = db.DateTimeProperty()
    proficient_exercises = db.StringListProperty() # Names of exercises in which the user is *explicitly* proficient
    all_proficient_exercises = db.StringListProperty() # Names of all exercises in which the user is proficient    
    suggested_exercises = db.StringListProperty()
    assigned_exercises = db.StringListProperty()
    need_to_reassess = db.BooleanProperty()
    points = db.IntegerProperty()
    
    def reassess_from_graph(self, ex_graph):
        all_proficient_exercises = []
        for ex in ex_graph.get_proficient_exercises():
            all_proficient_exercises.append(ex.name)
        suggested_exercises = []
        for ex in ex_graph.get_suggested_exercises():
            suggested_exercises.append(ex.name)
        is_changed = (all_proficient_exercises != self.all_proficient_exercises or 
                      suggested_exercises != self.suggested_exercises)
        self.all_proficient_exercises = all_proficient_exercises
        self.suggested_exercises = suggested_exercises
        self.need_to_reassess = False
        return is_changed
    
    def reassess_if_necessary(self):
        if not self.need_to_reassess or self.all_proficient_exercises is None:
            return
        ex_graph = ExerciseGraph(self)
        self.reassess_from_graph(ex_graph)
        
    def is_proficient_at(self, exid):
        self.reassess_if_necessary()
        return (exid in self.all_proficient_exercises)
        
    def is_suggested(self, exid):
        self.reassess_if_necessary()
        return (exid in self.suggested_exercises)
    

class Video(db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()
    playlists = db.StringListProperty()
    keywords = db.StringProperty()


class Playlist(db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()


class ProblemLog(db.Model):

    user = db.UserProperty()
    exercise = db.StringProperty()
    correct = db.BooleanProperty()
    time_done = db.DateTimeProperty()
    time_taken = db.IntegerProperty()


# Represents a matching between a playlist and a video
# Allows us to keep track of which videos are in a playlist and
# which playlists a video belongs to (not 1-to-1 mapping)


class VideoPlaylist(db.Model):

    playlist = db.ReferenceProperty(Playlist)
    video = db.ReferenceProperty(Video)
    video_position = db.IntegerProperty()


# Matching between videos and exercises


class ExerciseVideo(db.Model):

    video = db.ReferenceProperty(Video)
    exercise = db.ReferenceProperty(Exercise)


# Matching between playlists and exercises


class ExercisePlaylist(db.Model):

    exercise = db.ReferenceProperty(Exercise)
    playlist = db.ReferenceProperty(Playlist)


class ExerciseGraph(object):

    def __init__(self, user_data):
#        addition_1 = Exercise(name="addition_1", covers=[], prerequisites=[], v_position = 1, h_position = 1)
#        addition_1.suggested = addition_1.proficient = False
#        self.exercises = [addition_1]
#        self.exercise_by_name = {"addition_1": addition_1}
#        return

        user_exercises = UserExercise.get_for_user_use_cache(users.get_current_user())
        exercises = Exercise.get_all_use_cache()
        self.exercises = exercises
        self.exercise_by_name = {}        
        for ex in exercises:
            self.exercise_by_name[ex.name] = ex
            ex.coverers = []
            ex.user_exercise = None
            ex.next_review = None  # Not set initially
            ex.is_review_candidate = False
            ex.is_ancestor_review_candidate = None  # Not set initially
            ex.proficient = None # Not set initially
            ex.suggested = None # Note set initially
            ex.assigned = False
            ex.streak = 0
        for name in user_data.proficient_exercises:
            ex = self.exercise_by_name.get(name)
            if ex:
                ex.proficient = True
        for name in user_data.assigned_exercises:
            ex = self.exercise_by_name.get(name)
            if ex:
                ex.assigned = True
        for ex in exercises:
            for covered in ex.covers:
                self.exercise_by_name[covered].coverers.append(ex)
            ex.prerequisites_ex = []
            for prereq in ex.prerequisites:
                ex.prerequisites_ex.append(self.exercise_by_name[prereq])
        for user_ex in user_exercises:
            ex = self.exercise_by_name.get(user_ex.exercise)
            if ex:
                ex.user_exercise = user_ex
                ex.streak = user_ex.streak
                ex.longest_streak = user_ex.longest_streak
                ex.total_done = user_ex.total_done
                ex.streakwidth = min(200, 20 * ex.streak)

        def compute_proficient(ex):
            # Consider an exercise proficient if it or a covering ancestor is proficient
            if ex.proficient is not None:
                return ex.proficient
            ex.proficient = False
            for c in ex.coverers:
                if compute_proficient(c) is True:
                    ex.proficient = True
                    break
            return ex.proficient

        for ex in exercises:
            compute_proficient(ex)
            
        def compute_suggested(ex):
            if ex.suggested is not None:
                return ex.suggested
            if ex.proficient is True:
                ex.suggested = False
                return ex.suggested
            ex.suggested = True
            # Don't suggest exs that are covered by suggested exs
            for c in ex.coverers:
                if compute_suggested(c) is True:
                    ex.suggested = False
                    return ex.suggested
            # Don't suggest exs if the user isn't proficient in all prereqs
            for prereq in ex.prerequisites_ex:
                if not prereq.proficient:
                    ex.suggested = False
                    break            
            return ex.suggested 
            
        for ex in exercises:
            compute_suggested(ex)
            ex.points = PointCalculator(ex.streak, ex.suggested, ex.proficient)            

    def get_review_exercises(self, now):

# An exercise ex should be reviewed iff all of the following are true:
#   * ex and all of ex's covering ancestors either
#      * are scheduled to have their next review in the past, or
#      * were answered incorrectly on last review (i.e. streak == 0 with proficient == True)
#   * None of ex's covering ancestors should be reviewed
#   * The user is proficient at ex
# The algorithm:
#   For each exercise:
#     traverse it's ancestors, computing and storing the next review time (if not already done), 
#     using now as the next review time if proficient and streak==0
#   Select and mark the exercises in which the user is proficient but with next review times in the past as review candidates
#   For each of those candidates:
#     traverse it's ancestors, computing and storing whether an ancestor is also a candidate
#   All exercises that are candidates but do not have ancestors as candidates should be listed for review

        def compute_next_review(ex):
            if ex.next_review is None:
                ex.next_review = datetime.datetime.min
                if ex.user_exercise is not None and ex.user_exercise.last_review > datetime.datetime.min:
                    next_review = ex.user_exercise.last_review + ex.user_exercise.get_review_interval()
                    if next_review > now and ex.proficient and ex.user_exercise.streak == 0:
                        next_review = now
                    if next_review > ex.next_review:
                        ex.next_review = next_review
                for c in ex.coverers:
                    c_next_review = compute_next_review(c)
                    if c_next_review > ex.next_review:
                        ex.next_review = c_next_review
            return ex.next_review

        def compute_is_ancestor_review_candidate(rc):
            if rc.is_ancestor_review_candidate is None:
                rc.is_ancestor_review_candidate = False
                for c in rc.coverers:
                    rc.is_ancestor_review_candidate = rc.is_ancestor_review_candidate or c.is_review_candidate or compute_is_ancestor_review_candidate(c)
            return rc.is_ancestor_review_candidate

        for ex in self.exercises:
            compute_next_review(ex)
        review_candidates = []
        for ex in self.exercises:
            if ex.proficient and ex.next_review <= now:
                ex.is_review_candidate = True
                review_candidates.append(ex)
            else:
                ex.is_review_candidate = False
        review_exercises = []
        for rc in review_candidates:
            if not compute_is_ancestor_review_candidate(rc):
                review_exercises.append(rc)
        return review_exercises
    
    def get_proficient_exercises(self):
        proficient_exercises = []
        for ex in self.exercises:
            if ex.proficient:
                proficient_exercises.append(ex)
        return proficient_exercises
    
    def get_suggested_exercises(self):
        # Mark an exercise as proficient if it or a a covering ancestor is proficient
        # Select all the exercises where the user is not proficient but the 
        # user is proficient in all prereqs.
        suggested_exercises = []
        for ex in self.exercises:
            if ex.suggested:
                suggested_exercises.append(ex)
        return suggested_exercises        


def PointCalculator(streak, suggested, proficient):
    points = 5 + max(streak, 10)
    if suggested:
        points = points * 3
    if not proficient:
        points = points * 5
    return points


class VideoDataTest(webapp.RequestHandler):

    def get(self):
        self.response.out.write('<html>')
        videos = Video.all()
        for video in videos:
            self.response.out.write('<P>Title: ' + video.title)


class DataStoreTest(webapp.RequestHandler):

    def get(self):
        if users.is_current_user_admin():
            self.response.out.write('<html>')
            user = users.get_current_user()
            if user:
                problems_done = ProblemLog.all()
                for problem in problems_done:
                    self.response.out.write('<P>' + problem.user.nickname() + ' ' + problem.exercise + ' done:' + str(problem.time_done) + ' taken:' + str(problem.time_taken) + ' correct:'
                                            + str(problem.correct))
        else:
            self.redirect(users.create_login_url(self.request.uri))


# Setting this up to make sure the old Video-Playlist associations are flushed before the bulk upload from the local datastore (with the new associations)


class DeleteVideoPlaylists(webapp.RequestHandler):

    def get(self):
        query = VideoPlaylist.all()

        all_video_playlists = query.fetch(450)
        db.delete(all_video_playlists)


class DeleteVideos(webapp.RequestHandler):

    def get(self):
        query = Video.all()

        all_videos = query.fetch(450)
        db.delete(all_videos)


class UpdateVideoData(webapp.RequestHandler):

    def get(self):
        self.response.out.write('<html>')
        yt_service = gdata.youtube.service.YouTubeService()
        playlist_feed = yt_service.GetYouTubePlaylistFeed(uri='http://gdata.youtube.com/feeds/api/users/khanacademy/playlists?start-index=1&max-results=50')

        # The next two blocks delete all the Videos and VideoPlaylists so that we don't get remnant videos or associations

        query = VideoPlaylist.all()
        all_video_playlists = query.fetch(100000)
        db.delete(all_video_playlists)

        query = Video.all()
        all_videos = query.fetch(100000)
        db.delete(all_videos)

        for playlist in playlist_feed.entry:
            self.response.out.write('<p>Playlist  ' + playlist.id.text)
            playlist_id = playlist.id.text.replace('http://gdata.youtube.com/feeds/api/users/khanacademy/playlists/', '')
            playlist_uri = playlist.id.text.replace('users/khanacademy/', '')
            query = Playlist.all()
            query.filter('youtube_id =', playlist_id)
            playlist_data = query.get()
            if not playlist_data:
                playlist_data = Playlist(youtube_id=playlist_id)
            playlist_data.url = playlist_uri
            playlist_data.title = playlist.title.text
            playlist_data.description = playlist.description.text
            playlist_data.put()

            for i in range(0, 4):
                start_index = i * 50 + 1
                video_feed = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri + '?start-index=' + str(start_index) + '&max-results=50')
                for video in video_feed.entry:

                    video_id = video.media.player.url.replace('http://www.youtube.com/watch?v=', '')
                    video_id = video_id.replace('&feature=youtube_gdata', '')
                    query = Video.all()
                    query.filter('youtube_id =', video_id.decode('windows-1252'))
                    video_data = query.get()
                    if not video_data:
                        video_data = Video(youtube_id=video_id.decode('windows-1252'))
                        video_data.playlists = []
                    video_data.title = video.media.title.text.decode('windows-1252')
                    video_data.url = video.media.player.url.decode('windows-1252')
                    if video.media.description.text is not None:
                        video_data.description = video.media.description.text.decode('windows-1252')
                    else:
                        video_data.decription = ' '

                    if playlist.title.text not in video_data.playlists:
                        video_data.playlists.append(playlist.title.text.decode('windows-1252'))
                    video_data.keywords = video.media.keywords.text.decode('windows-1252')
                    video_data.put()
                    query = VideoPlaylist.all()
                    query.filter('playlist =', playlist_data.key())
                    query.filter('video =', video_data.key())
                    playlist_video = query.get()
                    if not playlist_video:
                        playlist_video = VideoPlaylist(playlist=playlist_data.key(), video=video_data.key())
                    self.response.out.write('<p>Playlist  ' + playlist_video.playlist.title)
                    playlist_video.video_position = int(video.position.text)
                    playlist_video.put()


class ViewExercise(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            exid = self.request.get('exid')
            key = self.request.get('key')
            time_warp = self.request.get('time_warp')

            query = UserExercise.all()
            query.filter('user =', user)
            query.filter('exercise =', exid)
            userExercise = query.get()

            query = UserData.all()
            query.filter('user =', user)
            user_data = query.get()
            if user_data is None:
                user_data = UserData(
                    user=user,
                    last_login=datetime.datetime.now(),
                    proficient_exercises=[],
                    suggested_exercises=[],
                    assigned_exercises=[],
                    need_to_reassess=True,
                    points=0,
                    )

            query = Exercise.all()
            query.filter('name =', exid)
            exercise = query.get()

            exercise_videos = None
            query = ExerciseVideo.all()
            query.filter('exercise =', exercise.key())
            exercise_videos = query.fetch(50)

            if not exid:
                exid = 'addition_1'

            if not userExercise:
                userExercise = UserExercise(
                    user=user,
                    exercise=exid,
                    streak=0,
                    longest_streak=0,
                    first_done=datetime.datetime.now(),
                    last_done=datetime.datetime.now(),
                    total_done=0,
                    )
                userExercise.put()

            proficient = False
            endangered = False
            reviewing = False
            if user_data.is_proficient_at(exid):
                proficient = True
                if (userExercise.last_review > datetime.datetime.min and
                    userExercise.last_review + userExercise.get_review_interval() <= self.get_time()):
                    reviewing = True
                if userExercise.streak == 0:
                    endangered = True

            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'points': user_data.points,
                'proficient': proficient,
                'endangered': endangered,
                'reviewing': reviewing,
                'cookiename': user.nickname().replace('@', 'at'),
                'key': userExercise.key(),
                'exercise': exercise,
                'exid': exid,
                'start_time': time.time(),
                'exercise_videos': exercise_videos,
                'extitle': exid.replace('_', ' ').capitalize(),
                'streakwidth': userExercise.streak * 20,
                'logout_url': logout_url,
                'streak': userExercise.streak,
                'time_warp': time_warp,
                }

            path = os.path.join(os.path.dirname(__file__), exid + '.html')
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))
    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)


class ViewVideo(webapp.RequestHandler):

    def get(self):
        video_id = self.request.get('v')
        if video_id:
            query = Video.all()
            query.filter('youtube_id =', video_id)
            video = query.get()

            query = VideoPlaylist.all()
            query.filter('video = ', video)
            video_playlists = query.fetch(5)

            colcount = 0  # used for formating on displayedpage
            rowcount = 0  # used for formating on displayedpage
            for video_playlist in video_playlists:
                query = VideoPlaylist.all()
                query.filter('playlist =', video_playlist.playlist)
                video_playlist.videos = query.fetch(500)

                video_count = 0  # used for formating on displayedpage
                rowcount = 0  # used for formating on displayedpage
                for videos_in_playlist in video_playlist.videos:
                    video_count = video_count + 1
                    if video_count % 3 == 0:  # three video titles per row
                        rowcount = rowcount + 1
                    if rowcount % 2 == 0:
                        videos_in_playlist.current_background = 'highlightWhite'
                    else:
                        videos_in_playlist.current_background = 'highlightGreyRelated'

                    if videos_in_playlist.video_position == video_playlist.video_position:
                        videos_in_playlist.current_video = True
                    else:
                        videos_in_playlist.current_video = False
                    if videos_in_playlist.video_position == video_playlist.video_position - 1:
                        video_playlist.previous_video = videos_in_playlist.video
                    if videos_in_playlist.video_position == video_playlist.video_position + 1:
                        video_playlist.next_video = videos_in_playlist.video

            template_values = {'App' : App, 'video': video, 'video_playlists': video_playlists}
            path = os.path.join(os.path.dirname(__file__), 'viewvideo.html')
            self.response.out.write(template.render(path, template_values))


class ViewExerciseVideos(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = UserData.all()
            query.filter('user =', user)
            user_data = query.get()

            if user_data is None:
                user_data = UserData(
                    user=user,
                    last_login=datetime.datetime.now(),
                    proficient_exercises=[],
                    suggested_exercises=[],
                    assigned_exercises=[],
                    need_to_reassess=True,
                    points=0,
                    )
                user_data.put()

            exkey = self.request.get('exkey')
            if exkey:
                exercise = Exercise.get(db.Key(exkey))
                query = ExerciseVideo.all()
                query.filter('exercise =', exercise.key())

                exercise_videos = query.fetch(50)

                logout_url = users.create_logout_url(self.request.uri)

                template_values = {
                    'App' : App,
                    'points': user_data.points,
                    'username': user.nickname(),
                    'logout_url': logout_url,
                    'exercise': exercise,
                    'first_video': exercise_videos[0].video,
                    'extitle': exercise.name.replace('_', ' ').capitalize(),
                    'exercise_videos': exercise_videos,
                    }

                path = os.path.join(os.path.dirname(__file__), 'exercisevideos.html')
                self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))


class ExerciseAdminPage(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = Exercise.all().order('h_position')
            exercises = query.fetch(200)

            for exercise in exercises:
                exercise.display_name = exercise.name.replace('_', ' ').capitalize()

            template_values = {'App' : App, 'exercises': exercises}

            path = os.path.join(os.path.dirname(__file__), 'exerciseadmin.html')
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))


class ReportIssue(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = UserData.all()
            query.filter('user =', user)
            user_data = query.get()

            if user_data is None:
                user_data = UserData(
                    user=user,
                    last_login=datetime.datetime.now(),
                    proficient_exercises=[],
                    suggested_exercises=[],
                    assigned_exercises=[],
                    need_to_reassess=True,
                    points=0,
                    )
                user_data.put()

            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'points': user_data.points,
                'username': user.nickname(),
                'referer': self.request.headers.get('Referer'),
                'logout_url': logout_url,
                }
            issue_type = self.request.get('type')
            page = 'reportissue_template.html'
            if issue_type == 'Defect':
                page = 'reportproblem.html'
            elif issue_type == 'Enhancement':
                page = 'makesuggestion.html'
            elif issue_type == 'New-Video':
                page = 'requestvideo.html'
            elif issue_type == 'Comment':
                page = 'makecomment.html'
            elif issue_type == 'Question':
                page = 'askquestion.html'
            path = os.path.join(os.path.dirname(__file__), page)
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))


class ViewMapExercises(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:

            query = UserData.all()
            query.filter('user =', user)
            user_data = query.get()

            if user_data is None:
                user_data = UserData(
                    user=user,
                    last_login=datetime.datetime.now(),
                    proficient_exercises=[],
                    suggested_exercises=[],
                    assigned_exercises=[],
                    need_to_reassess=True,
                    points=0,
                    )
            
            knowledge_map_url = '/knowledgemap?'
            
            def exercises_to_query_params(typeChar, exs):
                query_params = ''
                count = 0
                for ex in exs:
                    query_params += '&' + typeChar + str(count) + '=' + ex.name
                    count = count + 1
                return query_params
                    
            ex_graph = ExerciseGraph(user_data)
            if user_data.reassess_from_graph(ex_graph):
                user_data.put()
            for exercise in ex_graph.exercises:
                exercise.display_name = exercise.name.replace('_', '&nbsp;').capitalize()
            review_exercises = ex_graph.get_review_exercises(self.get_time())
            knowledge_map_url += exercises_to_query_params('r', review_exercises)
            suggested_exercises = ex_graph.get_suggested_exercises()
            knowledge_map_url += exercises_to_query_params('s', suggested_exercises)
            knowledge_map_url += exercises_to_query_params('p', ex_graph.get_proficient_exercises())

            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'exercises': ex_graph.exercises,
                'suggested_exercises': suggested_exercises,
                'review_exercises': review_exercises,
                'knowledge_map_url': knowledge_map_url,
                'points': user_data.points,
                'username': user.nickname(),
                'logout_url': logout_url,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewknowledgemap.html')
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))

    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)


class ViewAllExercises(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = UserData.all()
            query.filter('user =', user)
            user_data = query.get()

            if user_data is None:
                user_data = UserData(
                    user=user,
                    last_login=datetime.datetime.now(),
                    proficient_exercises=[],
                    suggested_exercises=[],
                    assigned_exercises=[],
                    need_to_reassess=True,
                    points=0,
                    )
            
            ex_graph = ExerciseGraph(user_data)
            if user_data.reassess_from_graph(ex_graph):
                user_data.put()
            for exercise in ex_graph.exercises:
                exercise.display_name = exercise.name.replace('_', ' ').capitalize()

            review_exercises = ex_graph.get_review_exercises(self.get_time())
            suggested_exercises = ex_graph.get_suggested_exercises()

            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'exercises': ex_graph.exercises,
                'review_exercises': review_exercises,
                'suggested_exercises': suggested_exercises,
                'points': user_data.points,
                'username': user.nickname(),
                'logout_url': logout_url,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewexercises.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)


class VideolessExercises(webapp.RequestHandler):

    def get(self):
        query = Exercise.all().order('h_position')
        exercises = query.fetch(200)
        self.response.out.write('<html>')
        for exercise in exercises:
            query = ExerciseVideo.all()
            query.filter('exercise =', exercise.key())
            videos = query.fetch(200)
            if not videos:
                self.response.out.write('<P><A href="/exercises?exid=' + exercise.name + '">' + exercise.name + '</A>')


class KnowledgeMap(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = Exercise.all().order('h_position')
            exercises = query.fetch(200)

            proficient_exercises = []
            suggested_exercises = []
            review_exercises = []

            proficient_count = 0
            proficient_exercise = self.request.get('p' + str(proficient_count))
            while proficient_exercise:
                proficient_exercises.append(proficient_exercise)
                proficient_count = proficient_count + 1
                proficient_exercise = self.request.get('p' + str(proficient_count))

            suggested_count = 0
            suggested_exercise = self.request.get('s' + str(suggested_count))
            while suggested_exercise:
                suggested_exercises.append(suggested_exercise)
                suggested_count = suggested_count + 1
                suggested_exercise = self.request.get('s' + str(suggested_count))

            review_count = 0
            review_exercise = self.request.get('r' + str(review_count))
            while review_exercise:
                review_exercises.append(review_exercise)
                review_count = review_count + 1
                review_exercise = self.request.get('r' + str(review_count))

            for exercise in exercises:
                exercise.suggested = False
                exercise.proficient = False
                if exercise.name in suggested_exercises:
                    exercise.suggested = True
                if exercise.name in proficient_exercises:
                    exercise.proficient = True
                if exercise.name in review_exercises:
                    exercise.review = True
                name = exercise.name.capitalize()
                name_list = name.split('_')
                exercise.display_name = str(name_list).replace("[u'", "['").replace(", u'", ", '")
                exercise.prereq_string = str(exercise.prerequisites).replace("[u'", "['").replace(", u'", ", '")

            logout_url = users.create_logout_url(self.request.uri)

            template_values = {'App' : App, 'exercises': exercises, 'logout_url': logout_url, 'map_height': 900}

            path = os.path.join(os.path.dirname(__file__), 'knowledgemap.html')
            self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))


class EditExercise(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            exercise_name = self.request.get('name')
            if exercise_name:
                query = Exercise.all().order('h_position')
                exercises = query.fetch(200)

                main_exercise = None
                for exercise in exercises:
                    exercise.display_name = exercise.name.replace('_', ' ').capitalize()
                    if exercise.name == exercise_name:
                        main_exercise = exercise

                query = ExercisePlaylist.all()
                query.filter('exercise =', main_exercise.key())
                exercise_playlists = query.fetch(50)

                query = Playlist.all()
                all_playlists = query.fetch(50)

                query = ExerciseVideo.all()
                query.filter('exercise =', main_exercise.key())
                exercise_videos = query.fetch(50)

                videos = []

                playlist_videos = None
                for exercise_playlist in exercise_playlists:
                    query = VideoPlaylist.all()
                    query.filter('playlist =', exercise_playlist.playlist.key())
                    query.order('video_position')
                    playlist_videos = query.fetch(200)
                    for playlist_video in playlist_videos:
                        videos.append(playlist_video.video)

                template_values = {
                    'App' : App,
                    'exercises': exercises,
                    'exercise_playlists': exercise_playlists,
                    'all_playlists': all_playlists,
                    'exercise_videos': exercise_videos,
                    'playlist_videos': playlist_videos,
                    'videos': videos,
                    'main_exercise': main_exercise,
                    }

                path = os.path.join(os.path.dirname(__file__), 'editexercise.html')
                self.response.out.write(template.render(path, template_values))
        else:

            self.redirect(users.create_login_url(self.request.uri))


class UpdateExercise(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if users.is_current_user_admin():
            exercise_name = self.request.get('name')
            if exercise_name:
                query = Exercise.all()
                query.filter('name =', exercise_name)
                exercise = query.get()
                if not exercise:
                    exercise = Exercise(name=exercise_name)
                    exercise.prerequisites = []
                    exercise.covers = []

                add_prerequisite = self.request.get('add_prerequisite')
                delete_prerequisite = self.request.get('delete_prerequisite')
                add_covers = self.request.get('add_covers')
                delete_covers = self.request.get('delete_covers')
                v_position = self.request.get('v_position')
                h_position = self.request.get('h_position')

                add_video = self.request.get('add_video')
                delete_video = self.request.get('delete_video')
                add_playlist = self.request.get('add_playlist')
                delete_playlist = self.request.get('delete_playlist')

                if add_prerequisite:
                    if add_prerequisite not in exercise.prerequisites:
                        exercise.prerequisites.append(add_prerequisite)
                if delete_prerequisite:
                    if delete_prerequisite in exercise.prerequisites:
                        exercise.prerequisites.remove(delete_prerequisite)
                if add_covers:
                    if add_covers not in exercise.covers:
                        exercise.covers.append(add_covers)
                if delete_covers:
                    if delete_covers in exercise.covers:
                        exercise.covers.remove(delete_covers)
                if v_position:
                    exercise.v_position = int(v_position)
                if h_position:
                    exercise.h_position = int(h_position)

                if add_video:
                    query = ExerciseVideo.all()
                    query.filter('video =', db.Key(add_video))
                    query.filter('exercise =', exercise.key())
                    exercise_video = query.get()
                    if not exercise_video:
                        exercise_video = ExerciseVideo()
                        exercise_video.exercise = exercise
                        exercise_video.video = db.Key(add_video)
                        exercise_video.put()
                if delete_video:
                    query = ExerciseVideo.all()
                    query.filter('video =', db.Key(delete_video))
                    query.filter('exercise =', exercise.key())
                    exercise_videos = query.fetch(200)
                    for exercise_video in exercise_videos:
                        exercise_video.delete()

                if add_playlist:
                    query = ExercisePlaylist.all()
                    query.filter('playlist =', db.Key(add_playlist))
                    query.filter('exercise =', exercise.key())
                    exercise_playlist = query.get()
                    if not exercise_playlist:
                        exercise_playlist = ExercisePlaylist()
                        exercise_playlist.exercise = exercise
                        exercise_playlist.playlist = db.Key(add_playlist)
                        exercise_playlist.put()

                if delete_playlist:
                    query = ExercisePlaylist.all()
                    query.filter('playlist =', db.Key(delete_playlist))
                    query.filter('exercise =', exercise.key())
                    exercise_playlists = query.fetch(200)
                    for exercise_playlist in exercise_playlists:
                        exercise_playlist.delete()

                exercise.put()

                if v_position or h_position:
                    self.redirect('/admin94040')
                else:
                    self.redirect('/editexercise?name=' + exercise_name)
        else:
            self.redirect(users.create_login_url(self.request.uri))


class GraphPage(webapp.RequestHandler):

    def get(self):
        width = self.request.get('w')
        height = self.request.get('h')
        template_values = {'App' : App, 'width': width, 'height': height}

        path = os.path.join(os.path.dirname(__file__), 'graphpage.html')
        self.response.out.write(template.render(path, template_values))

class AdminViewUser(webapp.RequestHandler):

    def get(self):
        username = self.request.get('u')
        if username:

            userdata = None
            exercisedata = None
            query = UserData.all()
            for user_data in query:
                if user_data.user.nickname() == username:
                    userdata = user_data
                    query = UserExercise.all()
                    query.filter('user =', userdata.user)
                    exercisedata = query.fetch(300)
                    break

            template_values = {'App' : App, 'exercise_data': exercisedata, 'user_data': userdata}
            path = os.path.join(os.path.dirname(__file__), 'adminviewuser.html')
            self.response.out.write(template.render(path, template_values))

class RegisterAnswer(webapp.RequestHandler):

    def post(self):
        user = users.get_current_user()
        if user:
            key = self.request.get('key')
            exid = self.request.get('exid')
            correct = int(self.request.get('correct'))
            start_time = float(self.request.get('start_time'))

            elapsed_time = int(float(time.time()) - start_time)

            problem_log = ProblemLog()
            problem_log.user = user
            problem_log.exercise = exid
            problem_log.correct = False
            if correct == 1:
                problem_log.correct = True
            problem_log.time_done = datetime.datetime.now()
            problem_log.time_taken = elapsed_time
            problem_log.put()

            userExercise = db.get(key)
            userExercise.last_done = datetime.datetime.now()

            query = UserData.all()
            query.filter('user =', userExercise.user)
            user_data = query.get()
            
            suggested = user_data.is_suggested(exid)
            proficient = user_data.is_proficient_at(exid)
                
            if user_data.points == None:
                user_data.points = 0
            user_data.points = user_data.points + PointCalculator(userExercise.streak, suggested, proficient)
            user_data.put()

            if userExercise.total_done:
                userExercise.total_done = userExercise.total_done + 1
            else:
                userExercise.total_done = 1
            userExercise.schedule_review(correct == 1, self.get_time())
            if correct == 1:
                userExercise.streak = userExercise.streak + 1
                if userExercise.streak > userExercise.longest_streak:
                    userExercise.longest_streak = userExercise.streak
                if userExercise.streak == 10:
                    userExercise.set_proficient(True)
            else:
                # Can't do the following here because RegisterCorrectness() already
                # set streak = 0.
                # if userExercise.streak == 0:
                    # 2+ in a row wrong -> not proficient
                    # userExercise.set_proficient(False)
                
                # Just in case RegisterCorrectness didn't get called.
                userExercise.streak = 0

            userExercise.put()

            self.redirect('/exercises?exid=' + exid)
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)


class RegisterCorrectness(webapp.RequestHandler):

# A POST request is made via AJAX when the user clicks "Check Answer".
# This allows us to reset the user's streak if the answer was wrong.  If we wait
# until he clicks the "Next Problem" button, he can avoid resetting his streak
# by just reloading the page.

    def post(self):
        user = users.get_current_user()
        if user:
            key = self.request.get('key')
            correct = int(self.request.get('correct'))
            userExercise = db.get(key)
            userExercise.schedule_review(correct == 1, self.get_time())
            if correct == 0:
                if userExercise.streak == 0:
                    # 2+ in a row wrong -> not proficient
                    userExercise.set_proficient(False)
                userExercise.streak = 0
            userExercise.put()
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)


class ViewUsers(webapp.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            query = UserData.all()
            count = 0
            for user in query:
                count = count + 1

            self.response.out.write('Users ' + str(count))
        else:

            # template_values = {'App' : App, 'users': all_users}

            # path = os.path.join(os.path.dirname(__file__), 'viewusers.html')
            # self.response.out.write(template.render(path, template_values))

            self.redirect(users.create_login_url(self.request.uri))


class ViewVideoLibrary(webapp.RequestHandler):

    def get(self):
        colOne = []
        colOne.append('Algebra 1')
        colOne.append('Algebra')
        colOne.append('California Standards Test: Algebra I')
        colOne.append('California Standards Test: Algebra II')
        colOne.append('Arithmetic')
        colOne.append('Pre-algebra')
        colOne.append('Geometry')
        colOne.append('California Standards Test: Geometry')

        colTwo = []
        colTwo.append('Chemistry')

        colTwo.append('Brain Teasers')
        colTwo.append('Current Economics')
        colTwo.append('Banking and Money')
        colTwo.append('Venture Capital and Capital Markets')
        colTwo.append('Finance')
        colTwo.append('Valuation and Investing')
        colTwo.append('Credit Crisis')
        colTwo.append('Geithner Plan')
        colTwo.append('Paulson Bailout')

        colThree = []
        colThree.append('Biology')
        colThree.append('Trigonometry')
        colThree.append('Precalculus')
        colThree.append('Statistics')
        colThree.append('Probability')
        colThree.append('Calculus')
        colThree.append('Differential Equations')

        colFour = []
        colFour.append('History')
        colFour.append('Linear Algebra')
        colFour.append('Physics')

        cols = [colOne, colTwo, colThree, colFour]

        columns = []
        for column in cols:
            new_column = []
            for playlist_title in column:
                query = Playlist.all()
                query.filter('title =', playlist_title)
                playlist = query.get()
                query = VideoPlaylist.all()
                query.filter('playlist =', playlist)
                query.order('video_position')
                playlist_videos = query.fetch(500)
                self.response.out.write(' ' + str(len(playlist_videos)) + ' retrieved for ' + playlist_title + ' ')
                new_column.append(playlist_videos)
            columns.append(new_column)

        # Separating out the columns because the formatting is a little different on each column

        template_values = {
            'App' : App,
            'c1': columns[0],
            'c2': columns[1],
            'c3': columns[2],
            'c4': columns[3],
            'playlist_names': cols,
            }
        path = os.path.join(os.path.dirname(__file__), 'videolibrary.html')
        self.response.out.write(template.render(path, template_values))


class Export(webapp.RequestHandler):

    def get(self):
        query = Exercise.all()
        exercises = query.fetch(50)
        for ex in exercises:
            self.response.out.write(ex)

# A singleton shared across requests
class App(object):
    # This gets reset every time the app is restarted which is at
    # least as often as the static files change.
    start_time = datetime.datetime.now().strftime('%y%m%d%H%M%S')

def main():
    webapp.template.register_template_library('templatefilters')
    application = webapp.WSGIApplication([ 
        ('/', ViewAllExercises),
        ('/library', ViewVideoLibrary),
        ('/syncvideodata', UpdateVideoData),
        ('/exercises', ViewExercise),
        ('/editexercise', EditExercise),
        ('/viewexercisevideos', ViewExerciseVideos),
        ('/knowledgemap', KnowledgeMap),
        ('/viewexercisesonmap', ViewMapExercises),
        ('/testdatastore', DataStoreTest),
        ('/admin94040', ExerciseAdminPage),
        ('/adminusers', ViewUsers),
        ('/videoless', VideolessExercises),
        ('/adminuserdata', AdminViewUser),
        ('/updateexercise', UpdateExercise),
        ('/graphpage.html', GraphPage),
        ('/registeranswer', RegisterAnswer),
        ('/registercorrectness', RegisterCorrectness),
        ('/video', ViewVideo),
        ('/reportissue', ReportIssue),
        ('/export', Export),
        # These are dangerous, should be able to clean things manually from the remote python shell
        # ('/deletevideos', DeleteVideos),
        # ('/deletevideoplaylists', DeleteVideoPlaylists),        

        # Below are all qbrary related pages
        ('/qbrary', qbrary.MainPage),
        ('/subjectmanager', qbrary.SubjectManager),
        ('/editsubject', qbrary.CreateEditSubject),
        ('/viewsubject', qbrary.ViewSubject),
        ('/deletequestion', qbrary.DeleteQuestion),
        ('/deletesubject', qbrary.DeleteSubject),
        ('/changepublished', qbrary.ChangePublished),
        ('/pickquestiontopic', qbrary.PickQuestionTopic),
        ('/pickquiztopic', qbrary.PickQuizTopic),
        ('/answerquestion', qbrary.AnswerQuestion),
        ('/rating', qbrary.Rating),
        ('/viewquestion', qbrary.ViewQuestion),
        ('/editquestion', qbrary.CreateEditQuestion),
        ('/addquestion', qbrary.CreateEditQuestion),
        ('/checkanswer', qbrary.CheckAnswer),
        ('/sessionaction', qbrary.SessionAction),
        ('/initqbrary', qbrary.InitQbrary),
        ], debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()
