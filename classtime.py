import datetime
import logging
import copy

from google.appengine.api import users
from google.appengine.ext import deferred

from asynctools import AsyncMultiTask, QueryTask

import util
from models import UserExercise, Exercise, UserData, ProblemLog, VideoLog, LogSummary
import activity_summary


def dt_to_utc(dt, timezone_adjustment):
    return dt - timezone_adjustment

def dt_to_ctz(dt, timezone_adjustment):
    return dt + timezone_adjustment



#this function will make the summaries for the day
#as summaries should be being updated on a continuous basis going forward, it should only be called for days where no summaries yet exist
#it is not terribly efficient - will have to rely on 
def fill_summaries_from_logs(students_data, dt_start_utc, timezone_adjustment):
    logging.info("starting to fill summaries from logs")
    dt_start_ctz = dt_to_ctz(dt_start_utc, timezone_adjustment)
    dt_end_ctz = dt_start_ctz + datetime.timedelta(days = 1)
    
    # Asynchronously grab all student data at once
    async_queries = []
    for user_data_student in students_data:
        query_problem_logs = ProblemLog.get_for_user_data_between_dts(user_data_student, dt_to_utc(dt_start_ctz, timezone_adjustment), dt_to_utc(dt_end_ctz, timezone_adjustment))
        query_video_logs = VideoLog.get_for_user_data_between_dts(user_data_student, dt_to_utc(dt_start_ctz, timezone_adjustment), dt_to_utc(dt_end_ctz, timezone_adjustment))

        async_queries.append(query_problem_logs)
        async_queries.append(query_video_logs)

    # Wait for all queries to finish
    results = util.async_queries(async_queries, limit=10000)

    for i, user_data_student in enumerate(students_data):
        logging.info("working on student # "+str(user_data_student.user))

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
            LogSummary.add_or_update_entry(user_data_student, activity, ClassDailyActivitySummary)
    
    logging.info("finished filling summaries from logs")



class ClassTimeAnalyzer:

    def __init__(self, timezone_offset = 0, downtime_minutes = 30):
        self.tried_logs = False
        
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

        classtime_table = ClassTimeTable(dt_start_ctz, dt_end_ctz)        

        # Asynchronously grab all student data at once
        async_queries = []
        for user_data_student in students_data:
            query = LogSummary.get_for_user_data_between_dts(user_data_student, self.dt_to_utc(dt_start_ctz), self.dt_to_utc(dt_end_ctz))

            async_queries.append(query)

        # Wait for all queries to finish
        results = util.async_queries(async_queries, limit=10000)

        rows=0
        for i, user_data_student in enumerate(students_data):

            summaries=results[i].get_result()
            for summary in summaries:
                rows += 1
                summary.summary.setTimezoneOffset(self.timezone_offset)
                classtime_table.drop_into_column(summary.summary, i)                

        logging.info("new rows="+str(rows))


        # if there is no data, perhaps they are trying to get report from before there were summaries - try fetching the summaries and load old version
        if len(classtime_table.rows)<=0 and not self.tried_logs:
            for i, user_data_student in enumerate(students_data):
                logging.info("deferring updating for "+str(user_data_student.user))
                deferred.defer(fill_summaries_from_logs, [user_data_student], dt_start_utc, self.timezone_adjustment)
            return self.get_classtime_table_old(students_data, dt_start_utc)
            
        classtime_table.balance()
        return classtime_table
 

    def get_classtime_table_old(self, students_data, dt_start_utc):

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

        rows = 0
        chunks = 0
        for i, user_data_student in enumerate(students_data):

            problem_logs = results[i * 2].get_result()
            video_logs = results[i * 2 + 1].get_result()

            problem_and_video_logs = []

            for problem_log in problem_logs:
                problem_and_video_logs.append(problem_log)
            for video_log in video_logs:
                problem_and_video_logs.append(video_log)

            problem_and_video_logs = sorted(problem_and_video_logs, key=lambda log: log.time_started())
            rows+=len(problem_and_video_logs)
            
            chunk_current = None

            for activity in problem_and_video_logs:

                if chunk_current is not None and self.dt_to_ctz(activity.time_started()) > (chunk_current.end + self.chunk_delta):
                    chunks += 1
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
                chunks += 1
                classtime_table.drop_into_column(chunk_current, column)
                chunk_current.description()

            column += 1

        logging.info("old rows="+str(rows)+", old chunks="+str(chunks))
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
        if not self.student_totals.has_key(chunk.user_data_student.email):
            self.student_totals[chunk.user_data_student.email] = 0
        self.student_totals[chunk.user_data_student.email] += chunk.minutes_spent()

    def get_student_total(self, student_email):
        if self.student_totals.has_key(student_email):
            return self.student_totals[student_email]
        return 0

    def dt_start_ctz_formatted(self):
        return self.dt_start_ctz.strftime("%m/%d/%Y")

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

    def drop_into_column(self, chunk, column):
        #not splitting up summary like old drop_into_column as it does not contain the individual logs
        
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

    def drop_into_column2(self, chunk, column):

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

