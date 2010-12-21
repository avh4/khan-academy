#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime, logging
import math
from google.appengine.api import users
from google.appengine.api import memcache

from google.appengine.ext import db
import cajole
import app
import util
import consts
import points
from search import Searchable
from app import App

# Setting stores per-application key-value pairs
# for app-wide settings that must be synchronized
# across all GAE instances.
class Setting(db.Model):

    value = db.StringProperty()

    @staticmethod
    def cached_library_content_date(val = None):
        if val is None:
            setting = Setting.get_by_key_name("cached_library_content_date")
            if setting is not None:
                return setting.value
            return None
        else:
            setting = Setting.get_or_insert("cached_library_content_date")
            setting.value = val
            setting.put()
            return setting.value

class UserExercise(db.Model):

    user = db.UserProperty()
    exercise = db.StringProperty()
    streak = db.IntegerProperty(default = 0)
    longest_streak = db.IntegerProperty(default = 0)
    first_done = db.DateTimeProperty(auto_now_add=True)
    last_done = db.DateTimeProperty()
    total_done = db.IntegerProperty(default = 0)
    last_review = db.DateTimeProperty(default=datetime.datetime.min)
    review_interval_secs = db.IntegerProperty(default=(60 * 60 * 24 * 3)) # Default 3 days until review
    proficient_date = db.DateTimeProperty()
    seconds_per_fast_problem = db.FloatProperty(default = 3.0) # Seconds expected to finish a problem 'quickly' for badge calculation
    
    _USER_EXERCISE_KEY_FORMAT = "UserExercise.all().filter('user = '%s')"
    @staticmethod
    def get_for_user_use_cache(user):
        user_exercises_key = UserExercise._USER_EXERCISE_KEY_FORMAT % user.email()
        user_exercises = memcache.get(user_exercises_key)
        if user_exercises is None:
            query = UserExercise.all()
            query.filter('user =', user)
            user_exercises = query.fetch(1000)
            memcache.set(user_exercises_key, user_exercises)
        return user_exercises
    
    def put(self):
        user_exercises_key = UserExercise._USER_EXERCISE_KEY_FORMAT % self.user.email()
        memcache.delete(user_exercises_key)
        db.Model.put(self)

    def get_exercise(self):
        if not hasattr(self, "cached_exercise"):
            query = Exercise.all()
            query.filter('name =', self.exercise)
            self.cached_exercise = query.get()
        return self.cached_exercise

    def required_streak(self):
        return self.get_exercise().required_streak()

    def reset_streak(self):
        if self.get_exercise().summative:
            # Reset streak to latest 10 milestone
            self.streak = (self.streak / consts.CHALLENGE_STREAK_BARRIER) * consts.CHALLENGE_STREAK_BARRIER
        else:
            self.streak = 0

    def struggling_threshold(self):
        return self.get_exercise().struggling_threshold()

    @staticmethod
    def is_struggling_with(user_exercise, exercise):
        return user_exercise.streak == 0 and user_exercise.longest_streak < exercise.required_streak() and user_exercise.total_done > exercise.struggling_threshold() 

    def is_struggling(self):
        return UserExercise.is_struggling_with(self, self.get_exercise())

    def get_review_interval(self):
        review_interval = datetime.timedelta(seconds=self.review_interval_secs)
        return review_interval

    def schedule_review(self, correct, now=datetime.datetime.now()):
        # if the user is not now and never has been proficient, don't schedule a review
        if (self.streak + correct) < self.required_streak() and self.longest_streak < self.required_streak():
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
        if not proficient and self.longest_streak < self.required_streak():
            # Not proficient and never has been so nothing to do
            return

        user_data = UserData.get_or_insert_for(self.user)
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
    seconds_per_fast_problem = db.FloatProperty(default = 3.0) # Seconds expected to finish a problem 'quickly' for badge calculation

    # True if this exercise is a quasi-exercise generated by
    # combining the content of other exercises
    summative = db.BooleanProperty(default=False)

    # Teachers contribute raw html with embedded CSS and JS
    # and we sanitize it with Caja before displaying it to
    # students.
    author = db.UserProperty()
    raw_html = db.TextProperty()
    last_modified = db.DateTimeProperty()    
    safe_html = db.TextProperty()
    safe_js = db.TextProperty()
    last_sanitized = db.DateTimeProperty(default=datetime.datetime.min)
    sanitizer_used = db.StringProperty()

    @staticmethod
    def to_display_name(name):
        return name.replace('_', ' ').capitalize()

    def display_name(self):
        return Exercise.to_display_name(self.name)

    def required_streak(self):
        if self.summative:
            return consts.REQUIRED_STREAK * len(self.covers)
        else:
            return consts.REQUIRED_STREAK

    def struggling_threshold(self):
        return 3 * self.required_streak()

    def summative_children(self):
        if not self.summative:
            return []
        query = db.Query(Exercise)
        query.filter("name IN ", self.covers)
        return query

    def summative_parents(self):
        query = db.Query(Exercise)
        query.filter("summative = ", True)
        query.filter("covers = ", self.name)
        return query

    def non_summative_exercise(self, user_data):
        if not self.summative:
            return self

        if len(self.covers) <= 0:
            raise Exception("Summative exercise '%s' does not cover any other exercises" % self.name)

        user_exercise = user_data.get_or_insert_exercise(self.name)

        # For now we just cycle through all of the covered exercises in a summative exercise
        index = user_exercise.total_done % len(self.covers)
        exid = self.covers[index]

        query = Exercise.all()
        query.filter('name =', exid)
        exercise = query.get()

        if not exercise:
            raise Exception("Unable to find covered exercise")

        if exercise.summative:
            return exercise.non_summative_exercise(user_data)
        else:
            return exercise

    def related_videos(self):
        exercise_videos = None
        query = ExerciseVideo.all()
        query.filter('exercise =', self.key())
        return query

    _CURRENT_SANITIZER = "http://caja.appspot.com/"
    def ensure_sanitized(self):
        if self.last_sanitized >= self.last_modified and self.sanitizer_used == Exercise._CURRENT_SANITIZER:
            return
        cajoled = cajole.cajole(self.raw_html)
        if 'error' in cajoled:
            raise Exception(cajoled['html'])
        self.safe_html = db.Text(cajoled['html'])
        self.safe_js = db.Text(cajoled['js'])
        self.last_sanitized = datetime.datetime.now()
        self.sanitizer = Exercise._CURRENT_SANITIZER
        self.put()
        
    
    _EXERCISES_KEY = "Exercise.all()"    
    @staticmethod
    def get_all_use_cache():
        exercises = memcache.get(Exercise._EXERCISES_KEY, namespace=App.version)
        if exercises is None:
            query = Exercise.all().order('h_position')
            exercises = query.fetch(200)
            memcache.set(Exercise._EXERCISES_KEY, exercises, namespace=App.version)
        return exercises

    def put(self):
        memcache.delete(Exercise._EXERCISES_KEY, namespace=App.version)
        db.Model.put(self)


