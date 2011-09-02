import logging

from google.appengine.ext import db
from django.template.defaultfilters import slugify
import simplejson

import app
from app import App
import request_handler
import consts
import layer_cache
from models import Video, Playlist, VideoPlaylist

CACHE_EXPIRATION_SECONDS = 60 * 60 * 24 * 3 # Expires after three days
MAX_RESULTS_PER_TYPE = 10

class Autocomplete(request_handler.RequestHandler):

    def get(self):

        video_results = []
        playlist_results = []

        query = self.request.get('q')
        query = query.strip().lower()

        if query:

            # Instead of using memcache and iterating through all videos and playlists, we could use the "fake prefix match" example at
            # code.google.com/appengine/docs/python/datastore/queriesandindexes.html to query the GAE datastore directly
            # for any Video/Playlist titles prefixed by query, but this would A) be less powerful b/c it only matches prefixes
            # and B) require us to make us to use a title_lowercase DerivedProperty or something similar to avoid case
            # sensitivity issues.
            #
            # However, memcache fits this solution because it's very quick, full-substring searches are much stronger than
            # prefix-only, and it's acceptable for this data to rarely and briefly be out-of-date.

            video_results = filter(lambda video_dict: query in video_dict["title"].lower(), video_title_dicts())
            playlist_results = filter(lambda playlist_dict: query in playlist_dict["title"].lower(), playlist_title_dicts())

            video_results = sorted(video_results, key=lambda dict: dict["title"].lower().index(query))[:MAX_RESULTS_PER_TYPE]
            playlist_results = sorted(playlist_results, key=lambda dict: dict["title"].lower().index(query))[:MAX_RESULTS_PER_TYPE]

        json = simplejson.dumps({"query": query, "videos": video_results, "playlists": playlist_results}, ensure_ascii=False)
        self.response.out.write(json)

@layer_cache.cache(expiration=CACHE_EXPIRATION_SECONDS)
def video_title_dicts():
    return map(lambda video: {
        "title": video.title,
        "key": str(video.key()),
        "url": "/video/%s" % video.readable_id
    }, Video.get_all_live())

@layer_cache.cache(expiration=CACHE_EXPIRATION_SECONDS)
def playlist_title_dicts():
    return map(lambda playlist: {
        "title": playlist.title,
        "url": "/#%s" % slugify(playlist.title.lower())
    }, Playlist.all())
