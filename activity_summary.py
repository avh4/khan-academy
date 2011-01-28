import datetime
import logging

from mapreduce import control
from mapreduce import operation as op

import request_handler
import models
import consts
import points

class ActivitySummaryExerciseItem:
    def __init__(self):
        self.c_problems = 0
        self.c_correct = 0
        self.time_taken = 0
        self.points_earned = 0
        self.exercise = None

class ActivitySummaryVideoItem:
    def __init__(self):
        self.seconds_watched = 0
        self.points_earned = 0
        self.playlist_titles = None
        self.video_title = None

class ActivitySummary:

    def __init__(self):
        self.user = None
        self.date = None
        self.dict_exercises = {}
        self.dict_videos = {}

    def has_video_activity(self):
        return len(self.dict_videos) > 0

    def has_exercise_activity(self):
        return len(self.dict_exercises) > 0

    def has_activity(self):
        return self.has_video_activity() or self.has_exercise_activity()

    @staticmethod
    def build(user, date, problem_logs, video_logs):
        summary = ActivitySummary()
        summary.user = user
        # Chop off minutes and seconds
        summary.date = datetime.datetime(date.year, date.month, date.day, date.hour)

        date_next = date + datetime.timedelta(hours=1)
        
        problem_logs_filtered = filter(lambda problem_log: date <= problem_log.time_done < date_next, problem_logs)
        video_logs_filtered = filter(lambda video_log: date <= video_log.time_watched < date_next, video_logs)

        for problem_log in problem_logs_filtered:
            if not summary.dict_exercises.has_key(problem_log.exercise):
                summary.dict_exercises[problem_log.exercise] = ActivitySummaryExerciseItem()

            summary_item = summary.dict_exercises[problem_log.exercise]
            summary_item.time_taken += problem_log.time_taken_capped_for_reporting()
            summary_item.points_earned += problem_log.points_earned
            summary_item.c_problems += 1
            summary_item.exercise = problem_log.exercise
            if problem_log.correct:
                summary_item.c_correct += 1

        for video_log in video_logs_filtered:
            video_key = video_log.key_for_video()
            if not summary.dict_videos.has_key(video_key):
                summary.dict_videos[video_key] = ActivitySummaryVideoItem()

            summary_item = summary.dict_videos[video_key]
            summary_item.seconds_watched += video_log.seconds_watched
            summary_item.points_earned += video_log.points_earned
            summary_item.playlist_titles = video_log.playlist_titles
            summary_item.video_title = video_log.video_title

        return summary

def fill_realtime_recent_hourly_activity_summaries(hourly_activity_logs, user_data, dt_end):

    if user_data.last_hourly_summary and dt_end <= user_data.last_hourly_summary:
        return hourly_activity_logs

    # We're willing to fill the last 3 hours with realtime data if summary logs haven't
    # been compiled for some reason.
    dt_end = min(dt_end, datetime.datetime.now())
    dt_start = dt_end - datetime.timedelta(hours=3)

    if user_data.last_hourly_summary:
        dt_start = max(dt_end - datetime.timedelta(hours=3), user_data.last_hourly_summary)

    # Chop off minutes and seconds
    dt_start = datetime.datetime(dt_start.year, dt_start.month, dt_start.day, dt_start.hour)
    dt_end = datetime.datetime(dt_end.year, dt_end.month, dt_end.day, dt_end.hour)

    dt = dt_start

    problem_logs = models.ProblemLog.get_for_user_between_dts(user_data.user, dt_start, dt_end)
    video_logs = models.VideoLog.get_for_user_between_dts(user_data.user, dt_start, dt_end)

    while dt <= dt_end:
        summary = ActivitySummary.build(user_data.user, dt, problem_logs, video_logs)
        if summary.has_activity():
            log = models.HourlyActivityLog.build(user_data.user, dt, summary)
            hourly_activity_logs.append(log)
        dt += datetime.timedelta(hours=1)

    return hourly_activity_logs

def hourly_activity_summary_map(user_data):

    # Start summarizing after the last summary
    dt_start = user_data.last_hourly_summary or datetime.datetime.min

    # Stop summarizing at the last sign of activity
    dt_end = user_data.last_activity or datetime.datetime.now()

    # Never summarize the most recent hour
    # (it'll be summarized later, and we'll use the more detailed logs for this data)
    dt_end = min(dt_end, datetime.datetime.now() - datetime.timedelta(hours=1))

    # Never summarize more than 30 days into the past
    dt_start = max(dt_start, dt_end - datetime.timedelta(days=30))

    # Chop off minutes and seconds
    dt_start = datetime.datetime(dt_start.year, dt_start.month, dt_start.day, dt_start.hour)
    dt_end = datetime.datetime(dt_end.year, dt_end.month, dt_end.day, dt_end.hour)

    # If at least three hours have passed b/w last summary and latest activity
    if (dt_end - dt_start) > datetime.timedelta(hours=3):

        # Only iterate over 3 days per mapreduce
        dt_end = min(dt_end, dt_start + datetime.timedelta(days=3))

        dt = dt_start
        list_entities_to_put = []

        problem_logs = models.ProblemLog.get_for_user_between_dts(user_data.user, dt_start, dt_end)
        video_logs = models.VideoLog.get_for_user_between_dts(user_data.user, dt_start, dt_end)

        while dt <= dt_end:
            summary = ActivitySummary.build(user_data.user, dt, problem_logs, video_logs)
            if summary.has_activity():
                log = models.HourlyActivityLog.build(user_data.user, dt, summary)
                list_entities_to_put.append(log)

            dt += datetime.timedelta(hours=1)

        user_data.last_hourly_summary = dt_end

        yield op.db.Put(user_data)
        for entity in list_entities_to_put:
            yield op.db.Put(entity)

class StartNewHourlyActivityLogMapReduce(request_handler.RequestHandler):
    def get(self):
        # Admin-only restriction is handled by /admin/* URL pattern
        # so this can be called by a cron job.
        # Start a new Mapper task for calling statistics_update_map
        mapreduce_id = control.start_map(
                name = "HourlyActivityLog",
                handler_spec = "activity_summary.hourly_activity_summary_map",
                reader_spec = "mapreduce.input_readers.DatastoreInputReader",
                reader_parameters = {"entity_kind": "models.UserData"},
                shard_count = 20)
        self.response.out.write("OK: " + str(mapreduce_id))


