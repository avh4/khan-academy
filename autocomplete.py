import logging

from google.appengine.ext import db
import simplejson

import app
from app import App
import request_handler
import consts
import layer_cache
from models import Video, Playlist, VideoPlaylist
from templatefilters import slugify

CACHE_EXPIRATION_SECONDS = 60 * 60 * 24 * 3 # Expires after three days

@layer_cache.cache(expiration=CACHE_EXPIRATION_SECONDS)
def video_title_dicts():
    return map(lambda video: {
        "title": video.title,
        "key": str(video.key()),
        "ka_url": "/video/%s" % video.readable_id
    }, Video.get_all_live())

@layer_cache.cache(expiration=CACHE_EXPIRATION_SECONDS)
def playlist_title_dicts():
    return map(lambda playlist: {
        "title": playlist.title,
        "key": str(playlist.key()),
        "ka_url": "/#%s" % slugify(playlist.title.lower())
    }, Playlist.all())