class UserData(db.Model):

    user = db.UserProperty()       
    moderator = db.BooleanProperty(default=False)
    joined = db.DateTimeProperty(auto_now_add=True)
    last_login = db.DateTimeProperty()
    proficient_exercises = db.StringListProperty() # Names of exercises in which the user is *explicitly* proficient
    all_proficient_exercises = db.StringListProperty() # Names of all exercises in which the user is proficient    
    suggested_exercises = db.StringListProperty()
    assigned_exercises = db.StringListProperty()
    badges = db.StringListProperty() # All awarded badges
    need_to_reassess = db.BooleanProperty()
    points = db.IntegerProperty()
    total_seconds_watched = db.IntegerProperty(default = 0)
    coaches = db.StringListProperty()
    map_coords = db.StringProperty()
    expanded_all_exercises = db.BooleanProperty(default=True)
    
    @staticmethod
    def get_for_current_user():
        user = util.get_current_user()
        if user is not None:
            user_data = UserData.get_for(user)
            if user_data is not None:
                return user_data
        return UserData()

    @staticmethod    
    def get_for(user):
        query = UserData.all()
        query.filter('user =', user)
        query.order('-points') # Temporary workaround for issue 289
        return query.get()
    
    @staticmethod    
    def get_or_insert_for(user):
        # Once we have rekeyed legacy entities,
        # the next block can just be a call to .get_or_insert()
        user_data = UserData.get_for(user)
        if user_data is None:
            user_data = UserData.get_or_insert(
                key_name=user.nickname(),
                user=user,
                moderator=False,
                last_login=datetime.datetime.now(),
                proficient_exercises=[],
                suggested_exercises=[],
                assigned_exercises=[],
                need_to_reassess=True,
                points=0,
                coaches=[]
                )
        return user_data

    def get_or_insert_exercise(self, exid):

        userExercise = UserExercise.get_by_key_name(exid, parent=self)

        if not userExercise:
            # There are some old entities lying around that don't have keys.
            # We have to check for them here, but once we have reparented and rekeyed legacy entities,
            # this entire function can just be a call to .get_or_insert()
            query = UserExercise.all()
            query.filter('user =', self.user)
            query.filter('exercise =', exid)
            query.order('-total_done') # Temporary workaround for issue 289
            userExercise = query.get()

        if not userExercise:
            userExercise = UserExercise.get_or_insert(
                key_name=exid,
                parent=self,
                user=self.user,
                exercise=exid,
                streak=0,
                longest_streak=0,
                first_done=datetime.datetime.now(),
                last_done=datetime.datetime.now(),
                total_done=0,
                )

        return userExercise
        
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
    
    def reassess_if_necessary(self, user=None):
        if not self.need_to_reassess or self.all_proficient_exercises is None:
            return
        ex_graph = ExerciseGraph(self, user)
        self.reassess_from_graph(ex_graph)
        
    def is_proficient_at(self, exid, user=None):
        self.reassess_if_necessary(user)
        return (exid in self.all_proficient_exercises)

    def is_explicitly_proficient_at(self, exid):
        return (exid in self.proficient_exercises)

    def is_reviewing(self, exid, user_exercise, time):

        # Short circuit out of full review check if not proficient or review time hasn't come around yet

        if not self.is_proficient_at(exid):
            return False

        if user_exercise.last_review + user_exercise.get_review_interval() > time:
            return False

        ex_graph = ExerciseGraph(self)
        review_exercise_names = map(lambda exercise: exercise.name, ex_graph.get_review_exercises(time))
        return (exid in review_exercise_names)

    def is_struggling_with(self, exid):
        if self.is_proficient_at(exid):
            return False
        else:
            userExercise = UserExercise.all().filter('user =', self.user).filter('exercise =', exid).get()              
            if userExercise and userExercise.is_struggling():
                return True
            else:
                return False
            
    def is_suggested(self, exid):
        self.reassess_if_necessary()
        return (exid in self.suggested_exercises)

    def get_students_data(self):
        coach_email = self.user.email()   
        query = db.GqlQuery("SELECT * FROM UserData WHERE coaches = :1", coach_email)
        students_data = []
        for student_data in query:
            students_data.append(student_data)
        if coach_email.lower() != coach_email:
            students_set = set(map(lambda student_data: student_data.key().id_or_name(), students_data))
            query = db.GqlQuery("SELECT * FROM UserData WHERE coaches = :1", coach_email.lower())
            for student_data in query:
        	    if student_data.key().id_or_name() not in students_set:
        		    students_data.append(student_data)
        return students_data
   
    def get_students(self):
        return map(lambda student_data: student_data.user.email(), self.get_students_data())

    def add_points(self, points):
        if self.points == None:
            self.points = 0
        self.points += points
    
