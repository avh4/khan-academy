from google.appengine.ext import db
from google.appengine.api import memcache

import app
from app import App
from models import Video, Playlist

from django.utils import simplejson
import logging

CACHE_EXPIRATION_SECONDS = 60 * 60 * 24 # Expires after one day
MAX_RESULTS_PER_TYPE = 10
VIDEO_TITLE_MEMCACHE_KEY = "video_title_dicts"
PLAYLIST_TITLE_MEMCACHE_KEY = "playlist_title_dicts"

class Autocomplete(app.RequestHandler):

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

            video_results = sorted(video_results, key=lambda dict: dict["title"].lower())[:MAX_RESULTS_PER_TYPE]
            playlist_results = sorted(playlist_results, key=lambda dict: dict["title"].lower())[:MAX_RESULTS_PER_TYPE]

        json = simplejson.dumps({"query": query, "videos": video_results, "playlists": playlist_results}, ensure_ascii=False)
        self.response.out.write(json)

def video_title_dicts():
    # Use a key namespace for the current app version so any new deployments are guaranteed to get fresh data.
    dicts = memcache.get(VIDEO_TITLE_MEMCACHE_KEY, namespace=App.version)

    if dicts == None:
        dicts = map(lambda video: {"title": video.title, "url": "/video/%s" % video.readable_id}, Video.all())
        if not memcache.set(VIDEO_TITLE_MEMCACHE_KEY, dicts, time=CACHE_EXPIRATION_SECONDS, namespace=App.version):
            logging.error("Memcache set failed for %s" % VIDEO_TITLE_MEMCACHE_KEY)

    return dicts

def playlist_title_dicts():
    dicts = memcache.get(PLAYLIST_TITLE_MEMCACHE_KEY, namespace=App.version)

    if dicts == None:
        dicts = map(lambda playlist: {"title": playlist.title, "url": "/#%s" % playlist.title}, Playlist.all())
        if not memcache.set(PLAYLIST_TITLE_MEMCACHE_KEY, dicts, time=CACHE_EXPIRATION_SECONDS, namespace=App.version):
            logging.error("Memcache set failed for %s" % PLAYLIST_TITLE_MEMCACHE_KEY)

    return dicts
