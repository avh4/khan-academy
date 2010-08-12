#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime, logging
from google.appengine.api import users
from google.appengine.api import memcache

from google.appengine.ext import db
import cajole


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
    moderator = db.BooleanProperty(default=False)
    joined = db.DateTimeProperty(auto_now_add=True)
    last_login = db.DateTimeProperty()
    proficient_exercises = db.StringListProperty() # Names of exercises in which the user is *explicitly* proficient
    all_proficient_exercises = db.StringListProperty() # Names of all exercises in which the user is proficient    
    suggested_exercises = db.StringListProperty()
    assigned_exercises = db.StringListProperty()
    need_to_reassess = db.BooleanProperty()
    points = db.IntegerProperty()
    coaches = db.StringListProperty()
    
    @staticmethod
    def get_for_current_user():
        user = users.get_current_user()
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
        # Once we have reparented and rekeyed legacy entities,
        # the next block can just be a call to .get_or_insert()
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
    
    def get_students(self):
        coach_email = self.user.email()
        query = db.GqlQuery("SELECT * FROM UserData WHERE coaches = :1", coach_email)
        students = []
        for student in query:
            students.append(student.user.email())
        return students
    
class Video(db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()
    playlists = db.StringListProperty()
    keywords = db.StringProperty()
    readable_id = db.StringProperty() #human readable, but unique id that can be used in URLS


class Playlist(db.Model):

    youtube_id = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    description = db.TextProperty()
    readable_id = db.StringProperty() #human readable, but unique id that can be used in URLS


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
    live_association = db.BooleanProperty(default = False)  #So we can remove associations without deleting the entry.  We need this so that bulkuploading of VideoPlaylist info has the proper effect.




# Matching between videos and exercises


class ExerciseVideo(db.Model):

    video = db.ReferenceProperty(Video)
    exercise = db.ReferenceProperty(Exercise)


# Matching between playlists and exercises


class ExercisePlaylist(db.Model):

    exercise = db.ReferenceProperty(Exercise)
    playlist = db.ReferenceProperty(Playlist)

class ExerciseGraph(object):

    def __init__(self, user_data, user=users.get_current_user()):
#        addition_1 = Exercise(name="addition_1", covers=[], prerequisites=[], v_position = 1, h_position = 1)
#        addition_1.suggested = addition_1.proficient = False
#        self.exercises = [addition_1]
#        self.exercise_by_name = {"addition_1": addition_1}
#        return
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
            ex.suggested = None # Note set initially
            ex.assigned = False
            ex.streak = 0
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
                ex.streakwidth = min(200, 20 * ex.streak)

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

