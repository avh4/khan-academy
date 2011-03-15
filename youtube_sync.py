import cgi
import datetime
import logging
import re
from urlparse import urlparse

import gdata.youtube
import gdata.youtube.service
import gdata.alt.appengine

from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.ext import db

from models import Setting, Video, Playlist, VideoPlaylist
import request_handler

class YouTubeSyncStep:
    START = 0
    UPDATE_VIDEO_AND_PLAYLIST_DATA = 1 # Sets all VideoPlaylist.dt_last_live_association = Setting.dtLastYouTubeSyncStart
    UPDATE_VIDEO_AND_PLAYLIST_READABLE_NAMES = 2
    COMMIT_LIVE_ASSOCIATIONS = 3 # Put entire set of video_playlists in bulk according to dt_last_live_association
    INDEX_VIDEO_AND_PLAYLIST_DATA = 4
    REGENERATE_LIBRARY_CONTENT = 5
    FINISH = 6

class YouTubeSync(request_handler.RequestHandler):

    def get(self):
        self.task_step(0)

    def post(self):
        # Protected for admins only by app.yaml so taskqueue can hit this URL
        step = self.request_int("step", default = 0)

        if step == YouTubeSyncStep.START:
            self.startYouTubeSync()
        elif step == YouTubeSyncStep.UPDATE_VIDEO_AND_PLAYLIST_DATA:
            self.updateVideoAndPlaylistData()
        elif step == YouTubeSyncStep.UPDATE_VIDEO_AND_PLAYLIST_READABLE_NAMES:
            self.updateVideoAndPlaylistReadableNames()
        elif step == YouTubeSyncStep.COMMIT_LIVE_ASSOCIATIONS:
            self.commitLiveAssociations()
        elif step == YouTubeSyncStep.INDEX_VIDEO_AND_PLAYLIST_DATA:
            self.indexVideoAndPlaylistData()
        elif step == YouTubeSyncStep.REGENERATE_LIBRARY_CONTENT:
            self.regenerateLibraryContent()
        elif step == YouTubeSyncStep.FINISH:
            self.finishYouTubeSync()

        if step < YouTubeSyncStep.FINISH:
            self.task_step(step + 1)

    def task_step(self, step):
        taskqueue.add(url='/admin/youtubesync', queue_name='youtube-sync-queue', params={'step': step})

    def startYouTubeSync(self):
        Setting.dt_last_youtube_sync_start(str(datetime.datetime.now()))

    def updateVideoAndPlaylistData(self):
        pass

    def updateVideoAndPlaylistReadableNames(self):
        pass

    def commitLiveAssociations(self):
        pass

    def indexVideoAndPlaylistData(self):
        pass

    def regenerateLibraryContent(self):
        pass

    def finishYouTubeSync(self):
        Setting.dt_last_youtube_sync_finish(str(datetime.datetime.now()))

class UpdateVideoReadableNames(request_handler.RequestHandler):  #Makes sure every video and playlist has a unique "name" that can be used in URLs

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return
        query = Video.all()
        all_videos = query.fetch(100000)
        for video in all_videos:
            potential_id = re.sub('[^a-z0-9]', '-', video.title.lower());
            potential_id = re.sub('-+$', '', potential_id)  # remove any trailing dashes (see issue 1140)
            potential_id = re.sub('^-+', '', potential_id)  # remove any leading dashes (see issue 1526)                        
            if video.readable_id == potential_id: # id is unchanged
                continue
            number_to_add = 0
            current_id = potential_id
            while True:
                query = Video.all()
                query.filter('readable_id=', current_id)
                if (query.get() is None): #id is unique so use it and break out
                    video.readable_id = current_id
                    video.put()
                    break
                else: # id is not unique so will have to go through loop again
                    number_to_add+=1
                    current_id = potential_id+'-'+number_to_add                       
        
