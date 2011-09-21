import datetime
import os
import logging

import shared_jinja

from app import App
import layer_cache
from models import Video, Playlist, VideoPlaylist, Setting
from topics_list import topics_list
import request_handler
import util

@layer_cache.cache_with_key_fxn(
        lambda *args, **kwargs: "library_content_html_%s" % Setting.cached_library_content_date()
        )
def library_content_html(bust_cache = False):
    # No cache found -- regenerate HTML
    all_playlists = []

    dict_videos = {}
    dict_videos_counted = {}
    dict_playlists = {}
    dict_playlists_by_title = {}
    dict_video_playlists = {}

    async_queries = [
        Video.all(),
        Playlist.all(),
        VideoPlaylist.all().filter('live_association = ', True).order('video_position'),
    ]

    results = util.async_queries(async_queries)

    for video in results[0].get_result():
        dict_videos[video.key()] = video

    for playlist in results[1].get_result():
        dict_playlists[playlist.key()] = playlist
        if playlist.title in topics_list:
            dict_playlists_by_title[playlist.title] = playlist

    for video_playlist in results[2].get_result():
        playlist_key = VideoPlaylist.playlist.get_value_for_datastore(video_playlist)
        video_key = VideoPlaylist.video.get_value_for_datastore(video_playlist)

        if dict_videos.has_key(video_key) and dict_playlists.has_key(playlist_key):
            video = dict_videos[video_key]
            playlist = dict_playlists[playlist_key]
            fast_video_playlist_dict = {"video":video, "playlist":playlist}

            if dict_video_playlists.has_key(playlist_key):
                dict_video_playlists[playlist_key].append(fast_video_playlist_dict)
            else:
                dict_video_playlists[playlist_key] = [fast_video_playlist_dict]

            if dict_playlists_by_title.has_key(playlist.title):
                # Only count videos in topics_list
                dict_videos_counted[video.youtube_id] = True

    # Update count of all distinct videos associated w/ a live playlist
    Setting.count_videos(len(dict_videos_counted.keys()))

    for topic in topics_list:
        if topic in dict_playlists_by_title:
            playlist = dict_playlists_by_title[topic]
            playlist_key = playlist.key()
            playlist_videos = dict_video_playlists.get(playlist_key) or []

            if not playlist_videos:
                logging.error('Playlist %s has no videos!', playlist.title)

            playlist_data = {
                     'title': topic,
                     'topic': topic,
                     'playlist': playlist,
                     'videos': playlist_videos,
                     'next': None
                     }

            all_playlists.append(playlist_data)

    playlist_data_prev = None
    for playlist_data in all_playlists:
        if playlist_data_prev:
            playlist_data_prev['next'] = playlist_data
        playlist_data_prev = playlist_data

    # Separating out the columns because the formatting is a little different on each column
    template_values = {
        'App' : App,
        'all_playlists': all_playlists,
        }

    html = shared_jinja.get().render_template("library_content_template.html", **template_values)

    # Set shared date of last generated content
    Setting.cached_library_content_date(str(datetime.datetime.now()))

    return html

class GenerateLibraryContent(request_handler.RequestHandler):

    def post(self):
        # We support posts so we can fire task queues at this handler
        self.get(from_task_queue = True)

    def get(self, from_task_queue = False):
        library_content_html(bust_cache=True)

        if not from_task_queue:
            self.redirect("/")

