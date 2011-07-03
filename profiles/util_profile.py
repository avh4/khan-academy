import datetime
import logging
import urllib

from django.utils import simplejson
from google.appengine.api import users

from profiles import templatetags
import request_handler
import util
import models
import consts
from badges import util_badges
from models import StudentList, UserData

import simplejson as json

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

class ViewClassProfile(request_handler.RequestHandler):
    @staticmethod
    def class_points(students):
        return reduce(lambda a,b: a + b, map(lambda s: s.points, students), 0)

    def get(self):

        user_data_coach = models.UserData.current()

        if user_data_coach:

            user_data_override = self.request_user_data("coach_email")
            if users.is_current_user_admin() and user_data_override:
                # Site administrators can look at any class profile
                user_data_coach = user_data_override

            students_data = user_data_coach.get_students_data()
            
            student_lists = StudentList.all().filter("coaches = ", user_data_coach.key())
            
            student_lists_list = [{
                'key': 'allstudents',
                'name': 'All students',
                'nstudents': len(students_data),
                'class_points': self.class_points(students_data)
            }];
            for student_list in student_lists:
                students = [s for s in students_data if student_list.key() in s.student_lists]
                student_lists_list.append({
                    'key': str(student_list.key()),
                    'name': student_list.name,
                    'nstudents': len(students),
                    'class_points': self.class_points(students)
                })
            
            list_id = self.request_string('list_id', 'allstudents')
            current_list = None
            for student_list in student_lists_list:
                if student_list['key'] == list_id:
                    current_list = student_list
            
            dict_students = map(lambda student_data: { 
                "email": student_data.email,
                "nickname": student_data.nickname,
            }, students_data)

            selected_graph_type = self.request_string("selected_graph_type") or ClassProgressReportGraph.GRAPH_TYPE
            initial_graph_url = "/profile/graph/%s?coach_email=%s&%s" % (selected_graph_type, urllib.quote(coach.email()), urllib.unquote(self.request_string("graph_query_params", default="")))
            if list_id:
                initial_graph_url += 'list_id=%s' % list_id
            
            template_values = {
                    'coach': coach,
                    'coach_email': coach.email(),
                    'list_id': list_id,
                    'student_list': current_list,
                    'student_lists': student_lists_list,
                    'student_lists_json': json.dumps(student_lists_list),
                    'coach_nickname': util.get_nickname_for(coach),
                    'selected_graph_type': selected_graph_type,
                    'initial_graph_url': initial_graph_url,
                    'exercises': models.Exercise.get_all_use_cache(),
                    'is_profile_empty': len(dict_students) <= 0,
                    'selected_nav_link': 'coach',
                    "view": self.request_string("view", default=""),
                    }
            self.render_template('viewclassprofile.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ViewProfile(request_handler.RequestHandler):

    def get(self):
        user_data_student = models.UserData.current()

        if user_data_student:

            user_data_override = self.request_user_data("student_email")
            if user_data_override and user_data_override.key_email != user_data_student.key_email:
                if (not users.is_current_user_admin()) and (not user_data_override.is_coached_by(user_data_student)):
                    # If current user isn't an admin or student's coach, they can't look at anything other than their own profile.
                    self.redirect("/profile")
                    return
                else:
                    # Allow access to this student's profile
                    user_data_student = user_data_override

            user_badges = util_badges.get_user_badges(user_data_student)

            selected_graph_type = self.request_string("selected_graph_type") or ActivityGraph.GRAPH_TYPE
            initial_graph_url = "/profile/graph/%s?student_email=%s&%s" % (selected_graph_type, urllib.quote(user_data_student.email), urllib.unquote(self.request_string("graph_query_params", default="")))
            tz_offset = self.request_int("tz_offset", default=0)

            template_values = {
                'student_nickname': user_data_student.nickname,
                'selected_graph_type': selected_graph_type,
                'initial_graph_url': initial_graph_url,
                'tz_offset': tz_offset,
                'student_points': user_data_student.points,
                'count_videos': models.Setting.count_videos(),
                'count_videos_completed': user_data_student.get_videos_completed(),
                'count_exercises': models.Exercise.get_count(),
                'count_exercises_proficient': len(user_data_student.all_proficient_exercises),
                'badge_collections': user_badges['badge_collections'],
                'user_badges_bronze': user_badges['bronze_badges'],
                'user_badges_silver': user_badges['silver_badges'],
                'user_badges_gold': user_badges['gold_badges'],
                'user_badges_platinum': user_badges['platinum_badges'],
                'user_badges_diamond': user_badges['diamond_badges'],
                'user_badges_master': user_badges['user_badges_master'],
                'user_badges': [user_badges['bronze_badges'], user_badges['silver_badges'], user_badges['gold_badges'], user_badges['platinum_badges'], user_badges['diamond_badges'],user_badges['user_badges_master']],
                'user_data_student': user_data_student,
                "show_badge_frequencies": self.request_bool("show_badge_frequencies", default=False),
                "view": self.request_string("view", default=""),
            }

            self.render_template('viewprofile.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ProfileGraph(request_handler.RequestHandler):

    def get(self):
        html = ""
        json_update = ""

        user_data_target = self.get_profile_target_user_data()
        if user_data_target:
            
            if self.redirect_if_not_ajax(user_data_target):
                return

            if self.request_bool("update", default=False):
                json_update = self.json_update(user_data_target)
            else:
                html_and_context = self.graph_html_and_context(user_data_target)

                if html_and_context["context"].has_key("is_graph_empty") and html_and_context["context"]["is_graph_empty"]:
                    # This graph is empty of activity. If it's a date-restricted graph, see if bumping out the time restrictions can help.
                    if self.redirect_for_more_data():
                        return

                html = html_and_context["html"]

        if len(json_update) > 0:
            self.response.out.write(json_update)
        else:
            json = simplejson.dumps({"html": html, "url": self.request.url}, ensure_ascii=False)
            self.response.out.write(json)

    def get_profile_target_user_data(self):
        user_data_student = models.UserData.current()

        if user_data_student:

            user_data_override = self.request_user_data("student_email")
            if user_data_override and user_data_override.key_email != user_data_student.key_email:
                if (not users.is_current_user_admin()) and (not user_data_override.is_coached_by(user_data_student)):
                    # If current user isn't an admin or student's coach, they can't look at anything other than their own profile.
                    user_data_student = None
                else:
                    # Allow access to this student's profile
                    user_data_student = user_data_override

        return user_data_student

    def redirect_if_not_ajax(self, user_data_student):
        if not self.is_ajax_request():
            # If it's not an ajax request, redirect to the appropriate /profile URL
            self.redirect("/profile?selected_graph_type=%s&student_email=%s&graph_query_params=%s" % 
                    (self.GRAPH_TYPE, urllib.quote(user_data_student.email), urllib.quote(urllib.quote(self.request.query_string))))
            return True
        return False

    def redirect_for_more_data(self):
        return False

    def json_update(self, user_data):
        return ""

class ClassProfileGraph(ProfileGraph):

    def get_profile_target_user_data(self):
        user_data_coach = models.UserData.current()

        if user_data_coach:
            user_data_override = self.request_user_data("coach_email")
            if users.is_current_user_admin() and user_data_override:
                # Site administrators can look at any class profile
                user_data_coach = user_data_override

        return user_data_coach

    def redirect_if_not_ajax(self, user_data_coach):
        if not self.is_ajax_request():
            # If it's not an ajax request, redirect to the appropriate /profile URL
            self.redirect("/class_profile?selected_graph_type=%s&coach_email=%s&graph_query_params=%s" % 
                    (self.GRAPH_TYPE, urllib.quote(user_data_coach.email), urllib.quote(urllib.quote(self.request.query_string))))
            return True
        return False
    
    def get_student_list(self, user_data_coach):
        list_id = self.request_string("list_id")
        if list_id and list_id != 'allstudents':
            return get_list(user_data_coach, self)
        else:
            return None

class ProfileDateToolsGraph(ProfileGraph):

    DATE_FORMAT = "%Y-%m-%d"

    @staticmethod
    def inclusive_start_date(dt):
        return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0) # Inclusive of start date

    @staticmethod
    def inclusive_end_date(dt):
        return datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 59) # Inclusive of end date

    def request_date_ctz(self, key):
        # Always work w/ client timezone dates on the client and UTC dates on the server
        dt = self.request_date(key, self.DATE_FORMAT, default=datetime.datetime.min)
        if dt == datetime.datetime.min:
            s_dt = self.request_string(key, default="")
            if s_dt == "today":
                dt = self.inclusive_start_date(self.utc_to_ctz(datetime.datetime.now()))
            elif s_dt == "yesterday":
                dt = self.inclusive_start_date(self.utc_to_ctz(datetime.datetime.now()) - datetime.timedelta(days=1))
            elif s_dt == "lastweek":
                dt = self.inclusive_start_date(self.utc_to_ctz(datetime.datetime.now()) - datetime.timedelta(days=6))
            elif s_dt == "lastmonth":
                dt = self.inclusive_start_date(self.utc_to_ctz(datetime.datetime.now()) - datetime.timedelta(days=29))
        return dt

    def tz_offset(self):
        return self.request_int("tz_offset", default=0)

    def ctz_to_utc(self, dt_ctz):
        return dt_ctz - datetime.timedelta(minutes=self.tz_offset())

    def utc_to_ctz(self, dt_utc):
        return dt_utc + datetime.timedelta(minutes=self.tz_offset())

