import datetime
import time
import logging

from django.template.defaultfilters import pluralize

import models
import util
from badges import models_badges, util_badges

class ActivityBucketType:
    HOUR = 0
    DAY = 1
    
def get_bucket_type(dt_start_utc, dt_end_utc):
    if (dt_end_utc - dt_start_utc).days > 1:
        return ActivityBucketType.DAY
    else:
        return ActivityBucketType.HOUR

def get_bucket_timedelta(bucket_type):
    if bucket_type == ActivityBucketType.DAY:
        return datetime.timedelta(days = 1)
    else:
        return datetime.timedelta(minutes = 60)

def get_bucket_value(dt_utc, tz_offset, bucket_type):
    dt_ctz = dt_utc + datetime.timedelta(minutes=tz_offset)

    if bucket_type == ActivityBucketType.DAY:
        return datetime.date(dt_ctz.year, dt_ctz.month, dt_ctz.day)
    else:
        return datetime.datetime(dt_ctz.year, dt_ctz.month, dt_ctz.day, dt_ctz.hour).strftime("%I:%M %p")

def get_empty_dict_bucket(bucket_list):
    dict_bucket = {}
    for bucket in bucket_list:
        dict_bucket[bucket] = None
    return dict_bucket

def get_bucket_list(dt_start_utc, dt_end_utc, tz_offset, bucket_type):

    bucket_list = []

    dt = dt_start_utc
    dt_last = dt

    while (dt < dt_end_utc):
        bucket_list.append(get_bucket_value(dt, tz_offset, bucket_type))
        dt_last = dt
        dt += get_bucket_timedelta(bucket_type)

    if get_bucket_value(dt_end_utc, tz_offset, bucket_type) != get_bucket_value(dt_last, tz_offset, bucket_type):
        # Make sure we always have the last bucket
        bucket_list.append(get_bucket_value(dt_end_utc, tz_offset, bucket_type))

    return bucket_list

def add_bucket_html_summary(dict_bucket, key, limit):
    for bucket in dict_bucket:
        if dict_bucket[bucket]:
            dict_entries = dict_bucket[bucket][key]
            list_entries = []
            c = 0
            for entry in dict_entries:
                if c >= limit:
                    list_entries.append("<em>...and %d more</em>" % (len(dict_entries) - limit))
                    break
                list_entries.append(entry)
                c += 1
            dict_bucket[bucket]["html_summary"] = "<br/>".join(list_entries)

def get_exercise_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset):

    dict_bucket = get_empty_dict_bucket(bucket_list)
    problem_logs = models.ProblemLog.get_for_user_between_dts(user, dt_start_utc, dt_end_utc)

    for problem_log in problem_logs:
        key = get_bucket_value(problem_log.time_done, tz_offset, bucket_type)

        if not dict_bucket.has_key(key):
            continue;

        if not dict_bucket[key]:
            dict_bucket[key] = {"minutes": 0, "seconds": 0, "points": 0, "exercise_names": {}}

        dict_bucket[key]["minutes"] += problem_log.minutes_spent()
        dict_bucket[key]["seconds"] += problem_log.time_taken_capped_for_reporting()
        dict_bucket[key]["points"] += problem_log.points_earned
        dict_bucket[key]["exercise_names"][models.Exercise.to_display_name(problem_log.exercise)] = True

    for bucket in bucket_list:
        if dict_bucket[bucket]:
            dict_bucket[bucket]["time_spent"] = util.seconds_to_time_string(dict_bucket[bucket]["seconds"], False)

    add_bucket_html_summary(dict_bucket, "exercise_names", 5)

    return dict_bucket

def get_playlist_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset):

    dict_bucket = get_empty_dict_bucket(bucket_list)
    video_logs = models.VideoLog.get_for_user_between_dts(user, dt_start_utc, dt_end_utc)

    for video_log in video_logs:
        key = get_bucket_value(video_log.time_watched, tz_offset, bucket_type)

        if not dict_bucket.has_key(key):
            continue;

        if not dict_bucket[key]:
            dict_bucket[key] = {"minutes": 0, "seconds": 0, "points": 0, "video_titles": {}}

        dict_bucket[key]["minutes"] += video_log.minutes_spent()
        dict_bucket[key]["seconds"] += video_log.seconds_watched
        dict_bucket[key]["points"] += video_log.points_earned
        dict_bucket[key]["video_titles"][video_log.video_title] = True

    for bucket in bucket_list:
        if dict_bucket[bucket]:
            dict_bucket[bucket]["time_spent"] = util.seconds_to_time_string(dict_bucket[bucket]["seconds"], False)

    add_bucket_html_summary(dict_bucket, "video_titles", 5)

    return dict_bucket

