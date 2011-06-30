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

from models import UserData, CoachRequest, StudentList
from badges import util_badges

from profiles.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph
from profiles.util_profile import ClassProgressReportGraph, ClassEnergyPointsPerMinuteGraph, ClassTimeGraph

import simplejson as json

class ViewCoaches(request_handler.RequestHandler):
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

class ViewStudents(request_handler.RequestHandler):
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
                'selected_nav_link': 'coach',
                'enable_tests': self.request_bool('enable_tests', default = False)
            }
            self.render_template('viewstudentlists.html', template_values)
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
        
        if self.is_ajax_request():
            raise Exception('todo: write something better')
        else:
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
                    if not self.is_ajax_request():
                        self.redirect("/students")
                    return

        if self.is_ajax_request():
            self.response.set_status(404)
        else:
            self.redirect("/students?invalid_student=1")

class AcceptCoach(request_handler.RequestHandler):
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

        if self.is_ajax_request():
            return
        else:
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

class CreateStudentList(request_handler.RequestHandler):
    def post(self):
        coach_data = get_coach(self)
        
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

class DeleteStudentList(request_handler.RequestHandler):
    def post(self):
        coach_data = get_coach(self)
        student_list = get_list(coach_data, self)
        student_list.delete()
        if not self.is_ajax_request():
            self.redirect_to('/students')
        
def get_coach(request_handler):
    coach = util.get_current_user()
    coach_data = UserData.get_or_insert_for(coach)
    return coach_data

def get_student(coach_data, request_handler):
    student_email = request_handler.request_string('student_email')
    student = users.User(student_email)
    student_data = UserData.get_for(student)
    if student_data is None:
        raise Exception("No student found with email='%s'." % student_email)
    if coach_data.user.email() not in student_data.coaches:
        raise Exception("Not your student!")
    return student_data

def get_list(coach_data, request_handler):
    list_id = request_handler.request_string('list_id')
    student_list = StudentList.get(list_id)
    if student_list is None:
        raise Exception("No list found with list_id='%s'." % list_id)
    if coach_data.key() not in student_list.coaches:
        raise Exception("Not your list!")
    return student_list

def get_coach_student_and_student_list(request_handler):
    coach_data = get_coach(request_handler)
    student_list = get_list(coach_data, request_handler)
    student_data = get_student(coach_data, request_handler)
    return (coach_data, student_data, student_list)

class AddStudentToList(request_handler.RequestHandler):
    def post(self):
        coach_data, student_data, student_list = get_coach_student_and_student_list(self)
        
        student_data.student_lists.append(student_list.key())
        student_data.put()

class RemoveStudentFromList(request_handler.RequestHandler):
    def post(self):
        coach_data, student_data, student_list = get_coach_student_and_student_list(self)
        
        student_data.student_lists.remove(student_list.key())
        student_data.put()

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

