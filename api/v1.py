import logging

import models
import layer_cache

from api import route
from api.decorators import jsonify, jsonp, compress, decompress

@route("/api/v1/playlists", methods=["GET"])
@jsonp
@layer_cache.cache_with_key_fxn(
    lambda: "api_playlists_%s" % models.Setting.cached_library_content_date(), 
    layer=layer_cache.Layers.Memcache)
@jsonify
def playlists_v1():
    return models.Playlist.get_for_all_topics()

@route("/api/v1/playlists/videos/<playlist_title>", methods=["GET"])
@jsonp
@layer_cache.cache_with_key_fxn(
    lambda playlist_title: "api_playlistvideos_%s_%s" % (playlist_title, models.Setting.cached_library_content_date()), 
    layer=layer_cache.Layers.Memcache)
@jsonify
def playlist_videos_v1(playlist_title):
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

@route("/api/v1/playlists/library", methods=["GET"])
@jsonp
@decompress # We compress and decompress around layer_cache so memcache never has any trouble storing the large amount of library data.
@layer_cache.cache_with_key_fxn(
    lambda: "api_library_%s" % models.Setting.cached_library_content_date(), 
    layer=layer_cache.Layers.Memcache)
@compress
@jsonify
def playlists_library_v1():
    playlist_api_dicts = []
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
