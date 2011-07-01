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
from request_handler import RequestHandler

from models import UserData, CoachRequest, StudentList
from badges import util_badges

from profiles.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph
from profiles.util_profile import ClassProgressReportGraph, ClassEnergyPointsPerMinuteGraph, ClassTimeGraph
import profiles.util_profile as util_profile

import simplejson as json

class ViewCoaches(RequestHandler):
    def get(self):
        user = util.get_current_user()
        if user:
            invalid_coach = self.request_bool("invalid_coach", default = False)

            user_data = UserData.get_or_insert_for(user)
            coach_requests = CoachRequest.get_for_student(user).fetch(1000)

            template_values = {
                        "coaches": user_data.coaches,
                        "invalid_coach": invalid_coach,
                        "coach_requests": coach_requests,
                        "student_id": user.email(),
                        'selected_nav_link': 'coach'
                    }

            self.render_template('viewcoaches.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ViewStudents(RequestHandler):
    def get(self):
        user = util.get_current_user()
        if user:

            invalid_student = self.request_bool("invalid_student", default = False)

            user_data = UserData.get_or_insert_for(user)
            
            coach_requests = [x.student_requested.email() for x in CoachRequest.get_for_coach(user)]

            student_lists_models = StudentList.all().filter("coaches = ", user_data.key())
            
            student_lists_list = [];
            for student_list in student_lists_models:
                student_lists_list.append({
                    'key': str(student_list.key()),
                    'name': student_list.name,
                })
            student_lists_dict = dict((g['key'], g) for g in student_lists_list)
            
            students_data = user_data.get_students_data()
            students = map(lambda s: {
                'key': str(s.key()),
                'email': s.user.email(),
                'nickname': s.nickname,
                'student_lists': map(lambda id: student_lists_dict[str(id)], s.student_lists),
            }, students_data)
            students.sort(key=lambda s: s['nickname'])
            
            template_values = {
                "students": students,
                "students_json": json.dumps(students),
                "student_lists": student_lists_list,
                "student_lists_json": json.dumps(student_lists_list),
                "invalid_student": invalid_student,
                "coach_requests": coach_requests,
                "coach_requests_json": json.dumps(coach_requests),
                'selected_nav_link': 'coach'
            }
            self.render_template('viewstudentlists.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class RegisterCoach(RequestHandler):
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

                if not self.is_ajax_request():
                    self.redirect("/coaches")
                return
        
        if self.is_ajax_request():
            self.response.set_status(400)
        else:
            self.redirect("/coaches?invalid_coach=1")

class RequestStudent(RequestHandler):
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
                    if not self.is_ajax_request():
                        self.redirect("/students")
                    return

        if self.is_ajax_request():
            self.response.set_status(404)
        else:
            self.redirect("/students?invalid_student=1")

class AcceptCoach(RequestHandler):
    @RequestHandler.exceptions_to_http(400)
    def get(self):
        user = util.get_current_user()

        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)

        accept_coach = self.request_bool("accept", default = False)
        coach_email = self.request_string("coach_email")
        student_email = self.request_string('student_email')

        if bool(coach_email) == bool(student_email):
            raise Exception('must provide coach_email xor student_email')

        if coach_email:
            student = user
            user_data_student = user_data
            coach = users.User(coach_email)
            user_data_coach = UserData.get_for(coach)
        elif student_email:
            student = users.User(student_email)
            user_data_student = UserData.get_for(student)
            coach = user
            user_data_coach = user_data
        
        if user_data_coach and not user_data_student.is_coached_by(coach):
            coach_request = CoachRequest.get_for(coach, student)
            if coach_request:
                coach_request.delete()

                if user==student and accept_coach:
                    user_data_student.coaches.append(coach.email())
                    user_data_student.put()

        if not self.is_ajax_request():
            self.redirect("/coaches")

class UnregisterCoach(RequestHandler):
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

class UnregisterStudent(RequestHandler):
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

class CreateStudentList(RequestHandler):
    @RequestHandler.exceptions_to_http(400)
    def post(self):
        coach_data = util_profile.get_coach(self)
        
        list_name = self.request_string('list_name')
        if not list_name:
            raise Exception('Invalid list name')

        student_list = StudentList(coaches=[coach_data.key()], name=list_name)
        student_list.put()
        
        student_list_json = {
            'name': student_list.name,
            'key': str(student_list.key())
        }
        
        self.render_json(student_list_json)

class DeleteStudentList(RequestHandler):
    @RequestHandler.exceptions_to_http(400)
    def post(self):
        coach_data = util_profile.get_coach(self)
        student_list = util_profile.get_list(coach_data, self)
        student_list.delete()
        if not self.is_ajax_request():
            self.redirect_to('/students')

class AddStudentToList(RequestHandler):
    @RequestHandler.exceptions_to_http(400)
    def post(self):
        coach_data, student_data, student_list = util_profile.get_coach_student_and_student_list(self)
        
        student_data.student_lists.append(student_list.key())
        student_data.put()

class RemoveStudentFromList(RequestHandler):
    @RequestHandler.exceptions_to_http(400)
    def post(self):
        coach_data, student_data, student_list = util_profile.get_coach_student_and_student_list(self)
        
        student_data.student_lists.remove(student_list.key())
        student_data.put()

class ViewIndividualReport(RequestHandler):
    def get(self):
        # Individual reports being replaced by user profile
        self.redirect("/profile")

class ViewSharedPoints(RequestHandler):
    def get(self):
        self.redirect("/class_profile?selected_graph_type=%s" % ClassEnergyPointsPerMinuteGraph.GRAPH_TYPE)
        
class ViewProgressChart(RequestHandler):
    def get(self):    
        self.redirect("/profile?selected_graph_type=" + ExercisesOverTimeGraph.GRAPH_TYPE)
             
class ViewClassTime(RequestHandler):
    def get(self):
        self.redirect("/class_profile?selected_graph_type=%s" % ClassTimeGraph.GRAPH_TYPE)

class ViewClassReport(RequestHandler):
    def get(self):            
        self.redirect("/class_profile?selected_graph_type=%s" % ClassProgressReportGraph.GRAPH_TYPE)

class ViewCharts(RequestHandler):
    def get(self):
        self.redirect("/profile?selected_graph_type=%s&student_email=%s&exid=%s" % 
                (ExerciseProblemsGraph.GRAPH_TYPE, self.request_string("student_email"), self.request_string("exercise_name")))

