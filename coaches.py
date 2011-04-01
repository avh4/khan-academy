import logging
import os
import datetime
import itertools
from collections import deque
from pprint import pformat
from math import sqrt, ceil
    
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from django.utils import simplejson

from app import App
import app
import facebook_util
import util
import request_handler

from models import UserExercise, Exercise, UserData, ProblemLog, VideoLog, ExerciseGraph
from badges import util_badges

from profiles.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph
from profiles.util_profile import ClassProgressReportGraph, ClassEnergyPointsPerMinuteGraph, ClassTimeGraph

class ViewCoaches(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            user_data = UserData.get_or_insert_for(user)
            invalid_coach = self.request_bool("invalid_coach", default = False)

            self.render_template('viewcoaches.html', { 'coaches': user_data.coaches, 'invalid_coach': invalid_coach })
        else:
            self.redirect(util.create_login_url(self.request.uri))
            
class RegisterCoach(request_handler.RequestHandler):
    
    def post(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)

        coach_email = self.request_string("coach", default="")
        if coach_email:
            coach_user = users.User(coach_email)
            coach_user_data = UserData.get_for(coach_user)

            if coach_user_data:

                if coach_email not in user_data.coaches and coach_email.lower() not in user_data.coaches:
                    user_data.coaches.append(coach_email)
                    user_data.put()

                self.redirect("/coaches")
                return

        self.redirect("/coaches?invalid_coach=1")

class UnregisterCoach(request_handler.RequestHandler):

    def post(self):
        user = util.get_current_user()
        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return
        user_data = UserData.get_or_insert_for(user)
        coach_email = self.request.get('coach')
        if coach_email:
            if coach_email in user_data.coaches:
                user_data.coaches.remove(coach_email)
                user_data.put()
            elif coach_email.lower() in user_data.coaches:
                user_data.coaches.remove(coach_email.lower())
                user_data.put()          
        self.redirect("/coaches") 

class ViewIndividualReport(request_handler.RequestHandler):
    def get(self):
        # Individual reports being replaced by user profile
        self.redirect("/profile")

class ViewSharedPoints(request_handler.RequestHandler):
    def get(self):
        self.redirect("/class_profile?selected_graph_type=%s" % ClassEnergyPointsPerMinuteGraph.GRAPH_TYPE)
        
class ViewProgressChart(request_handler.RequestHandler):
    def get(self):    
        self.redirect("/profile?selected_graph_type=" + ExercisesOverTimeGraph.GRAPH_TYPE)
            
class ViewStudents(request_handler.RequestHandler):
    def get(self):
        self.redirect("/class_profile")
       
class ViewClassTime(request_handler.RequestHandler):
    def get(self):
        self.redirect("/class_profile?selected_graph_type=%s" % ClassTimeGraph.GRAPH_TYPE)

class ViewClassReport(request_handler.RequestHandler):
    def get(self):            
        self.redirect("/class_profile?selected_graph_type=%s" % ClassProgressReportGraph.GRAPH_TYPE)

class ViewCharts(request_handler.RequestHandler):
    def get(self):
        self.redirect("/profile?selected_graph_type=%s&student_email=%s&exid=%s" % 
                (ExerciseProblemsGraph.GRAPH_TYPE, self.request_string("student_email"), self.request_string("exercise_name")))

