import copy
import logging

from google.appengine.api import users

from flask import request

import models
import layer_cache
import topics_list

from api import route
from api.decorators import jsonify, jsonp, compress, decompress, etag
from api.auth.decorators import oauth_required

import util

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
@etag(lambda: models.Setting.cached_library_content_date())
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
def get_visible_user_data_from_request(user_coach):

    email_student = request.values.get("email")
    if not email_student:
        return None

    user_student = util.get_current_user() if email_student == "me" else users.User(email_student)
    user_data_student = models.UserData.get_for(user_student)

    if user_data_student and (user_student.email() == user_coach.email() or user_data_student.is_coached_by(user_coach)):
        return user_data_student

    return None

@route("/api/v1/users/me", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_data_me():
    user = util.get_current_user()
    if user:
        return models.UserData.get_for(user)
    return None

@route("/api/v1/users", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_data_other():
    user = util.get_current_user()

    if user:
        user_data_student = get_visible_user_data_from_request(user)
        if user_data_student:
            return user_data_student

    return None

@route("/api/v1/users/videos", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_videos_all():
    user = util.get_current_user()

    if user:
        user_data_student = get_visible_user_data_from_request(user)

        if user_data_student:
            user_videos = models.UserVideo.all().filter("user =", user_data_student.user)
            return user_videos.fetch(10000)

    return None

@route("/api/v1/users/videos/<youtube_id>", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_videos_specific(youtube_id):
    user = util.get_current_user()

    if user and youtube_id:
        user_data_student = get_visible_user_data_from_request(user)
        video = models.Video.all().filter("youtube_id =", youtube_id).get()

        if user_data_student and video:
            user_videos = models.UserVideo.all().filter("user =", user_data_student.user).filter("video =", video)
            return user_videos.get()

    return None

@route("/api/v1/users/videos/<youtube_id>/log", methods=["POST"])
@oauth_required
@jsonp
@jsonify
def log_user_video(youtube_id):
    user = util.get_current_user()

    if user and youtube_id:
        user_data= models.UserData.get_for(user)
        video = models.Video.all().filter("youtube_id =", youtube_id).get()

        seconds_watched = last_second_watched = 0

        try:
            seconds_watched = int(float(request.values.get("seconds_watched")))
            last_second_watched = int(float(request.values.get("last_second_watched")))
        except ValueError:
            pass

        if user_data and video:
            return models.VideoLog.add_entry(user_data, video, seconds_watched, last_second_watched)

    return 0

@route("/api/v1/users/exercises", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_exercises_all():
    user = util.get_current_user()

    if user:
        user_data_student = get_visible_user_data_from_request(user)

        if user_data_student:
            user_exercises = models.UserExercise.all().filter("user =", user_data_student.user)
            return user_exercises.fetch(10000)

    return None

@route("/api/v1/users/exercises/<exercise_name>", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_exercises_specific(exercise_name):
    user = util.get_current_user()

    if user and exercise_name:
        user_data_student = get_visible_user_data_from_request(user)

        if user_data_student:
            user_exercises = models.UserExercise.all().filter("user =", user_data_student.user).filter("exercise =", exercise_name)
            return user_exercises.get()

    return None

@route("/api/v1/users/playlists", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_playlists_all():
    user = util.get_current_user()

    if user:
        user_data_student = get_visible_user_data_from_request(user)

        if user_data_student:
            user_playlists = models.UserPlaylist.all().filter("user =", user_data_student.user)
            return user_playlists.fetch(10000)

    return None

@route("/api/v1/users/playlists/<playlist_title>", methods=["GET"])
@oauth_required
@jsonp
@jsonify
def user_playlists_specific(playlist_title):
    user = util.get_current_user()

    if user and playlist_title:
        user_data_student = get_visible_user_data_from_request(user)
        playlist = models.Playlist.all().filter("title =", playlist_title).get()

        if user_data_student and playlist:
            user_playlists = models.UserPlaylist.all().filter("user =", user_data_student.user).filter("playlist =", playlist)
            return user_playlists.get()

    return None
