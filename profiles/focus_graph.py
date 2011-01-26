import datetime
import time
import logging

from django.template.defaultfilters import pluralize

import models
import util

def get_playlist_focus_data(user, dt_start_utc, dt_end_utc):
    total_seconds = 0
    dict_playlist_seconds = {}

    # We fetch all of the results here to avoid making tons of RPC calls.
    video_logs = models.VideoLog.get_for_user_between_dts(user, dt_start_utc, dt_end_utc).fetch(500000)

    for video_log in video_logs:

        playlist_title = "Other"
        if video_log.playlist_titles:
            playlist_title = video_log.playlist_titles[0] # Only count against the first playlist for now

        key_playlist = playlist_title.lower()
        if dict_playlist_seconds.has_key(key_playlist):
            dict_playlist_seconds[key_playlist]["seconds"] += video_log.seconds_watched
        else:
            dict_playlist_seconds[key_playlist] = {"playlist_title": playlist_title, "seconds": video_log.seconds_watched, "videos": {}}

        key_video = video_log.video_title.lower()
        if dict_playlist_seconds[key_playlist]["videos"].has_key(key_video):
            dict_playlist_seconds[key_playlist]["videos"][key_video]["seconds"] += video_log.seconds_watched
        else:
            dict_playlist_seconds[key_playlist]["videos"][key_video] = {"video_title": video_log.video_title, "seconds": video_log.seconds_watched}

        total_seconds += video_log.seconds_watched

    for key_playlist in dict_playlist_seconds:
        dict_playlist_seconds[key_playlist]["percentage"] = int(float(dict_playlist_seconds[key_playlist]["seconds"]) / float(total_seconds) * 100.0)
        dict_playlist_seconds[key_playlist]["time_spent"] = util.seconds_to_time_string(dict_playlist_seconds[key_playlist]["seconds"], False)

        for key_video in dict_playlist_seconds[key_playlist]["videos"]:
            dict_playlist_seconds[key_playlist]["videos"][key_video]["time_spent"] = util.seconds_to_time_string(dict_playlist_seconds[key_playlist]["videos"][key_video]["seconds"], False)

    return (total_seconds, dict_playlist_seconds)

def get_exercise_focus_data(user, dt_start_utc, dt_end_utc):

    total_seconds = 0
    dict_exercise_seconds = {}

    # We fetch all of the results here to avoid making tons of RPC calls.
    problem_logs = models.ProblemLog.get_for_user_between_dts(user, dt_start_utc, dt_end_utc).fetch(500000)

    for problem_log in problem_logs:

        exid = problem_log.exercise

        key_exercise = exid.lower()
        if not dict_exercise_seconds.has_key(key_exercise):
            dict_exercise_seconds[key_exercise] = {"exercise_title": models.Exercise.to_display_name(exid), "exid": exid, "seconds": 0, "correct": 0, "problems": 0}

        dict_exercise_seconds[key_exercise]["seconds"] += problem_log.time_taken_capped_for_reporting()
        dict_exercise_seconds[key_exercise]["problems"] += 1
        if problem_log.correct:
            dict_exercise_seconds[key_exercise]["correct"] += 1

        total_seconds += problem_log.time_taken_capped_for_reporting()

    user_data = models.UserData.get_for(user)

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

def focus_graph_context(user, dt_start_utc, dt_end_utc):

    if not user:
        return {}

    playlist_focus_data = get_playlist_focus_data(user, dt_start_utc, dt_end_utc)
    exercise_focus_data = get_exercise_focus_data(user, dt_start_utc, dt_end_utc)

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


