import logging

import models
from api import api_app
from api.decorators import jsonp

@api_app.route("/api/v1/playlists", methods=["GET"])
@jsonp
def playlists_v1():
    return models.Playlist.get_for_all_topics()

@api_app.route("/api/v1/playlists/videos/<playlist_name>", methods=["GET"])
@jsonp
def playlist_videos_v1(playlist_name):
    pass

@api_app.route("/api/v1/playlists/library", methods=["GET"])
@jsonp
def playlists_library_v1():
    pass

