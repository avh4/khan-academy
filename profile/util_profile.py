import datetime
import logging
import urllib

from django.utils import simplejson
from google.appengine.api import users

from profile import templatetags
import request_handler
import util
import models
import consts
from badges import util_badges

class ViewProfile(request_handler.RequestHandler):

    def get(self):
        user = util.get_current_user()
        if user:
            student = user
            user_data_student = None

            student_email = self.request_string("student_email")
            if student_email and student_email != student.email():
                student_override = users.User(email=student_email)
                user_data_student = models.UserData.get_or_insert_for(student_override)
                if (not users.is_current_user_admin()) and user.email() not in user_data_student.coaches and user.email().lower() not in user_data_student.coaches:
                    # If current user isn't an admin or student's coach, they can't look at anything other than their own profile.
                    self.redirect("/profile")
                else:
                    # Allow access to this student's profile
                    student = student_override

            if not user_data_student:
                user_data_student = models.UserData.get_or_insert_for(student)

            user_badges = util_badges.get_user_badges(student)

            selected_graph_type = self.request_string("selected_graph_type") or ActivityGraph.GRAPH_TYPE
            initial_graph_url = "/profile/graph/%s?student_email=%s&%s" % (selected_graph_type, urllib.quote(student.email()), urllib.unquote(self.request_string("graph_query_params", default="")))
            tz_offset = self.request_int("tz_offset", default=0)

            template_values = {
                'student': student,
                'student_nickname': util.get_nickname_for(student),
                'selected_graph_type': selected_graph_type,
                'initial_graph_url': initial_graph_url,
                'tz_offset': tz_offset,
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
                "show_badge_frequencies": self.request_bool("show_badge_frequencies", default=False),
            }

            self.render_template('viewprofile.html', template_values)
        else:
            self.redirect(util.create_login_url(self.request.uri))

class ProfileGraph(request_handler.RequestHandler):
    def get(self):
        html = ""

        user = util.get_current_user()
        if user:
            student = user

            student_email = self.request_string("student_email")
            if student_email and student_email != student.email():
                student_override = users.User(email=student_email)
                user_data = models.UserData.get_or_insert_for(student_override)
                if (not users.is_current_user_admin()) and user.email() not in user_data.coaches and user.email().lower() not in user_data.coaches:
                    # If current user isn't an admin or student's coach, they can't look at anything other than their own profile.
                    self.redirect("/profile")
                else:
                    # Allow access to this student's profile
                    student = student_override

            if (not self.is_ajax_request()):
                # If it's not an ajax request, redirect to the appropriate /profile URL
                self.redirect("/profile?selected_graph_type=%s&student_email=%s&graph_query_params=%s" % 
                        (self.GRAPH_TYPE, urllib.quote(student.email()), urllib.quote(urllib.quote(self.request.query_string))))
                return

            html_and_context = self.graph_html_and_context(student)

            if html_and_context["context"].has_key("is_graph_empty") and html_and_context["context"]["is_graph_empty"]:
                # This graph is empty of activity. If it's a date-restricted graph, see if bumping out the time restrictions can help.
                if self.redirect_for_more_data():
                    return

            html = html_and_context["html"]

        json = simplejson.dumps({"html": html, "url": self.request.url}, ensure_ascii=False)
        self.response.out.write(json)

    def redirect_for_more_data(self):
        return False

class ProfileDateRangeGraph(ProfileGraph):

    DATE_FORMAT = "%Y-%m-%d"

    @staticmethod
    def inclusive_start_date(dt):
        return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0) # Inclusive of start date

    @staticmethod
    def inclusive_end_date(dt):
        return datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 59) # Inclusive of end date

    def request_date_ctz(self, key):
        # Always work w/ client timezone dates on the client and UTC dates on the server
        dt = self.request_date(key, ProfileDateRangeGraph.DATE_FORMAT, default=datetime.datetime.min)
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

    def get_start_date(self):
        dt_ctz = self.request_date_ctz("dt_start")

        if dt_ctz == datetime.datetime.min:
            # If no start date, assume looking at last 7 days
            dt_ctz = self.utc_to_ctz(datetime.datetime.now() - datetime.timedelta(days=6))

        return self.ctz_to_utc(ProfileDateRangeGraph.inclusive_start_date(dt_ctz))

    def get_end_date(self):
        dt_ctz = self.request_date_ctz("dt_end")
        dt_start_ctz_test = self.request_date_ctz("dt_start")
        dt_start_ctz = self.get_start_date()

        if (dt_ctz == datetime.datetime.min and dt_start_ctz_test == datetime.datetime.min):
            # If no end date or start date specified, assume looking at 7 days after start date
            dt_ctz = dt_start_ctz + datetime.timedelta(days=6)
        elif dt_ctz == datetime.datetime.min:
            # If start date specified but no end date, assume one day
            dt_ctz = dt_start_ctz

        if (dt_ctz - dt_start_ctz).days > consts.MAX_GRAPH_DAY_RANGE or dt_start_ctz > dt_ctz:
            # Maximum range of 30 days for now
            dt_ctz = dt_start_ctz + datetime.timedelta(days=consts.MAX_GRAPH_DAY_RANGE)

        return self.ctz_to_utc(ProfileDateRangeGraph.inclusive_end_date(dt_ctz))

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
    def graph_html_and_context(self, student):
        return templatetags.profile_activity_graph(student, self.get_start_date(), self.get_end_date(), self.tz_offset())

class FocusGraph(ProfileDateRangeGraph):
    GRAPH_TYPE = "focus"
    def graph_html_and_context(self, student):
        return templatetags.profile_focus_graph(student, self.get_start_date(), self.get_end_date())

class ExercisesOverTimeGraph(ProfileGraph):
    GRAPH_TYPE = "exercisesovertime"
    def graph_html_and_context(self, student):
        return templatetags.profile_exercises_over_time_graph(student)

class ExerciseProblemsGraph(ProfileGraph):
    GRAPH_TYPE = "exerciseproblems"
    def graph_html_and_context(self, student):
        return templatetags.profile_exercise_problems_graph(student, self.request_string("exercise_name"))

class ExerciseProgressGraph(ProfileGraph):
    GRAPH_TYPE = "exerciseprogress"
    def graph_html_and_context(self, student):
        return templatetags.profile_exercise_progress_graph(student)
