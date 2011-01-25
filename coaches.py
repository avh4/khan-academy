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
import util
import request_handler
import classtime

from models import UserExercise, Exercise, UserData, ProblemLog, VideoLog, ExerciseGraph
from badges import util_badges
from django.template.defaultfilters import escape

from profile.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph

def meanstdv(x):
    n, mean, std = len(x), 0, 0
    for a in x:
	mean = mean + a
    mean = mean / float(n)
    for a in x:
	std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std
    
    
class Class(db.Model):

    coach = db.StringProperty()
    blacklist = db.StringListProperty()

    def compute_stats(self, student_data, date):
        student = student_data.user
        key = self.coach + ":" + date.strftime('%Y-%m-%d')
        day_stats = DayStats.get_or_insert(key, class_ref=self, avg_modules_completed=1.0, standard_deviation=0.0) 
        student_stats = StudentStats.get_or_insert(key+":"+student.email(), day_stats=day_stats, student=student) 
            
        student_stats.modules_completed = len(student_data.all_proficient_exercises) + 1       
        student_stats.put()   
        modules_completed_list = []
        for student_stats in StudentStats.all().filter('day_stats =', day_stats):
           modules_completed_list.append(student_stats.modules_completed)
        if len(modules_completed_list) > 1:
            logging.info("modules_completed_list: " + str(modules_completed_list))
            day_stats.avg_modules_completed, day_stats.standard_deviation = meanstdv(modules_completed_list) 
            logging.info("day_stats.avg_modules_completed: " + str(day_stats.avg_modules_completed))
            logging.info("day_stats.standard_deviation: " + str(day_stats.standard_deviation)) 
            day_stats.put()
            
    def get_stats_for_period(self, joined_date, start_date, end_date):
        stats = []
        for day_stats in DayStats.all().filter('class_ref =', self).filter('date >=', start_date).filter('date <=', end_date):
            day_stats.days_until_proficient = (day_stats.date - joined_date.date()).days  
            stats.append(day_stats)
        return stats


class DayStats(db.Model):

    class_ref = db.ReferenceProperty(Class)
    date = db.DateProperty(auto_now_add = True)    
    avg_modules_completed = db.FloatProperty(default = 1.0)
    standard_deviation = db.FloatProperty(default = 0.0)

    
class StudentStats(db.Model):

    day_stats = db.ReferenceProperty(DayStats)    
    student = db.UserProperty()
    modules_completed = db.IntegerProperty(default = 0)
    
    
    
