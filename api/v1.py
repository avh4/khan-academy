import copy
import datetime
import logging

from google.appengine.api import users

from flask import request, current_app

import models
import layer_cache
import topics_list
from badges import badges, util_badges, models_badges
import util

from api import route
from api.decorators import jsonify, jsonp, compress, decompress, etag
from api.auth.decorators import oauth_required, oauth_optional

def api_error_response(e):
    return current_app.response_class("API error. %s" % e.message, status=500)

def add_action_results_property(obj, dict_results):
    badges_earned = []

    user_data = models.UserData.current()
    user = user_data.user
    if user:
        badge_counts = util_badges.get_badge_counts(user_data)

        user_badges = badges.UserBadgeNotifier.pop_for_user(user)
        badges_dict = util_badges.all_badges_dict()

        for user_badge in user_badges:
            badge = badges_dict.get(user_badge.badge_name)

            if badge:
                if not hasattr(badge, "user_badges"):
                    badge.user_badges = []
                badge.user_badges.append(user_badge)
                badge.is_owned = True
                badges_earned.append(badge)

    dict_results["badges_earned"] = badges_earned

    obj.action_results = dict_results

@route("/api/v1/playlists", methods=["GET"])
@jsonp
@layer_cache.cache_with_key_fxn(
    lambda: "api_playlists_%s" % models.Setting.cached_library_content_date(), 
    layer=layer_cache.Layers.Memcache)
@jsonify
def playlists():
    return models.Playlist.get_for_all_topics()

@route("/api/v1/playlists/<playlist_title>/videos", methods=["GET"])
@jsonp
@layer_cache.cache_with_key_fxn(
    lambda playlist_title: "api_playlistvideos_%s_%s" % (playlist_title, models.Setting.cached_library_content_date()), 
    layer=layer_cache.Layers.Memcache)
@jsonify
def playlist_videos(playlist_title):
    query = models.Playlist.all()
    query.filter('title =', playlist_title)
    playlist = query.get()

    if not playlist:
        return None

    video_query = models.Video.all()
    video_query.filter('playlists = ', playlist_title)
    video_key_dict = models.Video.get_dict(video_query, lambda video: video.key())

    video_playlist_query = models.VideoPlaylist.all()
    video_playlist_query.filter('playlist =', playlist)
    video_playlist_query.filter('live_association =', True)
    video_playlist_key_dict = models.VideoPlaylist.get_key_dict(video_playlist_query)

    video_playlists = sorted(video_playlist_key_dict[playlist.key()].values(), key=lambda video_playlist: video_playlist.video_position)

    videos = []
    for video_playlist in video_playlists:
        video = video_key_dict[models.VideoPlaylist.video.get_value_for_datastore(video_playlist)]
        video.position = video_playlist.video_position
        videos.append(video)
    
    return videos

@route("/api/v1/playlists/<playlist_title>/exercises", methods=["GET"])
@jsonp
@layer_cache.cache_with_key_fxn(
    lambda playlist_title: "api_playlistexercises_%s" % (playlist_title),
    layer=layer_cache.Layers.Memcache)
@jsonify
def playlist_exercises(playlist_title):
    query = models.Playlist.all()
    query.filter('title =', playlist_title)
    playlist = query.get()

    if not playlist:
        return None

    video_query = models.Video.all(keys_only=True)
    video_query.filter('playlists = ', playlist_title)
    video_keys = video_query.fetch(1000)

    exercise_query = models.Exercise.all()
    exercise_key_dict = models.Exercise.get_dict(exercise_query, lambda exercise: exercise.key())

    exercise_video_query = models.ExerciseVideo.all()
    exercise_video_key_dict = models.ExerciseVideo.get_key_dict(exercise_video_query)

    playlist_exercise_dict = {}
    for video_key in video_keys:
        if exercise_video_key_dict.has_key(video_key):
            for exercise_key in exercise_video_key_dict[video_key]:
                if exercise_key_dict.has_key(exercise_key):
                    exercise = exercise_key_dict[exercise_key]
                    playlist_exercise_dict[exercise_key] = exercise

    playlist_exercises = []
    for exercise_key in playlist_exercise_dict:
        playlist_exercises.append(playlist_exercise_dict[exercise_key])

    return playlist_exercises

@route("/api/v1/playlists/library", methods=["GET"])
@etag(lambda: models.Setting.cached_library_content_date())
@jsonp
@decompress # We compress and decompress around layer_cache so memcache never has any trouble storing the large amount of library data.
@layer_cache.cache_with_key_fxn(
    lambda: "api_library_%s" % models.Setting.cached_library_content_date(), 
    layer=layer_cache.Layers.Memcache)
@compress
@jsonify
def playlists_library():
    playlists = fully_populated_playlists()

    playlist_dict = {}
    for playlist in playlists:
        playlist_dict[playlist.title] = playlist

    playlist_structure = copy.deepcopy(topics_list.PLAYLIST_STRUCTURE)
    replace_playlist_values(playlist_structure, playlist_dict)

    return playlist_structure

