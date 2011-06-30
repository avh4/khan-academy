import datetime
import logging
import copy

from google.appengine.api import users
from asynctools import AsyncMultiTask, QueryTask

import util
from models import UserExercise, Exercise, UserData, ProblemLog, VideoLog, ExerciseGraph

class ClassTimeAnalyzer:

    def __init__(self, timezone_offset = 0, downtime_minutes = 30):
        self.timezone_offset = timezone_offset
        self.timezone_adjustment = datetime.timedelta(minutes = self.timezone_offset)

        # Number of downtime minutes considered to indicate a new 'chunk' of work
        self.chunk_delta = datetime.timedelta(minutes = downtime_minutes)

    def dt_to_utc(self, dt):
        return dt - self.timezone_adjustment

    def dt_to_ctz(self, dt):
        return dt + self.timezone_adjustment

    def get_classtime_table(self, students_data, dt_start_utc):

        dt_start_ctz = self.dt_to_ctz(dt_start_utc)
        dt_end_ctz = dt_start_ctz + datetime.timedelta(days = 1)

        column = 0

        classtime_table = ClassTimeTable(dt_start_ctz, dt_end_ctz)

        # Asynchronously grab all student data at once
        async_queries = []
        for user_data_student in students_data:

            query_problem_logs = ProblemLog.get_for_user_data_between_dts(user_data_student, self.dt_to_utc(dt_start_ctz), self.dt_to_utc(dt_end_ctz))
            query_video_logs = VideoLog.get_for_user_data_between_dts(user_data_student, self.dt_to_utc(dt_start_ctz), self.dt_to_utc(dt_end_ctz))

            async_queries.append(query_problem_logs)
            async_queries.append(query_video_logs)

        # Wait for all queries to finish
        results = util.async_queries(async_queries, limit=10000)

        for i, user_data_student in enumerate(students_data):

            problem_logs = results[i * 2].get_result()
            video_logs = results[i * 2 + 1].get_result()

            problem_and_video_logs = []

            for problem_log in problem_logs:
                problem_and_video_logs.append(problem_log)
            for video_log in video_logs:
                problem_and_video_logs.append(video_log)

            problem_and_video_logs = sorted(problem_and_video_logs, key=lambda log: log.time_started())

            chunk_current = None

            for activity in problem_and_video_logs:

                if chunk_current is not None and self.dt_to_ctz(activity.time_started()) > (chunk_current.end + self.chunk_delta):
                    classtime_table.drop_into_column(chunk_current, column)
                    chunk_current.description()
                    chunk_current = None

                if chunk_current is None:
                    chunk_current = ClassTimeChunk()
                    chunk_current.user_data_student = user_data_student
                    chunk_current.start = self.dt_to_ctz(activity.time_started())
                    chunk_current.end = self.dt_to_ctz(activity.time_ended())

                chunk_current.activities.append(activity)
                chunk_current.end = min(self.dt_to_ctz(activity.time_ended()), dt_end_ctz)

            if chunk_current is not None:
                classtime_table.drop_into_column(chunk_current, column)
                chunk_current.description()

            column += 1

        classtime_table.balance()
        return classtime_table
 
class ClassTimeTable:
    def __init__(self, dt_start_ctz, dt_end_ctz):
        self.rows = []
        self.height = 0
        self.student_totals = {}
        self.dt_start_ctz = dt_start_ctz
        self.dt_end_ctz = dt_end_ctz

    def update_student_total(self, chunk):
        if not self.student_totals.has_key(chunk.user_data_student.display_email()):
            self.student_totals[chunk.user_data_student.display_email()] = 0
        self.student_totals[chunk.user_data_student.display_email()] += chunk.minutes_spent()

    def get_student_total(self, student_email):
        if self.student_totals.has_key(student_email):
            return self.student_totals[student_email]
        return 0

    def dt_start_ctz_formatted(self):
        return self.dt_start_ctz.strftime("%m/%d/%Y")

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
        self.user_data_student = None
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