class UpdateVideoData(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return

        self.response.out.write('<html>')
        yt_service = gdata.youtube.service.YouTubeService()
        playlist_feed = yt_service.GetYouTubePlaylistFeed(uri='http://gdata.youtube.com/feeds/api/users/khanacademy/playlists?start-index=1&max-results=50')

        # The next block makes all current VideoPlaylist entries false so that we don't get remnant associations
        query = VideoPlaylist.all()
        all_video_playlists = []

        for video_playlist in query:
            video_playlist.live_association = False
            all_video_playlists.append(video_playlist)
        db.put(all_video_playlists)

        video_youtube_id_dict = Video.get_dict(Video.all(), lambda video: video.youtube_id)
        video_playlist_key_dict = VideoPlaylist.get_key_dict(VideoPlaylist.all())

        for playlist in playlist_feed.entry:

            self.response.out.write('<p>Playlist  ' + playlist.id.text)
            playlist_id = playlist.id.text.replace('http://gdata.youtube.com/feeds/api/users/khanacademy/playlists/', '')
            playlist_uri = playlist.id.text.replace('users/khanacademy/', '')
            query = Playlist.all()
            query.filter('youtube_id =', playlist_id)
            playlist_data = query.get()
            if not playlist_data:
                playlist_data = Playlist(youtube_id=playlist_id)
                self.response.out.write('<p><strong>Creating Playlist: ' + playlist.title.text + '</strong>')
            playlist_data.url = playlist_uri
            playlist_data.title = playlist.title.text
            playlist_data.description = playlist.description.text
            playlist_data.put()
            playlist_data.index()
            playlist_data.indexed_title_changed()
            
            for i in range(0, 10):
                start_index = i * 50 + 1
                video_feed = yt_service.GetYouTubePlaylistVideoFeed(uri=playlist_uri + '?start-index=' + str(start_index) + '&max-results=50')
                video_data_list = []

                if len(video_feed.entry) <= 0:
                    # No more videos in playlist
                    break

                for video in video_feed.entry:

                    video_id = cgi.parse_qs(urlparse(video.media.player.url).query)['v'][0].decode('windows-1252')

                    video_data = None
                    if video_youtube_id_dict.has_key(video_id):
                        video_data = video_youtube_id_dict[video_id]
                    
                    if not video_data:
                        video_data = Video(youtube_id=video_id)
                        self.response.out.write('<p><strong>Creating Video: ' + video.media.title.text.decode('windows-1252') + '</strong>')
                        video_data.playlists = []

                    video_data.title = video.media.title.text.decode('windows-1252')
                    video_data.url = video.media.player.url.decode('windows-1252')
                    video_data.duration = int(video.media.duration.seconds)
                    video_data.views = int(video.statistics.view_count)

                    if video.media.description.text is not None:
                        video_data.description = video.media.description.text.decode('windows-1252')
                    else:
                        video_data.decription = ' '

                    if playlist.title.text not in video_data.playlists:
                        video_data.playlists.append(playlist.title.text.decode('windows-1252'))
                    video_data.keywords = video.media.keywords.text.decode('windows-1252')
                    video_data.position = video.position
                    video_data_list.append(video_data)
                db.put(video_data_list)
                for video_data in video_data_list:
                    video_data.index()
                    video_data.indexed_title_changed()

                playlist_videos = []
                for video_data in video_data_list:                
                    playlist_video = None
                    if video_playlist_key_dict.has_key(playlist_data.key()):
                        if video_playlist_key_dict[playlist_data.key()].has_key(video_data.key()):
                            playlist_video = video_playlist_key_dict[playlist_data.key()][video_data.key()]

                    if not playlist_video:
                        playlist_video = VideoPlaylist(playlist=playlist_data.key(), video=video_data.key())
                        self.response.out.write('<p><strong>Creating VideoPlaylist(' + playlist_data.title + ',' + video_data.title + ')</strong>')
                    else:
                        self.response.out.write('<p>Updating VideoPlaylist(' + playlist_video.playlist.title + ',' + playlist_video.video.title + ')')
                    playlist_video.live_association = True
                    playlist_video.video_position = int(video_data.position.text)
                    playlist_videos.append(playlist_video)
                db.put(playlist_videos)