class ClassProfileDateGraph(ClassProfileGraph, ProfileDateToolsGraph):

    DATE_FORMAT = "%m/%d/%Y"

    def get_date(self):
        dt_ctz = self.request_date_ctz("dt")

        if dt_ctz == datetime.datetime.min:
            # If no date, assume looking at today
            dt_ctz = self.utc_to_ctz(datetime.datetime.now())

        return self.ctz_to_utc(self.inclusive_start_date(dt_ctz))

class ProfileDateRangeGraph(ProfileDateToolsGraph):

    def get_start_date(self):
        dt_ctz = self.request_date_ctz("dt_start")

        if dt_ctz == datetime.datetime.min:
            # If no start date, assume looking at last 7 days
            dt_ctz = self.utc_to_ctz(datetime.datetime.now() - datetime.timedelta(days=6))

        return self.ctz_to_utc(self.inclusive_start_date(dt_ctz))

    def get_end_date(self):
        dt_ctz = self.request_date_ctz("dt_end")
        dt_start_ctz_test = self.request_date_ctz("dt_start")
        dt_start_ctz = self.utc_to_ctz(self.get_start_date())

        if (dt_ctz == datetime.datetime.min and dt_start_ctz_test == datetime.datetime.min):
            # If no end date or start date specified, assume looking at 7 days after start date
            dt_ctz = dt_start_ctz + datetime.timedelta(days=6)
        elif dt_ctz == datetime.datetime.min:
            # If start date specified but no end date, assume one day
            dt_ctz = dt_start_ctz

        if (dt_ctz - dt_start_ctz).days > consts.MAX_GRAPH_DAY_RANGE or dt_start_ctz > dt_ctz:
            # Maximum range of 30 days for now
            dt_ctz = dt_start_ctz + datetime.timedelta(days=consts.MAX_GRAPH_DAY_RANGE)

        return self.ctz_to_utc(self.inclusive_end_date(dt_ctz))

    def redirect_for_more_data(self):
        dt_start_ctz_test = self.request_date_ctz("dt_start")
        dt_end_ctz_test = self.request_date_ctz("dt_end")

        # If no dates were specified and activity was empty, try max day range instead of default 7.
        if dt_start_ctz_test == datetime.datetime.min and dt_end_ctz_test == datetime.datetime.min:
            self.redirect(self.request_url_with_additional_query_params("dt_start=lastmonth&dt_end=today&is_ajax_override=1")) 
            return True

        return False

