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
        user = util.get_current_user()
        if user:
            invalid_coach = self.request_bool("invalid_coach", default = False)

            user_data = UserData.get_or_insert_for(user)
            coach_requests = CoachRequest.get_for_student(user)

            template_values = {
                        "coaches": user_data.coaches,
                        "invalid_coach": invalid_coach,
                        "coach_requests": coach_requests,
                    }

            self.render_template('viewcoaches.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ViewStudents(request_handler.RequestHandler):
    def get(self):
        user = util.get_current_user()
        if user:

            invalid_student = self.request_bool("invalid_student", default = False)

            user_data = UserData.get_or_insert_for(user)
            student_emails = user_data.get_students()
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

class RequestStudent(request_handler.RequestHandler):
    def post(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        student_email = self.request_string("student_email")
        if student_email:
            student = users.User(student_email)
            user_data_student = UserData.get_for(student)
            if user_data_student and not user_data_student.is_coached_by(user):
                coach_request = CoachRequest.get_or_insert_for(user, student)
                if coach_request:
                    self.redirect("/students")
                    return

        self.redirect("/students?invalid_student=1")

class AcceptCoach(request_handler.RequestHandler):
    def get(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        accept_coach = self.request_bool("accept", default = False)
        user_data_student = UserData.get_or_insert_for(user)

        coach_email = self.request_string("coach_email")
        if coach_email:
            coach = users.User(coach_email)
            user_data_coach = UserData.get_for(coach)
            if user_data_coach and not user_data_student.is_coached_by(coach):
                coach_request = CoachRequest.get_for(coach, user)
                if coach_request:
                    coach_request.delete()

                    if accept_coach:
                        user_data_student.coaches.append(coach.email())
                        user_data_student.put()

        self.redirect("/coaches")

class UnregisterCoach(request_handler.RequestHandler):
    def get(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)
        coach_email = self.request.get('coach')

        if coach_email:
            try:
                user_data.coaches.remove(coach_email)
                user_data.coaches.remove(coach_email.lower())
            except ValueError:
                pass

            user_data.put()          

        self.redirect("/coaches") 

class UnregisterStudent(request_handler.RequestHandler):
    def get(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)
        student_email = self.request_string("student_email")

        if student_email:

            student = users.User(student_email)
            user_data_student = UserData.get_for(student)

            if user_data_student:

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