class ViewCoaches(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            user_data = UserData.get_or_insert_for(user)
            logout_url = users.create_logout_url(self.request.uri)

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'coaches': user_data.coaches
                }

            self.render_template('viewcoaches.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))
            
            
class RegisterCoach(request_handler.RequestHandler):
    
    def post(self):
        user = util.get_current_user()
        if user is None:
            self.redirect(util.create_login_url(self.request.uri))
            return

        user_data = UserData.get_or_insert_for(user)
        coach_email = self.request.get('coach').lower()            
        user_data.coaches.append(coach_email)
        user_data.put()
        self.redirect("/coaches")
            

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

        user = util.get_current_user()

        if user:

            logout_url = users.create_logout_url(self.request.uri)
            user_coach = user

            coach_email = self.request_string("coach")
            if len(coach_email) > 0:
                user_coach = users.User(email=coach_email)
                if user_coach:
                    user_data = UserData.get_or_insert_for(user_coach)

            if self.request_bool("update", default=False):
                points = 0
                if user_data:
                    students_data = user_data.get_students_data()
                    for student_data in students_data:
                        points += student_data.points
                json = simplejson.dumps({"points": points})
                self.response.out.write(json)
            else:
                template_values = {
                        'App' : App,
                        'username': user.nickname(),
                        'logout_url': logout_url,  
                        'user_coach': user_coach,
                        'coach_email': user_coach.email(),
                        }
                self.render_template('viewsharedpoints.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))  
        
class ViewProgressChart(request_handler.RequestHandler):
    def get(self):    
        self.redirect("/profile?selected_graph_type=" + ExercisesOverTimeGraph.GRAPH_TYPE)
            
class ViewStudents(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            user_data = UserData.get_or_insert_for(user)
            logout_url = users.create_logout_url(self.request.uri)
            
            student_emails = user_data.get_students()
            students = []
            for student_email in student_emails:   
                student = users.User(email=student_email)
                student_data = UserData.get_or_insert_for(student)
                student_data.user.name = util.get_nickname_for(student_data.user) 
                if student_email != student_data.user.name:
                   student_data.user.name += " (%s)" % student_email                                       
                students.append(student_data.user)

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'students': students,
                'coach_email': user_data.user.email(),
                }

            self.render_template('viewstudents.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))
        
class ViewClassTime(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)
            user_coach = user

            if users.is_current_user_admin():
                # Site administrators can view other coaches' data
                coach_email = self.request_string("coach")
                if len(coach_email) > 0:
                    user_coach = users.User(email=coach_email)

            coach_user_data = UserData.get_or_insert_for(user_coach)
            student_emails = coach_user_data.get_students()

            dt_ctz = self.request_date("dt", "%m/%d/%Y", default=datetime.datetime.min)

            classtime_table = None
            classtime_analyzer = classtime.ClassTimeAnalyzer(self.request_int("timezone_offset", default = -1))
            student_data = []

            if classtime_analyzer.timezone_offset != -1:
                # If no timezone offset is specified, don't bother grabbing all the data
                # because we'll be redirecting back to here w/ timezone information.
                classtime_table = classtime_analyzer.get_classtime_table(student_emails, dt_ctz)

            for student_email in student_emails:

                short_name = util.get_nickname_for(users.User(email=student_email))
                if len(short_name) > 18:
                    short_name = short_name[0:18] + "..."

                total_student_minutes = 0
                if classtime_table is not None:
                    total_student_minutes = classtime_table.get_student_total(student_email)

                student_data.append({
                    "name": short_name,
                    "total_minutes": "~%.0f" % total_student_minutes
                    })

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'classtime_table': classtime_table,
                'timezone_offset': classtime_analyzer.timezone_offset,
                'coach_email': user_coach.email(),
                'width': (80 * len(student_data)) + 150,
                'student_data': student_data,
                }
            self.render_template('viewclasstime.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ViewClassReport(request_handler.RequestHandler):
        
    def get(self):            
        user = util.get_current_user()
        if user:
            logout_url = users.create_logout_url(self.request.uri)   

            user_coach = user

            if users.is_current_user_admin():
                # Site administrators can view other coaches' data
                coach_email = self.request_string("coach")
                if len(coach_email) > 0:
                    user_coach = users.User(email=coach_email)

            coach_user_data = UserData.get_or_insert_for(user_coach)  
            students = coach_user_data.get_students()
            class_exercises = self.get_class_exercises(students)

            exercises_all = Exercise.get_all_use_cache()
            exercises_found = []

            for exercise in exercises_all:
                for student_email in students:
                    if class_exercises[student_email].has_key(exercise.name):
                        exercises_found.append(exercise)
                        break

            exercises_found_names = map(lambda exercise: exercise.name, exercises_found)
            exercise_data = {}

            for student_email in students:   

                student_data = class_exercises[student_email]["student_data"]
                if not student_data:
                    continue

                name = util.get_nickname_for(student_data.user)
                i = 0

                for exercise in exercises_found:

                    exercise_name = exercise.name
                    user_exercise = UserExercise()
                    if class_exercises[student_email].has_key(exercise_name):
                        user_exercise = class_exercises[student_email][exercise_name]

                    if not exercise_data.has_key(exercise_name):
                        exercise_data[exercise_name] = {}

                    link = "/profile/graph/exerciseproblems?student_email="+student_email+"&exercise_name="+exercise_name

                    status = ""
                    hover = ""
                    color = "transparent"

                    if student_data.is_proficient_at(exercise_name):
                        status = "Proficient"
                        color = "proficient"

                        if not student_data.is_explicitly_proficient_at(exercise_name):
                            status = "Proficient (due to proficiency in a more advanced module)"

                    elif user_exercise.exercise is not None and UserExercise.is_struggling_with(user_exercise, exercise):
                        status = "Struggling"
                        color = "struggling"
                    elif user_exercise.exercise is not None and user_exercise.total_done > 0:
                        status = "Started"
                        color = "started"

                    exercise_display = Exercise.to_display_name(exercise_name)
                    short_name = name
                    if len(short_name) > 18:
                        short_name = short_name[0:18] + "..."

                    if len(status) > 0:
                        hover = "<b>%s</b><br/><br/><b>%s</b><br/><em><nobr>Status: %s</nobr></em><br/><em>Streak: %s</em><br/><em>Problems attempted: %s</em>" % (escape(name), exercise_display, status, user_exercise.streak, user_exercise.total_done)

                    exercise_data[exercise_name][student_email] = {
                            "name": name, 
                            "short_name": short_name, 
                            "exercise_display": exercise_display, 
                            "link": link, 
                            "hover": hover,
                            "color": color
                            }
                    i += 1

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'exercise_names': exercises_found_names,
                'exercise_data': exercise_data,
                'coach_email': coach_user_data.user.email(),
                'students': students,
                }
            self.render_template('viewclassreport.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))
        
    def get_class_exercises(self, students):
            class_exercise_dict = {}
            for student_email in students:

                student = users.User(email=student_email)
                student_data = UserData.get_for(student)

                class_exercise_dict[student_email] = {"student_data": student_data}

                user_exercises = UserExercise.get_for_user_use_cache(student)
                for user_exercise in user_exercises:
                    if user_exercise.exercise not in class_exercise_dict[student_email]:
                        class_exercise_dict[student_email][user_exercise.exercise] = user_exercise

            return class_exercise_dict

class ViewCharts(request_handler.RequestHandler):
    def get(self):
        self.redirect("/profile?selected_graph_type=%s&student_email=%s&exid=%s" % 
                (ExerciseProblemsGraph.GRAPH_TYPE, self.request_string("student_email"), self.request_string("exercise_name")))