@route("/api/v1/playlists/library/list", methods=["GET"])
@jsonp
@decompress # We compress and decompress around layer_cache so memcache never has any trouble storing the large amount of library data.
@layer_cache.cache_with_key_fxn(
    lambda: "api_library_list_%s" % models.Setting.cached_library_content_date(), 
    layer=layer_cache.Layers.Memcache)
@compress
@jsonify
def playlists_library_list():
    return fully_populated_playlists()

@route("/api/v1/exercises", methods=["GET"])
@jsonp
@jsonify
def exercises():
    return models.Exercise.get_all_use_cache()

@route("/api/v1/exercises/<exercise_name>", methods=["GET"])
@jsonp
@jsonify
def exercises(exercise_name):
    return models.Exercise.get_by_name(exercise_name)

@route("/api/v1/exercises/<exercise_name>/videos", methods=["GET"])
@jsonp
@jsonify
def exercise_videos(exercise_name):
    exercise = models.Exercise.get_by_name(exercise_name)
    if exercise:
        exercise_videos = exercise.related_videos()
        return map(lambda exercise_video: exercise_video.video, exercise_videos)
    return []

@route("/api/v1/videos/<video_id>", methods=["GET"])
@jsonp
@jsonify
def video(video_id):
    return models.Video.all().filter("youtube_id =", video_id).get()

@route("/api/v1/videos/<video_id>/download_available", methods=["POST"])
@oauth_required(require_anointed_consumer=True)
@jsonp
@jsonify
def video_download_available(video_id):
    video = models.Video.all().filter("youtube_id =", video_id).get()
    if video:
        video.download_available = request.request_bool("available", default=False)
        video.put()
    return video

@route("/api/v1/videos/<video_id>/exercises", methods=["GET"])
@jsonp
@jsonify
def video_exercises(video_id):
    video = models.Video.all().filter("youtube_id =", video_id).get()
    if video:
        exercise_videos = video.related_exercises()
        return map(lambda exercise_video: exercise_video.exercise, exercise_videos)
    return []

def fully_populated_playlists():
    playlists = models.Playlist.get_for_all_topics()
    video_key_dict = models.Video.get_dict(models.Video.all(), lambda video: video.key())

    video_playlist_query = models.VideoPlaylist.all()
    video_playlist_query.filter('live_association =', True)
    video_playlist_key_dict = models.VideoPlaylist.get_key_dict(video_playlist_query)

    for playlist in playlists:
        playlist.videos = []
        video_playlists = sorted(video_playlist_key_dict[playlist.key()].values(), key=lambda video_playlist: video_playlist.video_position)
        for video_playlist in video_playlists:
            video = video_key_dict[models.VideoPlaylist.video.get_value_for_datastore(video_playlist)]
            video.position = video_playlist.video_position
            playlist.videos.append(video)

    return playlists

def replace_playlist_values(structure, playlist_dict):
    if type(structure) == list:
        for sub_structure in structure:
            replace_playlist_values(sub_structure, playlist_dict)
    else:
        if structure.has_key("items"):
            replace_playlist_values(structure["items"], playlist_dict)
        elif structure.has_key("playlist"):
            # Replace string playlist title with real playlist object
            structure["playlist"] = playlist_dict[structure["playlist"]]

# Return specific user data requests from request
# IFF currently logged in user has permission to view
def get_visible_user_data_from_request():

    user = models.UserData.current().user
    if not user:
        return None

    email_student = request.request_string("email")
    user_student = users.User(email_student) if email_student else user

    user_data_student = models.UserData.get_for(user_student)

    if user_data_student and (user_student.email() == user.email() or user_data_student.is_coached_by(user)):
        return user_data_student

    return None

