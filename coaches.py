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

from models import UserData, CoachRequest, StudyGroup
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

            study_groups_models = StudyGroup.gql("WHERE coaches = :1", user_data.key())
            
            study_groups_list = [];
            for group in study_groups_models:
                study_groups_list.append({
                    'key': str(group.key()),
                    'name': group.name,
                })
            study_groups_dict = dict((g['key'], g) for g in study_groups_list)
            
            students_data = user_data.get_students_data()
            students = map(lambda s: {
                'key': str(s.key()),
                'email': s.user.email(),
                'nickname': s.nickname,
                'study_groups': map(lambda id: study_groups_dict[str(id)], s.studygroups),
            }, students_data)
            students.sort(key=lambda s: s['nickname'])
            
            template_values = {
                "students": students,
                "students_json": json.dumps(students),
                "study_groups": study_groups_list,
                "study_groups_json": json.dumps(study_groups_list),
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

class CreateGroup(request_handler.RequestHandler):
    def post(self):
        coach_data = get_coach(self)
        
        group_name = self.request_string('group_name')
        if not group_name:
            raise Exception('Invalid group name')

        study_group = StudyGroup(coaches=[coach_data.key()], name=group_name)
        study_group.put()
        
        study_group_json = {
            'name': study_group.name,
            'key': str(study_group.key())
        }
        
        self.render_json(study_group_json)

class DeleteGroup(request_handler.RequestHandler):
    def post(self):
        coach_data = get_coach(self)
        group = get_group(coach_data, self)
        group.delete()
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

def get_group(coach_data, request_handler):
    group_id = request_handler.request_string('group_id')
    group = StudyGroup.get(group_id)
    if group is None:
        raise Exception("No group found with group_id='%s'." % group_id)
    if coach_data.key() not in group.coaches:
        raise Exception("Not your group!")
    return group

def get_coach_student_and_group(request_handler):
    coach_data = get_coach(request_handler)
    group = get_group(coach_data, request_handler)
    student_data = get_student(coach_data, request_handler)
    return (coach_data, student_data, group)

class AddStudentToGroup(request_handler.RequestHandler):
    def post(self):
        coach_data, student_data, group = get_coach_student_and_group(self)
        
        student_data.studygroups.append(group.key())
        student_data.put()

class RemoveStudentFromGroup(request_handler.RequestHandler):
    def post(self):
        coach_data, student_data, group = get_coach_student_and_group(self)
        
        student_data.studygroups.remove(group.key())
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