class ClassDailyActivitySummary:
    SCHOOLDAY_START_HOURS = 8 # 8am
    SCHOOLDAY_END_HOURS = 15 # 3pm

    def __init__(self):
        self.user_data_student = None
        self.start = None
        self.end = None
        self.dict_videos = {}
        self.dict_exercises = {}
        self.activity_class = None

    def setTimezoneOffset(self, offset):
        adjustment = datetime.timedelta(minutes = offset)
        self.start = self.start + adjustment
        self.end = self.end + adjustment

    def minutes_spent(self):
        return util.minutes_between(self.start, self.end)

    def activity_class(self):
        return self.activity_class

    #updates the activity class based upon the new activity
    def update_activity_class(self, activity):
        if self.activity_class is None:
            if type(activity) == ProblemLog:
                self.activity_class = "exercise"
            elif type(activity) == VideoLog:
                self.activity_class = "video"
            elif (self.activity_class == "exercise" and type(activity) == VideoLog) or (self.activity_class == "video" and type(activity) == ProblemLog): 
                self.activity_class = "exercise_video"
        return self.activity_class

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

    #redefining chunk as being within a schoolday if any part of it is within the school day
    def during_schoolday(self):
        return (self.start >= self.schoolday_start() and self.start <= self.schoolday_end()) or (self.end >= self.schoolday_start() and self.end <= self.schoolday_end())  

    def add(self, user, activity):
        self.user_data_student = activity.user
        self.start = min(self.start, activity.time_started()) if self.start is not None else activity.time_started()
        self.end   = max(self.end, activity.time_ended()) if self.end is not None else activity.time_ended()

        dict_target = None
        name_activity = None

        if type(activity) == ProblemLog:
            name_activity = activity.exercise
            dict_target = self.dict_exercises
        elif type(activity) == VideoLog:
            name_activity = activity.video_title
            dict_target = self.dict_videos

        if dict_target is not None:
            # For older data that doesn't have video titles recorded
            if name_activity is None:
                name_activity = "Unknown"

            if not dict_target.has_key(name_activity):
                dict_target[name_activity] = True

        self.update_activity_class(activity)

    def description(self):
        desc_videos = ""
        for key in self.dict_videos:
            if len(desc_videos) > 0:
                desc_videos += "<br/>"
            desc_videos += " - <em>%s</em>" % key
        if len(desc_videos) > 0:
            desc_videos = "<br/><b>Videos:</b><br/>" + desc_videos

        desc_exercises = ""
        for key in self.dict_exercises:
            if len(desc_exercises) > 0:
                desc_exercises += "<br/>"
            desc_exercises += " - <em>%s</em>" % Exercise.to_display_name(key)
        if len(desc_exercises) > 0:
            desc_exercises = "<br/><b>Exercises:</b><br/>" + desc_exercises
 
        desc = ("<b>%s</b> - <b>%s</b><br/>(<em>~%.0f min.</em>)" % (self.start.strftime("%I:%M%p"), self.end.strftime("%I:%M%p"), self.minutes_spent())) + "<br/>" + desc_videos + desc_exercises

        return desc


