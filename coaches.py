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

from models import UserData, CoachRequest
from badges import util_badges

from profiles.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph
from profiles.util_profile import ClassProgressReportGraph, ClassEnergyPointsPerMinuteGraph, ClassTimeGraph

class ViewCoaches(request_handler.RequestHandler):
    def get(self):
        user_data = UserData.current()
        user = user_data.user

        if user:
            invalid_coach = self.request_bool("invalid_coach", default = False)

            coach_requests = CoachRequest.get_for_student(user).fetch(1000)
            
            template_values = {
                        "coach_emails": user_data.coach_display_emails(),
                        "invalid_coach": invalid_coach,
                        "coach_requests": coach_requests,
                        "student_id": user_data.display_user.email(),
                    }

            self.render_template('viewcoaches.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ViewStudents(request_handler.RequestHandler):
    def get(self):
        user_data = UserData.current()
        user = user_data.user

        if user:

            invalid_student = self.request_bool("invalid_student", default = False)

            student_emails = user_data.student_display_emails()
            coach_requests = CoachRequest.get_for_coach(user)

            template_values = {
                        "student_emails": student_emails,
                        "invalid_student": invalid_student,
                        "coach_requests": coach_requests,
                    }
            self.render_template('viewstudents.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class RegisterCoach(request_handler.RequestHandler):
    def post(self):
        user_data = UserData.current()
        user = user_data.user

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data_coach = self.request_user_data("coach", default="")
        if user_data_coach and user_data_coach.user:

            coach = user_data_coach.user

            if not user_data.is_coached_by(coach):
                user_data.coaches.append(coach.email())
                user_data.put()

            self.redirect("/coaches")
            return

        self.redirect("/coaches?invalid_coach=1")

class RequestStudent(request_handler.RequestHandler):
    def post(self):
        user_data = UserData.current()
        user = user_data.user

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data_student = self.request_user_data("student_email")
        if user_data_student and user_data_student.user:

            student = user_data_student.user

            if not user_data_student.is_coached_by(user):
                coach_request = CoachRequest.get_or_insert_for(user, student)
                if coach_request:
                    self.redirect("/students")
                    return

        self.redirect("/students?invalid_student=1")

class AcceptCoach(request_handler.RequestHandler):
    def get(self):
        user_data_student = UserData.current()
        user = user_data_student.user

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        accept_coach = self.request_bool("accept", default = False)

        user_data_coach = self.request_user_data("coach")
        if user_data_coach and user_data_coach.user:

            coach = user_data_coach.user

            if not user_data_student.is_coached_by(coach):
                coach_request = CoachRequest.get_for(coach, user)
                if coach_request:
                    coach_request.delete()

                    if accept_coach:
                        user_data_student.coaches.append(coach.email())
                        user_data_student.put()

        self.redirect("/coaches")

class UnregisterCoach(request_handler.RequestHandler):
    def get(self):
        user_data = UserData.current()
        user = user_data.user

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data_coach = self.request_user_data("coach")
        if user_data_coach and user_data_coach.user:
            try:
                user_data.coaches.remove(user_data_coach.user.email())
                user_data.coaches.remove(user_data_coach.user.email().lower())
            except ValueError:
                pass

            user_data.put()          

        self.redirect("/coaches") 

class UnregisterStudent(request_handler.RequestHandler):
    def get(self):
        user_data = UserData.current()
        user = user_data.user

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data_student = self.request_user_data("student_email")
        if user_data_student and user_data_student.user:

            try:
                user_data_student.coaches.remove(user.email())
                user_data_student.coaches.remove(user.email().lower())
            except ValueError:
                pass

            user_data_student.put()

        self.redirect("/students")

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

