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

from models import UserExercise, Exercise, UserData, ProblemLog, VideoLog, ExerciseGraph
from badges import util_badges

from profiles.util_profile import ExercisesOverTimeGraph, ExerciseProblemsGraph
from profiles.util_profile import ClassProgressReportGraph, ClassEnergyPointsPerMinuteGraph

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