class Video(Searchable, db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()
    playlists = db.StringListProperty()
    keywords = db.StringProperty()
    duration = db.IntegerProperty(default = 0)
    readable_id = db.StringProperty() #human readable, but unique id that can be used in URLS
    INDEX_ONLY = ['title', 'keywords', 'description']
    INDEX_TITLE_FROM_PROP = 'title'
    INDEX_USES_MULTI_ENTITIES = False
    
    @staticmethod
    def get_for_readable_id(readable_id):
        video = None
        query = Video.all()
        query.filter('readable_id =', readable_id)
        # The following should just be:
        # video = query.get()
        # but the database currently contains multiple Video objects for a particular
        # video.  Some are old.  Some are due to a YouTube sync where the youtube urls
        # changed and our code was producing youtube_ids that ended with '_player'.
        # This hack gets the most recent valid Video object.
        key_id = 0
        for v in query:
            if v.key().id() > key_id and not v.youtube_id.endswith('_player'):
                video = v
                key_id = v.key().id()
        # End of hack
        return video

    def first_playlist(self):
        query = VideoPlaylist.all()
        query.filter('video =', self)
        query.filter('live_association =', True)
        return query.get().playlist

    def current_user_points(self):
        user_video = UserVideo.get_for_video_and_user(self, util.get_current_user())
        if user_video:
            return points.VideoPointCalculator(user_video)
        else:
            return 0

class Playlist(Searchable, db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()
    readable_id = db.StringProperty() #human readable, but unique id that can be used in URLS
    INDEX_ONLY = ['title', 'description']
    INDEX_TITLE_FROM_PROP = 'title'
    INDEX_USES_MULTI_ENTITIES = False

class UserPlaylist(db.Model):
    user = db.UserProperty()
    playlist = db.ReferenceProperty(Playlist)
    seconds_watched = db.IntegerProperty(default = 0)
    last_watched = db.DateTimeProperty(auto_now_add = True)

    @staticmethod
    def get_for_user(user):
        query = UserPlaylist.all()
        query.filter('user =', user)
        return query

    @staticmethod
    def get_key_name(playlist, user):
        return user.email() + ":" + playlist.youtube_id

    @staticmethod
    def get_for_playlist_and_user(playlist, user, insert_if_missing=False):

        if not user:
            return None

        key = UserPlaylist.get_key_name(playlist, user)

        if insert_if_missing:
            return UserPlaylist.get_or_insert(
                        key_name = key,
                        user = user,
                        playlist = playlist)
        else:
            return UserPlaylist.get_by_key_name(key)

class UserVideo(db.Model):

    @staticmethod
    def get_key_name(video, user):
        return user.email() + ":" + video.youtube_id

    @staticmethod
    def get_for_video_and_user(video, user, insert_if_missing=False):

        if not user:
            return None

        key = UserVideo.get_key_name(video, user)

        if insert_if_missing:
            return UserVideo.get_or_insert(
                        key_name = key,
                        user = user,
                        video = video,
                        duration = video.duration)
        else:
            return UserVideo.get_by_key_name(key)

    user = db.UserProperty()
    video = db.ReferenceProperty(Video)

    # Farthest second in video watched
    last_second_watched = db.IntegerProperty(default = 0)

    # Number of seconds actually spent watching this video, regardless of jumping around to various
    # scrubber positions. This value can exceed the total duration of the video if it is watched
    # many times, and it doesn't necessarily match the percent wached.
    seconds_watched = db.IntegerProperty(default = 0)

    last_watched = db.DateTimeProperty(auto_now_add = True)
    duration = db.IntegerProperty(default = 0)

    def points(self):
        return points.VideoPointCalculator(self)

class VideoLog(db.Model):
    user = db.UserProperty()
    video = db.ReferenceProperty(Video)
    video_title = db.StringProperty()
    time_watched = db.DateTimeProperty(auto_now_add = True)
    seconds_watched = db.IntegerProperty(default = 0)

    @staticmethod
    def get_for_user_and_day(user, dt):
        query = VideoLog.all()
        query.filter('user =', user)

        query.filter('time_watched <=', dt + datetime.timedelta(days = 1))
        query.filter('time_watched >=', dt)
        query.order('time_watched')

        return query

    def time_started(self):
        return self.time_watched - datetime.timedelta(seconds = self.seconds_watched)

    def time_ended(self):
        return self.time_watched

class ProblemLog(db.Model):

    user = db.UserProperty()
    exercise = db.StringProperty()
    correct = db.BooleanProperty()
    time_done = db.DateTimeProperty()
    time_taken = db.IntegerProperty()
    problem_number = db.IntegerProperty(default = -1) # Used to reproduce problems
    hint_used = db.BooleanProperty(default = False)

    @staticmethod
    def get_for_user_and_day(user, dt):
        query = ProblemLog.all()
        query.filter('user =', user)

        query.filter('time_done <=', dt + datetime.timedelta(days = 1))
        query.filter('time_done >=', dt)
        query.order('time_done')

        return query

    def time_taken_capped_for_reporting(self):
        # For reporting's sake, we cap the amount of time that you can be considered to be
        # working on a single problem at 60 minutes. If you've left your browser open
        # longer, you're probably not actively working on the problem.
        return min(consts.MAX_WORKING_ON_PROBLEM_SECONDS, self.time_taken)

    def time_started(self):
        return self.time_done - datetime.timedelta(seconds = self.time_taken_capped_for_reporting())

    def time_ended(self):
        return self.time_done

# Represents a matching between a playlist and a video
# Allows us to keep track of which videos are in a playlist and
# which playlists a video belongs to (not 1-to-1 mapping)


class VideoPlaylist(db.Model):

    playlist = db.ReferenceProperty(Playlist)
    video = db.ReferenceProperty(Video)
    video_position = db.IntegerProperty()
    live_association = db.BooleanProperty(default = False)  #So we can remove associations without deleting the entry.  We need this so that bulkuploading of VideoPlaylist info has the proper effect.

    _VIDEO_PLAYLIST_KEY_FORMAT = "VideoPlaylist_Videos_for_Playlist_%s"
    _PLAYLIST_VIDEO_KEY_FORMAT = "VideoPlaylist_Playlists_for_Video_%s"

    @staticmethod
    def get_cached_videos_for_playlist(playlist, limit=500):

        key = VideoPlaylist._VIDEO_PLAYLIST_KEY_FORMAT % playlist.key()
        namespace = str(App.version) + "_" + str(Setting.cached_library_content_date())

        videos = memcache.get(key, namespace=namespace)

        if videos is None:
            videos = []
            query = VideoPlaylist.all()
            query.filter('playlist =', playlist)
            query.filter('live_association = ', True)
            query.order('video_position')
            video_playlists = query.fetch(limit)
            for video_playlist in video_playlists:
                videos.append(video_playlist.video)

            memcache.set(key, videos, namespace=namespace)

        return videos

    @staticmethod
    def get_cached_playlists_for_video(video, limit=5):

        key = VideoPlaylist._PLAYLIST_VIDEO_KEY_FORMAT % video.key()
        namespace = str(App.version) + "_" + str(Setting.cached_library_content_date())

        playlists = memcache.get(key, namespace=namespace)

        if playlists is None:
            playlists = []
            query = VideoPlaylist.all()
            query.filter('video =', video)
            query.filter('live_association = ', True)
            video_playlists = query.fetch(limit)
            for video_playlist in video_playlists:
                playlists.append(video_playlist.playlist)

            memcache.set(key, playlists, namespace=namespace)

        return playlists

    @staticmethod
    def get_query_for_playlist_title(playlist_title):
        query = Playlist.all()
        query.filter('title =', playlist_title)
        playlist = query.get()
        query = VideoPlaylist.all()
        query.filter('playlist =', playlist)
        query.filter('live_association = ', True) #need to change this to true once I'm done with all of my hacks
        query.order('video_position')
        return query

# Matching between videos and exercises


class ExerciseVideo(db.Model):

    video = db.ReferenceProperty(Video)
    exercise = db.ReferenceProperty(Exercise)


# Matching between playlists and exercises


class ExercisePlaylist(db.Model):

    exercise = db.ReferenceProperty(Exercise)
    playlist = db.ReferenceProperty(Playlist)

class ExerciseGraph(object):

    def __init__(self, user_data, user=None):
        if user is None:
            user = util.get_current_user()
        user_exercises = UserExercise.get_for_user_use_cache(user)
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
            ex.suggested = None # Not set initially
            ex.assigned = False
            ex.streak = 0
            ex.longest_streak = 0
            ex.total_done = 0
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
                ex.last_done = user_ex.last_done

        def compute_proficient(ex):
            # Consider an exercise proficient if it is explicitly proficient or
            # the user has never missed a problem and a covering ancestor is proficient
            if ex.proficient is not None:
                return ex.proficient
            ex.proficient = False
            if ex.streak == ex.total_done:
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
            ex.points = points.ExercisePointCalculator(ex, ex, ex.suggested, ex.proficient)            

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
            if not ex.summative and ex.proficient and ex.next_review <= now:
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

    def get_summative_exercises(self):
        summative_exercises = []
        for ex in self.exercises:
            if ex.summative:
                summative_exercises.append(ex)
        return summative_exercises
    
    def get_suggested_exercises(self):
        # Mark an exercise as proficient if it or a a covering ancestor is proficient
        # Select all the exercises where the user is not proficient but the 
        # user is proficient in all prereqs.
        suggested_exercises = []
        for ex in self.exercises:
            if ex.suggested:
                suggested_exercises.append(ex)
        return suggested_exercises

    def get_recent_exercises(self, n_recent=2):
        recent_exercises = sorted(self.exercises, reverse=True,
                key=lambda ex: ex.last_done if hasattr(ex, "last_done") else datetime.datetime.min)
        
        recent_exercises = recent_exercises[0:n_recent]

        return filter(lambda ex: hasattr(ex, "last_done"), recent_exercises)
