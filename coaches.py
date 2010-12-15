import logging
import os
import datetime
import itertools
import copy
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
from django.template.defaultfilters import escape

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

            path = os.path.join(os.path.dirname(__file__), 'viewcoaches.html')
            self.response.out.write(template.render(path, template_values))
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
        user = util.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email and student_email != user.email():
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if (not users.is_current_user_admin()) and user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)                                   
            logout_url = users.create_logout_url(self.request.uri)   

            ex_graph = ExerciseGraph(user_data, user=student)
            proficient_exercises = ex_graph.get_proficient_exercises()
            self.compute_report(student, proficient_exercises, dummy_values=True)
            suggested_exercises = ex_graph.get_suggested_exercises()
            self.compute_report(student, suggested_exercises)
            review_exercises = ex_graph.get_review_exercises(self.get_time())
            self.compute_report(student, review_exercises)
            
            name = util.get_nickname_for(student)
            if student.email() != name:
                name = name + " (%s)" % student.email()
                   
            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'proficient_exercises': proficient_exercises,
                'suggested_exercises': suggested_exercises,
                'review_exercises': review_exercises,  
                'student': name,                
                'student_email': student_email,                  
                }

            path = os.path.join(os.path.dirname(__file__), 'viewindividualreport.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))

    def compute_report(self, user, exercises, dummy_values=False):
            for exercise in exercises:
                #logging.info(exercise.name)             
                if dummy_values:
                    exercise.percent_correct = "-"
                    exercise.percent_of_last_ten = "-"                    
                else:
                    total_correct = 0
                    correct_of_last_ten = 0
                    problems = ProblemLog.all().filter('user =', user).filter('exercise =', exercise.name).order("-time_done")
                    problem_num = 0
                    for problem in problems:
                        #logging.info("problem.time_done: " + str(problem.time_done) + " " + str(problem.correct))
                        if problem.correct:
                            total_correct += 1
                            if problem_num < 10:
                                correct_of_last_ten += 1
                        problem_num += 1
                    #logging.info("total_done: " + str(exercise.total_done))
                    #logging.info("total_correct: " + str(total_correct))
                    #logging.info("correct_of_last_ten: " + str(correct_of_last_ten))
                    if problem_num > 0:
                        exercise.percent_correct = "%.0f%%" % (100.0*total_correct/problem_num,)
                    else:
                        exercise.percent_correct = "0%"            
                    exercise.percent_of_last_ten = "%.0f%%" % (100.0*correct_of_last_ten/10,)
                
    def get_time(self):
        time_warp = int(self.request.get('time_warp') or '0')
        return datetime.datetime.now() + datetime.timedelta(days=time_warp)      
            
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
                path = os.path.join(os.path.dirname(__file__), 'viewsharedpoints.html')
                self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))  
        
