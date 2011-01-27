import datetime
import time
import logging

from django.template.defaultfilters import pluralize

import models
import util
import activity_summary

def get_playlist_focus_data(user, hourly_activity_logs, dt_start_utc, dt_end_utc):
    total_seconds = 0
    dict_playlist_seconds = {}

    for hourly_activity_log in hourly_activity_logs:

        activity_summary = hourly_activity_log.activity_summary
        for video_key in activity_summary.dict_videos.keys():
            activity_summary_video_item = activity_summary.dict_videos[video_key]

            playlist_title = "Other"
            if activity_summary_video_item.playlist_titles:
                playlist_title = activity_summary_video_item.playlist_titles[0] # Only count against the first playlist for now

            key_playlist = playlist_title.lower()
            if dict_playlist_seconds.has_key(key_playlist):
                dict_playlist_seconds[key_playlist]["seconds"] += activity_summary_video_item.seconds_watched
            else:
                dict_playlist_seconds[key_playlist] = {"playlist_title": playlist_title, "seconds": activity_summary_video_item.seconds_watched, "videos": {}}

            key_video = activity_summary_video_item.video_title.lower()
            if dict_playlist_seconds[key_playlist]["videos"].has_key(key_video):
                dict_playlist_seconds[key_playlist]["videos"][key_video]["seconds"] += activity_summary_video_item.seconds_watched
            else:
                dict_playlist_seconds[key_playlist]["videos"][key_video] = {"video_title": activity_summary_video_item.video_title, "seconds": activity_summary_video_item.seconds_watched}

            total_seconds += activity_summary_video_item.seconds_watched

    for key_playlist in dict_playlist_seconds:
        dict_playlist_seconds[key_playlist]["percentage"] = int(float(dict_playlist_seconds[key_playlist]["seconds"]) / float(total_seconds) * 100.0)
        dict_playlist_seconds[key_playlist]["time_spent"] = util.seconds_to_time_string(dict_playlist_seconds[key_playlist]["seconds"], False)

        for key_video in dict_playlist_seconds[key_playlist]["videos"]:
            dict_playlist_seconds[key_playlist]["videos"][key_video]["time_spent"] = util.seconds_to_time_string(dict_playlist_seconds[key_playlist]["videos"][key_video]["seconds"], False)

    return (total_seconds, dict_playlist_seconds)

def get_exercise_focus_data(user, user_data, hourly_activity_logs, dt_start_utc, dt_end_utc):

    total_seconds = 0
    dict_exercise_seconds = {}

    for hourly_activity_log in hourly_activity_logs:

        activity_summary = hourly_activity_log.activity_summary

        for exercise_key in activity_summary.dict_exercises.keys():
            activity_summary_exercise_item = activity_summary.dict_exercises[exercise_key]

            exid = activity_summary_exercise_item.exercise

            key_exercise = exid.lower()
            if not dict_exercise_seconds.has_key(key_exercise):
                dict_exercise_seconds[key_exercise] = {"exercise_title": models.Exercise.to_display_name(exid), "exid": exid, "seconds": 0, "correct": 0, "problems": 0}

            dict_exercise_seconds[key_exercise]["seconds"] += activity_summary_exercise_item.time_taken
            dict_exercise_seconds[key_exercise]["problems"] += activity_summary_exercise_item.c_problems
            dict_exercise_seconds[key_exercise]["correct"] += activity_summary_exercise_item.c_correct

            total_seconds += activity_summary_exercise_item.time_taken

    keys = dict_exercise_seconds.keys()
    for key_exercise in keys:
        percentage = int(float(dict_exercise_seconds[key_exercise]["seconds"]) / float(total_seconds) * 100.0)
        if percentage:
            dict_exercise_seconds[key_exercise]["percentage"] = percentage
            dict_exercise_seconds[key_exercise]["time_spent"] = util.seconds_to_time_string(dict_exercise_seconds[key_exercise]["seconds"], False)

            correct = dict_exercise_seconds[key_exercise]["correct"]
            dict_exercise_seconds[key_exercise]["s_correct_problems"] = "%d correct problem%s without a hint" % (correct, pluralize(correct))

            problems = dict_exercise_seconds[key_exercise]["problems"]
            dict_exercise_seconds[key_exercise]["s_problems"] = "%d total problem%s" % (problems, pluralize(problems))

            dict_exercise_seconds[key_exercise]["proficient"] = user_data.is_proficient_at(key_exercise, user)

        else:
            # Don't bother showing 0 percentage exercises
            del dict_exercise_seconds[key_exercise]

    return (total_seconds, dict_exercise_seconds)

def focus_graph_context(user_data_student, dt_start_utc, dt_end_utc):

    if not user_data_student:
        return {}

    user = user_data_student.user

    # Should never be more than (31*24)=744 activity logs per user
    hourly_activity_logs = models.HourlyActivityLog.get_for_user_between_dts(user, dt_start_utc, dt_end_utc).fetch(1000)
    hourly_activity_logs = activity_summary.fill_realtime_recent_hourly_activity_summaries(hourly_activity_logs, user_data_student, dt_end_utc)

    playlist_focus_data = get_playlist_focus_data(user, hourly_activity_logs, dt_start_utc, dt_end_utc)
    exercise_focus_data = get_exercise_focus_data(user, user_data_student, hourly_activity_logs, dt_start_utc, dt_end_utc)

    total_playlist_seconds = playlist_focus_data[0]
    dict_playlist_seconds = playlist_focus_data[1]

    total_exercise_seconds = exercise_focus_data[0]
    dict_exercise_seconds = exercise_focus_data[1]

    return {
            "student_email": user.email(),
            "total_playlist_seconds": total_playlist_seconds,
            "dict_playlist_seconds": dict_playlist_seconds,
            "total_exercise_seconds": total_exercise_seconds,
            "dict_exercise_seconds": dict_exercise_seconds,
            "is_graph_empty": (total_playlist_seconds + total_exercise_seconds <= 0),
            }