def get_badge_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset):

    dict_bucket = get_empty_dict_bucket(bucket_list)
    user_badges = models_badges.UserBadge.get_for_user_between_dts(user, dt_start_utc, dt_end_utc)
    badges_dict = util_badges.all_badges_dict()

    for user_badge in user_badges:
        key = get_bucket_value(user_badge.date, tz_offset, bucket_type)

        badge = badges_dict.get(user_badge.badge_name)
        if not badge:
            continue

        if not dict_bucket.has_key(key):
            continue;

        if not dict_bucket[key]:
            dict_bucket[key] = {"points": 0, "badge_category": -1, "badge_url": "", "badge_descriptions": {}}

        dict_bucket[key]["points"] += user_badge.points_earned
        dict_bucket[key]["badge_descriptions"][badge.description] = True

        if badge.badge_category > dict_bucket[key]["badge_category"]:
            dict_bucket[key]["badge_url"] = badge.chart_icon_src()
            dict_bucket[key]["badge_category"] = badge.badge_category

    add_bucket_html_summary(dict_bucket, "badge_descriptions", 3)

    return dict_bucket

def get_proficiency_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset):

    dict_bucket = get_empty_dict_bucket(bucket_list)
    user_exercises = models.UserExercise.get_for_user_use_cache(user)

    for user_exercise in user_exercises:

        if not user_exercise.proficient_date:
            continue

        if user_exercise.proficient_date < dt_start_utc or user_exercise.proficient_date > dt_end_utc:
            continue

        key = get_bucket_value(user_exercise.proficient_date, tz_offset, bucket_type)

        if not dict_bucket.has_key(key):
            continue;

        if not dict_bucket[key]:
            dict_bucket[key] = {"exercise_names": {}}

        dict_bucket[key]["exercise_names"][models.Exercise.to_display_name(user_exercise.exercise)] = True

    add_bucket_html_summary(dict_bucket, "exercise_names", 3)

    return dict_bucket

def get_points_activity_data(bucket_list, dict_playlist_buckets, dict_exercise_buckets, dict_badge_buckets):
    dict_bucket = get_empty_dict_bucket(bucket_list)

    for bucket in bucket_list:
        dict_bucket[bucket] = 0
        if dict_playlist_buckets[bucket]:
            dict_bucket[bucket] += dict_playlist_buckets[bucket]["points"]
        if dict_exercise_buckets[bucket]:
            dict_bucket[bucket] += dict_exercise_buckets[bucket]["points"]
        if dict_badge_buckets[bucket]:
            dict_bucket[bucket] += dict_badge_buckets[bucket]["points"]

    return dict_bucket

def map_scatter_y_values(dict_target, dict_exercise_buckets, dict_playlist_buckets):
    # Icon's y coordinate is set just above the highest playlist/exercise time spent
    for key in dict_target:
        if dict_target[key]:
            bucket_minutes_playlist = dict_playlist_buckets[key]["minutes"] if dict_playlist_buckets[key] else 0
            bucket_minutes_exercise= dict_exercise_buckets[key]["minutes"] if dict_exercise_buckets[key] else 0
            dict_target[key]["y"] = bucket_minutes_playlist + bucket_minutes_exercise

def has_activity_type(dict_target, bucket, key_activity):
    return dict_target[bucket] and dict_target[bucket][key_activity]

def activity_graph_context(user, dt_start_utc, dt_end_utc, tz_offset):

    if not user:
        return {}

    bucket_type = get_bucket_type(dt_start_utc, dt_end_utc)
    bucket_list = get_bucket_list(dt_start_utc, dt_end_utc, tz_offset, bucket_type)

    dict_playlist_buckets = get_playlist_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset)
    dict_exercise_buckets = get_exercise_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset)
    dict_badge_buckets = get_badge_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset)
    dict_proficiency_buckets = get_proficiency_activity_data(user, bucket_list, bucket_type, dt_start_utc, dt_end_utc, tz_offset)
    dict_points_buckets = get_points_activity_data(bucket_list, dict_playlist_buckets, dict_exercise_buckets, dict_badge_buckets)

    map_scatter_y_values(dict_badge_buckets, dict_playlist_buckets, dict_exercise_buckets)
    map_scatter_y_values(dict_proficiency_buckets, dict_playlist_buckets, dict_exercise_buckets)

    has_activity = False
    for bucket in bucket_list:
        if (has_activity_type(dict_playlist_buckets, bucket, "minutes") or
            has_activity_type(dict_exercise_buckets, bucket, "minutes") or
            has_activity_type(dict_badge_buckets, bucket, "badge_category") or
            has_activity_type(dict_points_buckets, bucket, "points")):
                has_activity = True
                break

    graph_title = ""
    if bucket_type == ActivityBucketType.HOUR:
        graph_title = str(get_bucket_value(dt_start_utc, tz_offset, ActivityBucketType.DAY))

    return {
            "is_graph_empty": not has_activity,
            "bucket_list": bucket_list,
            "enable_drill_down": (bucket_type != ActivityBucketType.HOUR),
            "dict_playlist_buckets": dict_playlist_buckets,
            "dict_exercise_buckets": dict_exercise_buckets,
            "dict_badge_buckets": dict_badge_buckets,
            "dict_proficiency_buckets": dict_proficiency_buckets,
            "dict_points_buckets": dict_points_buckets,
            "student_email": user.email(),
            "tz_offset": tz_offset,
            "graph_title": graph_title,
            }