@route("/api/v1/user", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_data_other():
    user = models.UserData.current().user

    if user:
        user_data_student = get_visible_user_data_from_request()
        if user_data_student:
            return user_data_student

    return None

def filter_query_by_request_dates(query, property):

    if request.request_string("dt_start"):
        try:
            dt_start = request.request_date_iso("dt_start")
            query.filter("%s >=" % property, dt_start)
        except ValueError:
            raise ValueError("Invalid date format sent to dt_start, use ISO 8601.")

    if request.request_string("dt_end"):
        try:
            dt_end = request.request_date_iso("dt_end")
            query.filter("%s <=" % property, dt_end)
        except ValueError:
            raise ValueError("Invalid date format sent to dt_end, use ISO 8601.")

@route("/api/v1/user/videos", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_videos_all():
    user = models.UserData.current().user

    if user:
        user_data_student = get_visible_user_data_from_request()

        if user_data_student:
            user_videos_query = models.UserVideo.all().filter("user =", user_data_student.user)

            try:
                filter_query_by_request_dates(user_videos_query, "last_watched")
            except ValueError, e:
                return api_error_response(e)

            return user_videos_query.fetch(10000)

    return None

@route("/api/v1/user/videos/<youtube_id>", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_videos_specific(youtube_id):
    user = models.UserData.current().user

    if user and youtube_id:
        user_data_student = get_visible_user_data_from_request()
        video = models.Video.all().filter("youtube_id =", youtube_id).get()

        if user_data_student and video:
            user_videos = models.UserVideo.all().filter("user =", user_data_student.user).filter("video =", video)
            return user_videos.get()

    return None

@route("/api/v1/user/videos/<youtube_id>/log", methods=["POST"])
@oauth_required(require_anointed_consumer=True)
@jsonp
@jsonify
def log_user_video(youtube_id):

    user_data = models.UserData.current()
    user = user_data.user

    points = 0
    video_log = None

    if user and youtube_id:
        video = models.Video.all().filter("youtube_id =", youtube_id).get()

        seconds_watched = int(request.request_float("seconds_watched", default = 0))
        last_second_watched = int(request.request_float("last_second_watched", default = 0))

        if video:
            user_video, video_log, video_points_total = models.VideoLog.add_entry(user_data, video, seconds_watched, last_second_watched)

            if video_log:
                add_action_results_property(video_log, {"user_video": user_video, "user_data": models.UserData.get_for(user)})

    return video_log

@route("/api/v1/user/exercises", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_exercises_all():
    user = models.UserData.current().user

    if user:
        user_data_student = get_visible_user_data_from_request()

        if user_data_student:
            user_exercises = models.UserExercise.all().filter("user =", user_data_student.user)
            return user_exercises.fetch(10000)

    return None

@route("/api/v1/user/exercises/<exercise_name>", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_exercises_specific(exercise_name):
    user = models.UserData.current().user

    if user and exercise_name:
        user_data_student = get_visible_user_data_from_request()

        if user_data_student:
            user_exercises = models.UserExercise.all().filter("user =", user_data_student.user).filter("exercise =", exercise_name)
            return user_exercises.get()

    return None

@route("/api/v1/user/playlists", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_playlists_all():
    user = models.UserData.current().user

    if user:
        user_data_student = get_visible_user_data_from_request()

        if user_data_student:
            user_playlists = models.UserPlaylist.all().filter("user =", user_data_student.user)
            return user_playlists.fetch(10000)

    return None

@route("/api/v1/user/playlists/<playlist_title>", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_playlists_specific(playlist_title):
    user = models.UserData.current().user

    if user and playlist_title:
        user_data_student = get_visible_user_data_from_request()
        playlist = models.Playlist.all().filter("title =", playlist_title).get()

        if user_data_student and playlist:
            user_playlists = models.UserPlaylist.all().filter("user =", user_data_student.user).filter("playlist =", playlist)
            return user_playlists.get()

    return None

@route("/api/v1/user/exercises/<exercise_name>/log", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_problem_logs(exercise_name):
    user = models.UserData.current().user

    if user and exercise_name:
        user_data_student = get_visible_user_data_from_request()
        exercise = models.Exercise.get_by_name(exercise_name)

        if user_data_student and exercise:

            problem_log_query = models.ProblemLog.all()
            problem_log_query.filter("user =", user)
            problem_log_query.filter("exercise =", exercise.name)

            try:
                filter_query_by_request_dates(problem_log_query, "time_done")
            except ValueError, e:
                return api_error_response(e)

            problem_log_query.order("time_done")

            return problem_log_query.fetch(500)

    return None

@route("/api/v1/user/videos/<youtube_id>/log", methods=["GET"])
@oauth_required()
@jsonp
@jsonify
def user_video_logs(youtube_id):
    user = models.UserData.current().user

    if user and youtube_id:
        user_data_student = get_visible_user_data_from_request()
        video = models.Video.all().filter("youtube_id =", youtube_id).get()

        if user_data_student and video:

            video_log_query = models.VideoLog.all()
            video_log_query.filter("user =", user)
            video_log_query.filter("video =", video)

            try:
                filter_query_by_request_dates(video_log_query, "time_watched")
            except ValueError, e:
                return api_error_response(e)

            video_log_query.order("time_watched")

            return video_log_query.fetch(500)

    return None

@route("/api/v1/badges", methods=["GET"])
@oauth_optional()
@jsonp
@jsonify
def badges_list():
    badges_dict = util_badges.all_badges_dict()

    user = models.UserData.current().user
    if user:

        user_data_student = get_visible_user_data_from_request()
        if user_data_student:

            user_badges = models_badges.UserBadge.get_for(user_data_student.user)

            for user_badge in user_badges:

                badge = badges_dict.get(user_badge.badge_name)

                if badge:
                    if not hasattr(badge, "user_badges"):
                        badge.user_badges = []
                    badge.user_badges.append(user_badge)
                    badge.is_owned = True

    return sorted(filter(lambda badge: not badge.is_hidden(), badges_dict.values()), key=lambda badge: badge.name)

@route("/api/v1/badges/categories", methods=["GET"])
@jsonp
@jsonify
def badge_categories():
    return badges.BadgeCategory.all()

@route("/api/v1/badges/categories/<category>", methods=["GET"])
@jsonp
@jsonify
def badge_category(category):
    return filter(lambda badge_category: str(badge_category.category) == category, badges.BadgeCategory.all())