class ActivityGraph(ProfileDateRangeGraph):
    GRAPH_TYPE = "activity"
    def graph_html_and_context(self, user_data_student):
        return templatetags.profile_activity_graph(user_data_student, self.get_start_date(), self.get_end_date(), self.tz_offset())

class FocusGraph(ProfileDateRangeGraph):
    GRAPH_TYPE = "focus"
    def graph_html_and_context(self, user_data_student):
        return templatetags.profile_focus_graph(user_data_student, self.get_start_date(), self.get_end_date())

class ExercisesOverTimeGraph(ProfileGraph):
    GRAPH_TYPE = "exercisesovertime"
    def graph_html_and_context(self, user_data_student):
        return templatetags.profile_exercises_over_time_graph(user_data_student)

class ExerciseProblemsGraph(ProfileGraph):
    GRAPH_TYPE = "exerciseproblems"
    def graph_html_and_context(self, user_data_student):
        return templatetags.profile_exercise_problems_graph(user_data_student, self.request_string("exercise_name"))

class ExerciseProgressGraph(ProfileGraph):
    GRAPH_TYPE = "exerciseprogress"
    def graph_html_and_context(self, user_data_student):
        return templatetags.profile_exercise_progress_graph(user_data_student)

class ClassExercisesOverTimeGraph(ClassProfileGraph):
    GRAPH_TYPE = "classexercisesovertime"
    def graph_html_and_context(self, user_data_coach):
        student_list = self.get_student_list(user_data_coach)
        return templatetags.class_profile_exercises_over_time_graph(user_data_coach, student_list)

class ClassProgressReportGraph(ClassProfileGraph):
    GRAPH_TYPE = "classprogressreport"
    def graph_html_and_context(self, user_data_coach):
        student_list = self.get_student_list(user_data_coach)
        return templatetags.class_profile_progress_report_graph(user_data_coach, student_list)

class ClassTimeGraph(ClassProfileDateGraph):
    GRAPH_TYPE = "classtime"
    def graph_html_and_context(self, user_data_coach):
        student_list = self.get_student_list(user_data_coach)
        return templatetags.class_profile_time_graph(user_data_coach, self.get_date(), self.tz_offset(), student_list)

class ClassEnergyPointsPerMinuteGraph(ClassProfileGraph):
    GRAPH_TYPE = "classenergypointsperminute"
    def graph_html_and_context(self, user_data_coach):
        student_list = self.get_student_list(user_data_coach)
        return templatetags.class_profile_energy_points_per_minute_graph(user_data_coach, student_list)

    def json_update(self, user_data_coach):
        student_list = self.get_student_list(user_data_coach)
        return templatetags.class_profile_energy_points_per_minute_update(user_data_coach, student_list)