class ViewProgressChart(request_handler.RequestHandler):

    def get(self):    
        class ExerciseData:
            def __init__(self, name, exid, days_until_proficient, proficient_date):
                self.name = name
                self.exid = exid
                self.days_until_proficient = days_until_proficient
                self.proficient_date = proficient_date

            def display_name(self):
                return Exercise.to_display_name(self.name)
                
        user = util.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email and student_email != user.email():
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if (not users.is_current_user_admin()) and user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)                  
            logout_url = users.create_logout_url(self.request.uri)   

            user_exercises = []
            init_days = None
            max_days = None
            num_exercises = 0
            start_date = None
            end_date = None
            #logging.info("user_data.joined: " + str(user_data.joined))
            for ue in UserExercise.all().filter('user =', user_data.user).filter('proficient_date >', None).order('proficient_date'):
                if num_exercises == 0:
                    init_days = (ue.proficient_date - user_data.joined).days  
                    start_date = ue.proficient_date
                days_until_proficient = (ue.proficient_date - user_data.joined).days   
                #logging.info(ue.exercise + ": " + str(ue.proficient_date))
                #logging.info("delta: " + str(ue.proficient_date - user_data.joined))
                proficient_date = ue.proficient_date.strftime('%m/%d/%Y')
                data = ExerciseData(ue.exercise, ue.exercise, days_until_proficient, proficient_date)
                user_exercises.append(data)
                max_days = days_until_proficient
                end_date = ue.proficient_date
                num_exercises += 1               
               
            #class_data = Class.get_or_insert(user.email(), coach=user.email()) 
            #stats = class_data.get_stats_for_period(user_data.joined, start_date, end_date)
            
            name = util.get_nickname_for(student)
            if student.email() != name:
                name = name + " (%s)" % student.email()
                   
            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,  
                'student': name,                
                'student_email': student_email,   
                'user_exercises': user_exercises,
                'init_days': init_days,
                'max_days': max_days,
                'num_exercises': num_exercises,
                #'stats': stats,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewprogresschart.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))  
            
            
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

            path = os.path.join(os.path.dirname(__file__), 'viewstudents.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))
        
class ClassTime:
    def __init__(self):
        self.rows = []
        self.height = 0
        self.student_totals = {}

    def update_student_total(self, chunk):
        if not self.student_totals.has_key(chunk.student.email()):
            self.student_totals[chunk.student.email()] = 0
        self.student_totals[chunk.student.email()] += chunk.minutes_spent()

    def get_student_total(self, student_email):
        if self.student_totals.has_key(student_email):
            return self.student_totals[student_email]
        return 0

    def today_formatted(self):
        return self.today.strftime("%m/%d/%Y")

    def drop_into_column(self, chunk, column):

        chunks_split = chunk.split_schoolday()
        if chunks_split is not None:
            for chunk_after_split in chunks_split:
                if chunk_after_split is not None:
                    self.drop_into_column(chunk_after_split, column)
            return

        ix = 0
        height = len(self.rows)
        while ix < height:
            if column >= len(self.rows[ix].chunks) or self.rows[ix].chunks[column] is None:
                break
            ix += 1

        if ix >= height:
            self.rows.append(ClassTimeRow())

        while len(self.rows[ix].chunks) <= column:
            self.rows[ix].chunks.append(None)

        self.rows[ix].chunks[column] = chunk

        self.update_student_total(chunk)

    def balance(self):
        width = 0
        height = len(self.rows)
        for ix in range(0, height):
            if len(self.rows[ix].chunks) > width:
                width = len(self.rows[ix].chunks)

        for ix in range(0, height):
            while len(self.rows[ix].chunks) < width:
                self.rows[ix].chunks.append(None)

class ClassTimeRow:
    def __init__(self):
        self.chunks = []

class ClassTimeChunk:

    SCHOOLDAY_START_HOURS = 8 # 8am
    SCHOOLDAY_END_HOURS = 15 # 3pm

    def __init__(self):
        self.student = None
        self.start = None
        self.end = None
        self.activities = []
        self.cached_activity_class = None

    def minutes_spent(self):
        return util.minutes_between(self.start, self.end)

    def activity_class(self):

        if self.cached_activity_class is not None:
            return self.cached_activity_class

        has_exercise = False
        has_video = False

        for activity in self.activities:
            has_exercise = has_exercise or type(activity) == ProblemLog
            has_video = has_video or type(activity) == VideoLog

        if has_exercise and has_video:
            self.cached_activity_class = "exercise_video"
        elif has_exercise:
            self.cached_activity_class = "exercise"
        elif has_video:
            self.cached_activity_class = "video"

        return self.cached_activity_class

    def schoolday_start(self):
        return datetime.datetime(
                year = self.start.year, 
                month = self.start.month, 
                day=self.start.day, 
                hour=ClassTimeChunk.SCHOOLDAY_START_HOURS)

    def schoolday_end(self):
        return datetime.datetime(
                year = self.start.year, 
                month = self.start.month, 
                day=self.start.day, 
                hour=ClassTimeChunk.SCHOOLDAY_END_HOURS)

    def during_schoolday(self):
        return self.start >= self.schoolday_start() and self.end <= self.schoolday_end()

    def split_schoolday(self):

        school_start = self.schoolday_start()
        school_end = self.schoolday_end()

        pre_schoolday = None
        schoolday = None
        post_schoolday = None

        if self.start < school_start and self.end > school_start:
            pre_schoolday = copy.copy(self)
            pre_schoolday.end = school_start

            schoolday = copy.copy(self)
            schoolday.start = school_start

        if self.start < school_end and self.end > school_end:
            post_schoolday = copy.copy(self)
            post_schoolday.start = school_end

            if schoolday is None:
                schoolday = copy.copy(self)
                schoolday.start = self.start

            schoolday.end = school_end

        if pre_schoolday is not None or schoolday is not None or post_schoolday is not None:
            return [pre_schoolday, schoolday, post_schoolday]

        return None

    def description(self):
        dict_videos = {}
        dict_exercises = {}

        for activity in self.activities:

            dict_target = None
            name_activity = None

            if type(activity) == ProblemLog:
                name_activity = activity.exercise
                dict_target = dict_exercises
            elif type(activity) == VideoLog:
                name_activity = activity.video_title
                dict_target = dict_videos

            if dict_target is not None:

                # For older data that doesn't have video titles recorded
                if name_activity is None:
                    name_activity = "Unknown"

                if not dict_target.has_key(name_activity):
                    dict_target[name_activity] = True

        desc_videos = ""
        for key in dict_videos:
            if len(desc_videos) > 0:
                desc_videos += "<br/>"
            desc_videos += " - <em>%s</em>" % key
        if len(desc_videos) > 0:
            desc_videos = "<br/><b>Videos:</b><br/>" + desc_videos

        desc_exercises = ""
        for key in dict_exercises:
            if len(desc_exercises) > 0:
                desc_exercises += "<br/>"
            desc_exercises += " - <em>%s</em>" % Exercise.to_display_name(key)
        if len(desc_exercises) > 0:
            desc_exercises = "<br/><b>Exercises:</b><br/>" + desc_exercises

        desc = ("<b>%s</b> - <b>%s</b><br/>(<em>~%.0f min.</em>)" % (self.start.strftime("%I:%M%p"), self.end.strftime("%I:%M%p"), self.minutes_spent())) + "<br/>" + desc_videos + desc_exercises

        return desc

class ViewClassTime(request_handler.RequestHandler):

    def __init__(self):
        self.timezone_offset = None
        self.timezone_adjustment = None

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

            if dt_ctz == datetime.datetime.min:
                dt = self.dt_to_ctz(datetime.datetime.now())
                dt_ctz = datetime.datetime(dt.year, dt.month, dt.day)

            classtime = None
            student_data = []

            if self.request_int("timezone_offset", default=-1) != -1:
                # If no timezone offset is specified, don't bother grabbing all the data
                # because we'll be redirecting back to here w/ timezone information.
                classtime = self.get_class_time_activity(student_emails, dt_ctz)

            for student_email in student_emails:

                short_name = util.get_nickname_for(users.User(email=student_email))
                if len(short_name) > 18:
                    short_name = short_name[0:18] + "..."

                total_student_minutes = 0
                if classtime is not None:
                    total_student_minutes = classtime.get_student_total(student_email)

                student_data.append({
                    "name": short_name,
                    "total_minutes": "~%.0f" % total_student_minutes
                    })

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'classtime': classtime,
                'timezone_offset': self.timezone_offset,
                'coach_email': user_coach.email(),
                'width': (80 * len(student_data)) + 150,
                'student_data': student_data,
                }
            path = os.path.join(os.path.dirname(__file__), 'viewclasstime.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))

    def prepare_tz_adjustment(self):
        if self.timezone_adjustment is None:
            self.timezone_offset = self.request_int("timezone_offset", default=0)
            self.timezone_adjustment = datetime.timedelta(minutes = self.timezone_offset)

    def dt_to_utc(self, dt):
        self.prepare_tz_adjustment()
        return dt - self.timezone_adjustment

    def dt_to_ctz(self, dt):
        self.prepare_tz_adjustment()
        return dt + self.timezone_adjustment

    def get_class_time_activity(self, student_emails, dt_ctz):

        column = 0

        classtime = ClassTime()

        classtime.today = dt_ctz
        tomorrow = classtime.today + datetime.timedelta(days = 1)

        for student_email in student_emails:
            student = users.User(email=student_email)

            problem_logs = ProblemLog.get_for_user_and_day(student, self.dt_to_utc(dt_ctz))
            video_logs = VideoLog.get_for_user_and_day(student, self.dt_to_utc(dt_ctz))

            problem_and_video_logs = []

            for problem_log in problem_logs:
                problem_and_video_logs.append(problem_log)
            for video_log in video_logs:
                problem_and_video_logs.append(video_log)

            problem_and_video_logs = sorted(problem_and_video_logs, key=lambda log: log.time_started())

            chunk_current = None
            chunk_delta = datetime.timedelta(minutes = 30) # 30 minutes of downtime = new chunk

            for activity in problem_and_video_logs:

                if chunk_current is not None and self.dt_to_ctz(activity.time_started()) > (chunk_current.end + chunk_delta):
                    classtime.drop_into_column(chunk_current, column)
                    chunk_current.description()
                    chunk_current = None

                if chunk_current is None:
                    chunk_current = ClassTimeChunk()
                    chunk_current.student = student
                    chunk_current.start = self.dt_to_ctz(activity.time_started())
                    chunk_current.end = self.dt_to_ctz(activity.time_ended())

                chunk_current.activities.append(activity)
                chunk_current.end = min(self.dt_to_ctz(activity.time_ended()), tomorrow)

            if chunk_current is not None:
                classtime.drop_into_column(chunk_current, column)
                chunk_current.description()

            column += 1

        classtime.balance()
        return classtime
        
class ViewClassReport(request_handler.RequestHandler):
        
    def get(self):
        class ReportCell:
            def __init__(self, data="", css_class="", link=""):
                self.data = data
                self.css_class = css_class
                self.link = link
            
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
                name = util.get_nickname_for(student_data.user)
                i = 0

                for exercise in exercises_found:

                    exercise_name = exercise.name
                    user_exercise = UserExercise()
                    if class_exercises[student_email].has_key(exercise_name):
                        user_exercise = class_exercises[student_email][exercise_name]

                    if not exercise_data.has_key(exercise_name):
                        exercise_data[exercise_name] = {}

                    link = "/charts?student_email="+student_email+"&exercise_name="+exercise_name

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
            path = os.path.join(os.path.dirname(__file__), 'viewclassreport.html')
            self.response.out.write(template.render(path, template_values))
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

    def moving_average(self, iterable, n=3):
        # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
        # http://en.wikipedia.org/wiki/Moving_average
        it = iter(iterable)
        d = deque(itertools.islice(it, n-1))
        d.appendleft(0)
        s = sum(d)
        for elem in it:
            s += elem - d.popleft()
            d.append(elem)
            yield s / float(n)    
                
    def get(self):
        class Problem:
            def __init__(self, time_taken, moving_average, correct):
                self.time_taken = time_taken
                self.moving_average = moving_average
                if correct:
                    self.correct = 1
                else:
                    self.correct = 0
        user = util.get_current_user()
        student = user
        if user:
            student_email = self.request.get('student_email')
            if student_email and student_email != user.email():
                #logging.info("user is a coach trying to look at data for student")
                student = users.User(email=student_email)
                user_data = UserData.get_or_insert_for(student)
                if (not users.is_current_user_admin()) and user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    raise Exception('Student '+ student_email + ' does not have you as their coach')
            else:
                #logging.info("user is a student looking at their own report")
                user_data = UserData.get_or_insert_for(user)   

            name = util.get_nickname_for(user_data.user)
            if user_data.user.email() != name:
                name = name + " (%s)" % user_data.user.email()
                
            logout_url = users.create_logout_url(self.request.uri)
            exercise_name = self.request.get('exercise_name')
            if not exercise_name:
                exercise_name = "addition_1"
              
            userExercise = user_data.get_or_insert_exercise(exercise_name)
            needs_proficient_date = False
            if user_data.is_proficient_at(exercise_name) and not userExercise.proficient_date:
                needs_proficient_date = True                 
        
            problem_list = []
            max_time_taken = 0  
            y_axis_interval = 1
            seconds_ranges = []
            problems = ProblemLog.all().filter('user =', student).filter('exercise =', exercise_name).order("time_done")            
            num_problems = problems.count()                           
            correct_in_a_row = 0
            proficient_date = None
            if num_problems > 2:          
                time_taken_list = []
                for problem in problems:  
                    time_taken_list.append(problem.time_taken)
                    if problem.time_taken > max_time_taken:
                        max_time_taken = problem.time_taken
                    problem_list.append(Problem(problem.time_taken_capped_for_reporting(), problem.time_taken_capped_for_reporting(), problem.correct))
                    #logging.info(str(problem.time_taken) + " " + str(problem.correct))  
                                        
                    if needs_proficient_date:
                        if problem.correct:
                            correct_in_a_row += 1
                        else:
                            correct_in_a_row = 0
                        if correct_in_a_row == 10:
                            proficient_date = problem.time_done
                    
                if needs_proficient_date and proficient_date:                    
                    userExercise.proficient_date = proficient_date 
                    userExercise.put()                        
                    
                if max_time_taken > 120:
                    max_time_taken = 120
                y_axis_interval = max_time_taken/5
                if y_axis_interval == 0:
                    y_axis_interval = max_time_taken/5.0            
                #logging.info("time_taken_list: " + str(time_taken_list))                                   
                #logging.info("max_time_taken: " + str(max_time_taken))
                #logging.info("y_axis_interval: " + str(y_axis_interval))

                averages = []   
                for average in self.moving_average(time_taken_list):
                    averages.append(int(average))
                #logging.info("averages: " + str(averages))
                for i in range(len(problem_list)):
                    problem = problem_list[i]
                    if i > 1:
                        problem.moving_average = averages[i-2]
                    #logging.info(str(problem.time_taken) + " " + str(problem.moving_average) + " " + str(problem.correct))                            

                range_size = self.get_range_size(num_problems, time_taken_list)
                #logging.info("range_size: " + str(range_size))  
                seconds_ranges = self.get_seconds_ranges(range_size)
                for problem in problem_list:
                    self.place_problem(problem, seconds_ranges)
                for seconds_range in seconds_ranges:
                    seconds_range.get_range_string(range_size)
                    seconds_range.get_percentages(num_problems)
                    #logging.info("seconds_range: " + str(seconds_range))  

            template_values = {
                'App' : App,
                'username': user.nickname(),
                'logout_url': logout_url,
                'exercise_name': Exercise.to_display_name(exercise_name),
                'exid': exercise_name,
                'problems': problem_list,
                'num_problems': num_problems,
                'max_time_taken': max_time_taken,
                'y_axis_interval': y_axis_interval,
                'student': name,
                'seconds_ranges': seconds_ranges,
                }

            path = os.path.join(os.path.dirname(__file__), 'viewcharts.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(util.create_login_url(self.request.uri))

    def get_range_size(self, num_problems, time_taken_list):
        range_size = 0
        pct_under_top_range = 0
        while pct_under_top_range < 0.8:
            range_size += 1
            #logging.info("range_size: " + str(range_size))
            #logging.info("range_size*10: " + str(range_size*10))
            num_under_top_range = 0
            for time_taken in time_taken_list:
                if time_taken < range_size*10:
                    num_under_top_range += 1
            #logging.info("num_under_top_range: " + str(num_under_top_range))
            pct_under_top_range = 1.0*num_under_top_range/num_problems
            #logging.info("pct_under_top_range: " + str(pct_under_top_range))
        return range_size
        
    def get_seconds_ranges(self, range_size):
        class SecondsRange:
            def __init__(self, lower_bound, upper_bound):
                self.lower_bound = lower_bound
                self.upper_bound = upper_bound
                self.num_correct = 0
                self.num_incorrect = 0
                self.pct_correct = 0
                self.pct_incorrect = 0
            def get_range_string(self, range_size):
                if self.upper_bound is None:
                    self.range_string = "%s+" % (self.lower_bound,)
                elif range_size == 1:
                    self.range_string = "%s" % (self.lower_bound,)                    
                else:
                    self.range_string = "%s-%s" % (self.lower_bound, self.upper_bound)
            def get_percentages(self, num_problems):
                self.pct_correct = 100.0*self.num_correct/num_problems
                self.pct_incorrect = 100.0*self.num_incorrect/num_problems                
            def __repr__(self):
                return self.range_string + " correct: " + str(self.pct_correct) + " incorrect: " + str(self.pct_incorrect)
                
        seconds_ranges = []
        for lower_bound in range(0, range_size*9, range_size): 
            seconds_ranges.append(SecondsRange(lower_bound, lower_bound+range_size-1))
        seconds_ranges.append(SecondsRange(range_size*9, None))
        return seconds_ranges

    def place_problem(self, problem, seconds_ranges):
        for seconds_range in seconds_ranges:
            if problem.time_taken >= seconds_range.lower_bound and \
                (seconds_range.upper_bound is None or problem.time_taken <= seconds_range.upper_bound):
                if problem.correct:
                    seconds_range.num_correct += 1
                else:
                    seconds_range.num_incorrect += 1    
