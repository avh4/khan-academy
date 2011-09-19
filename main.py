#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import datetime
import time
import urllib
import urlparse
import logging
import re
import devpanel
from pprint import pformat
from google.appengine.api import capabilities
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.runtime.apiproxy_errors import DeadlineExceededError

import config_django

from django.template.loader import render_to_string
import simplejson
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from google.appengine.api import taskqueue

import bulk_update.handler
import facebook
import request_cache
from gae_mini_profiler import profiler
from gae_bingo.middleware import GAEBingoWSGIMiddleware
from gae_bingo.gae_bingo import bingo
import autocomplete
import coaches
import knowledgemap
import consts
import youtube_sync
import warmup
import library
import homepage

from search import Searchable
import search

import request_handler
from app import App
import app
import util
import user_util
import points
import exercise_statistics
import backfill
import activity_summary
import exercises
import dashboard
import exercisestats.report
import exercisestats.report_json
import github
import paypal

import models
from models import UserExercise, Exercise, UserData, Video, Playlist, ProblemLog, VideoPlaylist, ExerciseVideo, Setting, UserVideo, UserPlaylist, VideoLog
from discussion import comments, notification, qa, voting
from about import blog, util_about
from phantom_users import util_notify
from badges import util_badges, custom_badges
from mailing_lists import util_mailing_lists
from profiles import util_profile
from topics_list import all_topics_list
from custom_exceptions import MissingVideoException
from render import render_block_to_string
from templatetags import streak_bar, exercise_message, exercise_icon, user_points
from badges.templatetags import badge_notifications, badge_counts
from oauth_provider import apps as oauth_apps
from phantom_users.phantom_util import create_phantom, get_phantom_user_id_from_cookies
from phantom_users.cloner import Clone
from counters import user_counter
from notifications import UserNotifier
from nicknames import get_nickname_for

class VideoDataTest(request_handler.RequestHandler):

    @user_util.developer_only
    def get(self):
        self.response.out.write('<html>')
        videos = Video.all()
        for video in videos:
            self.response.out.write('<P>Title: ' + video.title)


class DeleteVideoPlaylists(request_handler.RequestHandler):
# Deletes at most 200 Video-Playlist associations that are no longer live.  Should be run every-now-and-then to make sure the table doesn't get too big
    @user_util.developer_only
    def get(self):
        query = VideoPlaylist.all()
        all_video_playlists = query.fetch(200)
        video_playlists_to_delete = []
        for video_playlist in all_video_playlists:
            if video_playlist.live_association != True:
                video_playlists_to_delete.append(video_playlist)
        db.delete(video_playlists_to_delete)


class KillLiveAssociations(request_handler.RequestHandler):
    @user_util.developer_only
    def get(self):
        query = VideoPlaylist.all()
        all_video_playlists = query.fetch(100000)
        for video_playlist in all_video_playlists:
            video_playlist.live_association = False
        db.put(all_video_playlists)

def get_mangled_playlist_name(playlist_name):
    for char in " :()":
        playlist_name = playlist_name.replace(char, "")
    return playlist_name

class ViewVideo(request_handler.RequestHandler):
    def get(self):

        # This method displays a video in the context of a particular playlist.
        # To do that we first need to find the appropriate playlist.  If we aren't
        # given the playlist title in a query param, we need to find a playlist that
        # the video is a part of.  That requires finding the video, given it readable_id
        # or, to support old URLs, it's youtube_id.
        video = None
        playlist = None
        video_id = self.request.get('v')
        playlist_title = self.request_string('playlist', default="") or self.request_string('p', default="")
        path = self.request.path
        readable_id  = urllib.unquote(path.rpartition('/')[2])
        readable_id = re.sub('-+$', '', readable_id)  # remove any trailing dashes (see issue 1140)

        # If either the readable_id or playlist title is missing,
        # redirect to the canonical URL that contains them
        redirect_to_canonical_url = False
        if video_id: # Support for old links
            query = Video.all()
            query.filter('youtube_id =', video_id)
            video = query.get()

            if not video:
                raise MissingVideoException("Missing video w/ youtube id '%s'" % video_id)

            readable_id = video.readable_id
            playlist = video.first_playlist()

            if not playlist:
                raise MissingVideoException("Missing video w/ youtube id '%s'" % video_id)

            redirect_to_canonical_url = True

        if playlist_title is not None and len(playlist_title) > 0:
            query = Playlist.all().filter('title =', playlist_title)
            key_id = 0
            for p in query:
                if p.key().id() > key_id and not p.youtube_id.endswith('_player'):
                    playlist = p
                    key_id = p.key().id()

        # If a playlist_title wasn't specified or the specified playlist wasn't found
        # use the first playlist for the requested video.
        if playlist is None:
            # Get video by readable_id just to get the first playlist for the video
            video = Video.get_for_readable_id(readable_id)
            if video is None:
                raise MissingVideoException("Missing video '%s'" % readable_id)

            playlist = video.first_playlist()
            if not playlist:
                raise MissingVideoException("Missing video '%s'" % readable_id)

            redirect_to_canonical_url = True

        exid = self.request_string('exid', default=None)

        if redirect_to_canonical_url:
            qs = {'playlist': playlist.title}
            if exid:
                qs['exid'] = exid

            urlpath = "/video/%s" % urllib.quote(readable_id)
            url = urlparse.urlunparse(('', '', urlpath, '', urllib.urlencode(qs), ''))
            self.redirect(url, True)
            return

        # If we got here, we have a readable_id and a playlist_title, so we can display
        # the playlist and the video in it that has the readable_id.  Note that we don't
        # query the Video entities for one with the requested readable_id because in some
        # cases there are multiple Video objects in the datastore with the same readable_id
        # (e.g. there are 2 "Order of Operations" videos).

        videos = VideoPlaylist.get_cached_videos_for_playlist(playlist)
        previous_video = None
        next_video = None
        for v in videos:
            if v.readable_id == readable_id:
                v.selected = 'selected'
                video = v
            elif video is None:
                previous_video = v
            elif next_video is None:
                next_video = v

        if video is None:
            raise MissingVideoException("Missing video '%s'" % readable_id)

        if App.offline_mode:
            video_path = "/videos/" + get_mangled_playlist_name(playlist_title) + "/" + video.readable_id + ".flv"
        else:
            video_path = video.download_video_url()

        exercise = None
        exercise_video = video.get_related_exercise()
        if exercise_video and exercise_video.exercise:
            exercise = exercise_video.exercise.name

        if video.description == video.title:
            video.description = None

        user_video = UserVideo.get_for_video_and_user_data(video, UserData.current(), insert_if_missing=True)

        awarded_points = 0
        if user_video:
            awarded_points = user_video.points

        template_values = {
                            'playlist': playlist,
                            'video': video,
                            'videos': videos,
                            'video_path': video_path,
                            'video_points_base': consts.VIDEO_POINTS_BASE,
                            'exercise': exercise,
                            'previous_video': previous_video,
                            'next_video': next_video,
                            'selected_nav_link': 'watch',
                            'awarded_points': awarded_points,
                            'issue_labels': ('Component-Videos,Video-%s' % readable_id),
                        }
        template_values = qa.add_template_values(template_values, self.request)

        self.render_template('viewvideo.html', template_values)

class LogVideoProgress(request_handler.RequestHandler):

    # LogVideoProgress uses a GET request to solve the IE-behind-firewall
    # issue with occasionally stripped POST data.
    # See http://code.google.com/p/khanacademy/issues/detail?id=3098
    # and http://stackoverflow.com/questions/328281/why-content-length-0-in-post-requests
    def post(self):
        self.get()

    @create_phantom
    def get(self):
        user_data = UserData.current()
        video_points_total = 0
        points_total = 0

        if user_data:

            video = None
            key_str = self.request_string("video_key", default = "")

            if key_str:
                key = db.Key(key_str)
                app_id = os.environ['APPLICATION_ID']
                if key.app() != app_id:
                    new_key = db.Key.from_path(
                        key.kind(),
                        key.id() or key.name(),
                        _app=app_id)
                    logging.warning("Key '%s' had invalid app_id '%s'. Changed to new key '%s'", str(key), key.app(), str(new_key))
                    key = new_key
                video = db.get(key)

            if video:

                # Seconds watched is restricted by both the scrubber's position
                # and the amount of time spent on the video page
                # so we know how *much* of each video each student has watched
                seconds_watched = int(self.request_float("seconds_watched", default=0))
                last_second_watched = int(self.request_float("last_second_watched", default=0))

                user_video, video_log, video_points_total = VideoLog.add_entry(user_data, video, seconds_watched, last_second_watched)

        user_points_html = self.render_template_block_to_string(
            "user_points.html",
            "user_points_block",
            user_points(user_data)
        )

        json = simplejson.dumps({"user_points_html": user_points_html, "video_points": video_points_total}, ensure_ascii=False)
        self.response.out.write(json)

class PrintProblem(request_handler.RequestHandler):

    def get(self):

        exid = self.request.get('exid')
        problem_number = self.request.get('problem_number')

        template_values = {
                'App' : App,
                'arithmetic_template': 'arithmetic_print_template.html',
                'exid': exid,
                'extitle': exid.replace('_', ' ').capitalize(),
                'problem_number': self.request.get('problem_number')
                }

        self.render_template(exid + '.html', template_values)

class PrintExercise(request_handler.RequestHandler):

    def get(self):

        user_data = UserData.current()

        if user_data:
            exid = self.request.get('exid')
            key = self.request.get('key')
            problem_number = int(self.request.get('problem_number') or '0')
            num_problems = int(self.request.get('num_problems'))
            time_warp = self.request.get('time_warp')

            query = Exercise.all()
            query.filter('name =', exid)
            exercise = query.get()

            exercise_videos = None
            query = ExerciseVideo.all()
            query.filter('exercise =', exercise.key())
            exercise_videos = query.fetch(50)

            if not exid:
                exid = 'addition_1'

            user_exercise = user_data.get_or_insert_exercise(exercise)

            if not problem_number:
                problem_number = user_exercise.total_done+1
            proficient = False
            endangered = False
            reviewing = False

            template_values = {
                'arithmetic_template': 'arithmetic_print_template.html',
                'proficient': proficient,
                'endangered': endangered,
                'reviewing': reviewing,
                'key': user_exercise.key(),
                'exercise': exercise,
                'exid': exid,
                'expath': exid + '.html',
                'start_time': time.time(),
                'exercise_videos': exercise_videos,
                'extitle': exid.replace('_', ' ').capitalize(),
                'user_exercise': user_exercise,
                'time_warp': time_warp,
                'user_data': user_data,
                'num_problems': num_problems,
                'problem_numbers': range(problem_number, problem_number+num_problems),
                }

            self.render_template('print_template.html', template_values)

        else:

            self.redirect(util.create_login_url(self.request.uri))

class ReportIssue(request_handler.RequestHandler):

    def get(self):
        issue_type = self.request.get('type')
        self.write_response(issue_type, {'issue_labels': self.request.get('issue_labels'),})

    def write_response(self, issue_type, extra_template_values):
        user_agent = self.request.headers.get('User-Agent')
        if user_agent is None:
            user_agent = ''
        user_agent = user_agent.replace(',',';') # Commas delimit labels, so we don't want them
        template_values = {
            'referer': self.request.headers.get('Referer'),
            'user_agent': user_agent,
            }
        template_values.update(extra_template_values)
        page = 'reportissue_template.html'
        if issue_type == 'Defect':
            page = 'reportproblem.html'
        elif issue_type == 'Enhancement':
            page = 'makesuggestion.html'
        elif issue_type == 'New-Video':
            page = 'requestvideo.html'
        elif issue_type == 'Comment':
            page = 'makecomment.html'
        elif issue_type == 'Question':
            page = 'askquestion.html'

        self.render_template(page, template_values)

class ProvideFeedback(request_handler.RequestHandler):
    def get(self):
        self.render_template("provide_feedback.html", {})

class VideolessExercises(request_handler.RequestHandler):

    def get(self):
        query = Exercise.all().order('h_position')
        exercises = query.fetch(200)
        self.response.out.write('<html>')
        for exercise in exercises:
            query = ExerciseVideo.all()
            query.filter('exercise =', exercise.key())
            videos = query.fetch(200)
            if not videos:
                self.response.out.write('<P><A href="/exercises?exid=' + exercise.name + '">' + exercise.name + '</A>')

class ShowUnusedPlaylists(request_handler.RequestHandler):

    def get(self):

        playlists = Playlist.all()
        playlists_unused = []

        for playlist in playlists:
            if not playlist.title in all_topics_list:
                playlists_unused.append(playlist)

        self.response.out.write("Unused playlists:<br/><br/>")
        for playlist_unused in playlists_unused:
            self.response.out.write(" + " + playlist_unused.title + "<br/>")
        self.response.out.write("</br>Done")

class YoutubeVideoList(request_handler.RequestHandler):

    def get(self):
        for playlist_title in all_topics_list:
            query = Playlist.all()
            query.filter('title =', playlist_title)
            playlist = query.get()
            query = VideoPlaylist.all()
            query.filter('playlist =', playlist)
            query.filter('live_association = ', True)
            query.order('video_position')
            for pv in query.fetch(500):
                v = pv.video
                self.response.out.write('http://www.youtube.com/watch?v=' + v.youtube_id + '\n')

class ExerciseAndVideoEntityList(request_handler.RequestHandler):

    def get(self):
        self.response.out.write("Exercises:\n")

        for exercise in Exercise.all():
            self.response.out.write(str(exercise.key().id()) + "\t" + exercise.display_name + "\n")

        self.response.out.write("\n\nVideos:\n")
        for playlist_title in all_topics_list:
            query = Playlist.all()
            query.filter('title =', playlist_title)
            playlist = query.get()
            query = VideoPlaylist.all()
            query.filter('playlist =', playlist)
            query.filter('live_association = ', True)
            query.order('video_position')
            for pv in query.fetch(1000):
                v = pv.video
                self.response.out.write(str(v.key().id()) + "\t" + v.title + "\n")

class Crash(request_handler.RequestHandler):
    def get(self):
        if self.request_bool("capability_disabled", default=False):
            raise CapabilityDisabledError("Simulate scheduled GAE downtime")
        else:
            # Even Watson isn't perfect
            raise Exception("What is Toronto?")

class ReadOnlyDowntime(request_handler.RequestHandler):
    def get(self):
        raise CapabilityDisabledError("App Engine maintenance period")

    def post(self):
        return self.get()

class SendToLog(request_handler.RequestHandler):
    def post(self):
        message = self.request_string("message", default="")
        if message:
            logging.critical("Manually sent to log: %s" % message)

class MobileFullSite(request_handler.RequestHandler):
    def get(self):
        self.set_mobile_full_site_cookie(True)
        self.redirect("/")

class MobileSite(request_handler.RequestHandler):
    def get(self):
        self.set_mobile_full_site_cookie(False)
        self.redirect("/")

class ViewFAQ(request_handler.RequestHandler):
    def get(self):
        self.redirect("/about/faq", True)
        return

class ViewGetInvolved(request_handler.RequestHandler):
    def get(self):
        self.redirect("/contribute", True)

class ViewContribute(request_handler.RequestHandler):
    def get(self):

        if self.request_bool("convert", default=False):
            bingo("contribute_text")

        self.render_template('contribute.html', {"selected_nav_link": "contribute"})

class ViewCredits(request_handler.RequestHandler):
    def get(self):
        self.render_template('viewcredits.html', {"selected_nav_link": "contribute"})

class Donate(request_handler.RequestHandler):
    def get(self):
        self.redirect("/contribute", True)

class ViewTOS(request_handler.RequestHandler):
    def get(self):
        self.render_template('tos.html', {"selected_nav_link": "tos"})

class ViewPrivacyPolicy(request_handler.RequestHandler):
    def get(self):
        self.render_template('privacy-policy.html', {"selected_nav_link": "privacy-policy"})

class ViewDMCA(request_handler.RequestHandler):
    def get(self):
        self.render_template('dmca.html', {"selected_nav_link": "dmca"})

class ViewStore(request_handler.RequestHandler):
    def get(self):
        self.render_template('store.html', {})

class ViewHowToHelp(request_handler.RequestHandler):
    def get(self):
        self.redirect("/contribute", True)
        return

class ViewSAT(request_handler.RequestHandler):

    def get(self):
        playlist_title = "SAT Preparation"
        query = Playlist.all()
        query.filter('title =', playlist_title)
        playlist = query.get()
        query = VideoPlaylist.all()
        query.filter('playlist =', playlist)
        query.filter('live_association = ', True) #need to change this to true once I'm done with all of my hacks
        query.order('video_position')
        playlist_videos = query.fetch(500)

        template_values = {
                'videos': playlist_videos,
        }

        self.render_template('sat.html', template_values)

class ViewGMAT(request_handler.RequestHandler):

    def get(self):
        problem_solving = VideoPlaylist.get_query_for_playlist_title("GMAT: Problem Solving")
        data_sufficiency = VideoPlaylist.get_query_for_playlist_title("GMAT Data Sufficiency")
        template_values = {
                            'data_sufficiency': data_sufficiency,
                            'problem_solving': problem_solving,
        }

        self.render_template('gmat.html', template_values)


class RetargetFeedback(bulk_update.handler.UpdateKind):
    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""
        return db.GqlQuery('select __key__ from Feedback')

    def use_transaction(self):
        return False

    def update(self, feedback):
        orig_video = feedback.video()

        if orig_video == None or type(orig_video).__name__ != "Video":
            return False
        readable_id = orig_video.readable_id
        query = Video.all()
        query.filter('readable_id =', readable_id)
        # The database currently contains multiple Video objects for a particular
        # video.  Some are old.  Some are due to a YouTube sync where the youtube urls
        # changed and our code was producing youtube_ids that ended with '_player'.
        # This hack gets the most recent valid Video object.
        key_id = 0
        for v in query:
            if v.key().id() > key_id and not v.youtube_id.endswith('_player'):
                video = v
                key_id = v.key().id()
        # End of hack
        if video is not None and video.key() != orig_video.key():
            logging.info("Retargeting Feedback %s from Video %s to Video %s", feedback.key().id(), orig_video.key().id(), video.key().id())
            feedback.targets[0] = video.key()
            return True
        else:
            return False

class DeleteStaleVideoPlaylists(bulk_update.handler.UpdateKind):
    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""
        return db.GqlQuery('select __key__ from VideoPlaylist')

    def use_transaction(self):
        return False

    def update(self, video_playlist):
        if video_playlist.live_association == True:
            logging.debug("Keeping VideoPlaylist %s", video_playlist.key().id())
            return False
        logging.info("Deleting stale VideoPlaylist %s", video_playlist.key().id())
        video_playlist.delete()
        return False

class DeleteStaleVideos(bulk_update.handler.UpdateKind):
    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""
        return db.GqlQuery('select __key__ from Video')

    def use_transaction(self):
        return False

    def update(self, video):
        query = ExerciseVideo.all()
        query.filter('video =', video)
        referrer = query.get()
        if referrer is not None:
            logging.debug("Keeping Video %s.  It is still referenced by ExerciseVideo %s", video.key().id(), referrer.key().id())
            return False
        query = VideoPlaylist.all()
        query.filter('video =', video)
        referrer = query.get()
        if referrer is not None:
            logging.debug("Keeping Video %s.  It is still referenced by VideoPlaylist %s", video.key().id(), referrer.key().id())
            return False
        logging.info("Deleting stale Video %s", video.key().id())
        video.delete()
        return False


class DeleteStalePlaylists(bulk_update.handler.UpdateKind):
    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""
        return db.GqlQuery('select __key__ from Playlist')

    def use_transaction(self):
        return False

    def update(self, playlist):
        query = VideoPlaylist.all()
        query.filter('playlist =', playlist)
        referrer = query.get()
        if referrer is not None:
            logging.debug("Keeping Playlist %s.  It is still referenced by VideoPlaylist %s", playlist.key().id(), referrer.key().id())
            return False
        logging.info("Deleting stale Playlist %s", playlist.key().id())
        playlist.delete()
        return False


class FixVideoRef(bulk_update.handler.UpdateKind):
    def use_transaction(self):
        return False

    def update(self, entity):
        orig_video = entity.video

        if orig_video == None or type(orig_video).__name__ != "Video":
            return False
        readable_id = orig_video.readable_id
        query = Video.all()
        query.filter('readable_id =', readable_id)
        # The database currently contains multiple Video objects for a particular
        # video.  Some are old.  Some are due to a YouTube sync where the youtube urls
        # changed and our code was producing youtube_ids that ended with '_player'.
        # This hack gets the most recent valid Video object.
        key_id = 0
        for v in query:
            if v.key().id() > key_id and not v.youtube_id.endswith('_player'):
                video = v
                key_id = v.key().id()
        # End of hack
        if video is not None and video.key() != orig_video.key():
            logging.info("Retargeting %s %s from Video %s to Video %s", type(entity), entity.key().id(), orig_video.key().id(), video.key().id())
            entity.video = video
            return True
        else:
            return False

class FixPlaylistRef(bulk_update.handler.UpdateKind):
    def use_transaction(self):
        return False

    def update(self, entity):
        orig_playlist = entity.playlist

        if orig_playlist == None or type(orig_playlist).__name__ != "Playlist":
            return False
        youtube_id = orig_playlist.youtube_id
        query = Playlist.all()
        query.filter('youtube_id =', youtube_id)
        # The database currently contains multiple Playlist objects for a particular
        # playlist.  Some are old.
        # This hack gets the most recent valid Playlist object.
        key_id = 0
        for p in query:
            if p.key().id() > key_id:
                playlist = p
                key_id = p.key().id()
        # End of hack
        if playlist is not None and playlist.key() != orig_playlist.key():
            logging.info("Retargeting %s %s from Playlist %s to Playlist %s", type(entity), entity.key().id(), orig_playlist.key().id(), playlist.key().id())
            entity.playlist = playlist
            return True
        else:
            return False

class ChangeEmail(bulk_update.handler.UpdateKind):

    def get_email_params(self):
        old_email = self.request.get('old')
        new_email = self.request.get('new')
        prop = self.request.get('prop')
        if old_email is None or len(old_email) == 0:
            raise Exception("parameter 'old' is required")
        if new_email is None or len(new_email) == 0:
            new_email = old_email
        if prop is None or len(prop) == 0:
            prop = "user"
        return (old_email, new_email, prop)

    def get(self):
        (old_email, new_email, prop) = self.get_email_params()
        if new_email == old_email:
            return bulk_update.handler.UpdateKind.get(self)
        self.response.out.write("To prevent a CSRF attack from changing email addresses, you initiate an email address change from the browser. ")
        self.response.out.write("Instead, run the following from remote_api_shell.py.<pre>\n")
        self.response.out.write("import bulk_update.handler\n")
        self.response.out.write("bulk_update.handler.start_task('%s',{'kind':'%s', 'old':'%s', 'new':'%s'})\n"
                                % (self.request.path, self.request.get('kind'), old_email, new_email))
        self.response.out.write("</pre>and then check the logs in the admin console")


    def get_keys_query(self, kind):
        """Returns a keys-only query to get the keys of the entities to update"""

        (old_email, new_email, prop) = self.get_email_params()
        # When a user's personal Google account is replaced by their transitioned Google Apps account with the same email,
        # the Google user ID changes and the new User object's are not considered equal to the old User object's with the same
        # email, so querying the datastore for entities referring to users with the same email return nothing. However an inequality
        # query will return the relevant entities.
        gt_user = users.User(old_email[:-1] + chr(ord(old_email[-1])-1) + chr(127))
        lt_user = users.User(old_email + chr(0))
        return db.GqlQuery(('select __key__ from %s where %s > :1 and %s < :2' % (kind, prop, prop)), gt_user, lt_user)

    def use_transaction(self):
        return False

    def update(self, entity):
        (old_email, new_email, prop) = self.get_email_params()
        if getattr(entity, prop).email() != old_email:
            # This should never occur, but just in case, don't change or reput the entity.
            return False
        setattr(entity, prop, users.User(new_email))
        return True

class ViewArticle(request_handler.RequestHandler):

    def get(self):
        video = None
        path = self.request.path
        readable_id  = urllib.unquote(path.rpartition('/')[2])

        article_url = "http://money.cnn.com/2010/08/23/technology/sal_khan_academy.fortune/index.htm"
        if readable_id == "fortune":
            article_url = "http://money.cnn.com/2010/08/23/technology/sal_khan_academy.fortune/index.htm"

        template_values = {
                'article_url': article_url,
                'issue_labels': ('Component-Videos,Video-%s' % readable_id),
        }

        self.render_template("article.html", template_values)

class Login(request_handler.RequestHandler):
    def get(self):
        return self.post()

    def post(self):
        cont = self.request_string('continue', default = "/")
        direct = self.request_bool('direct', default = False)

        openid_identifier = self.request.get('openid_identifier')
        if openid_identifier is not None and len(openid_identifier) > 0:
            if App.accepts_openid:
                self.redirect(users.create_login_url(cont, federated_identity = openid_identifier))
                return
            self.redirect(users.create_login_url(cont))
            return

        if App.facebook_app_secret is None:
            self.redirect(users.create_login_url(cont))
            return
        template_values = {
                           'continue': cont,
                           'direct': direct
                           }
        self.render_template('login.html', template_values)

class MobileOAuthLogin(request_handler.RequestHandler):
    def get(self):
        self.render_template('login_mobile_oauth.html', {
            "oauth_map_id": self.request_string("oauth_map_id", default=""),
            "anointed": self.request_bool("an", default=False),
            "view": self.request_string("view", default="")
        })

class PostLogin(request_handler.RequestHandler):
    def get(self):
        cont = self.request_string('continue', default = "/")

        # Immediately after login we make sure this user has a UserData entity
        user_data = UserData.current()
        if user_data:

            # Update email address if it has changed
            current_google_user = users.get_current_user()
            if current_google_user and current_google_user.email() != user_data.email:
                user_data.user_email = current_google_user.email()
                user_data.put()

            # Update nickname if it has changed
            current_nickname = get_nickname_for(user_data)
            if user_data.user_nickname != current_nickname:
                user_data.user_nickname = current_nickname
                user_data.put()

            # Set developer to True if user is admin
            if not user_data.developer and users.is_current_user_admin():
                user_data.developer = True
                user_data.put()

            # If user is brand new and has 0 points, migrate data
            phantom_id = get_phantom_user_id_from_cookies()
            if phantom_id:
                phantom_data = UserData.get_from_db_key_email(phantom_id)

                # First make sure user has 0 points and phantom user has some activity
                if user_data.points == 0 and phantom_data and phantom_data.points > 0:

                    # Make sure user has no students
                    if not user_data.has_students():

                        # Clear all "login" notifications
                        UserNotifier.clear_all(phantom_data)

                        # Update phantom user_data to real user_data
                        phantom_data.user_id = user_data.user_id
                        phantom_data.current_user = user_data.current_user
                        phantom_data.user_email = user_data.user_email
                        phantom_data.user_nickname = user_data.user_nickname

                        if phantom_data.put():
                            # Phantom user was just transitioned to real user
                            user_counter.add(1)
                            user_data.delete()

                        cont = "/newaccount?continue=%s" % cont
        else:

            # If nobody is logged in, clear any expired Facebook cookie that may be hanging around.
            self.delete_cookie("fbs_" + App.facebook_app_id)

            logging.critical("Missing UserData during PostLogin, with id: %s, cookies: (%s), google user: %s" % (
                    util.get_current_user_id(), os.environ.get('HTTP_COOKIE', ''), users.get_current_user()
                )
            )

        # Always delete phantom user cookies on login
        self.delete_cookie('ureg_id')

        self.redirect(cont)

class Logout(request_handler.RequestHandler):
    def get(self):
        self.delete_cookie('ureg_id')
        self.redirect(users.create_logout_url(self.request_string("continue", default="/")))

class Search(request_handler.RequestHandler):

    def get(self):
        query = self.request.get('page_search_query')
        template_values = { 'page_search_query': query }
        query = query.strip()
        query_too_short = None
        if len(query) < search.SEARCH_PHRASE_MIN_LENGTH:
            if len(query) > 0:
                template_values.update({'query_too_short': search.SEARCH_PHRASE_MIN_LENGTH})
            self.render_template("searchresults.html", template_values)
            return
        searched_phrases = []
        playlists = Playlist.search(query, limit=50, searched_phrases_out=searched_phrases)
        videos = Video.search(query, limit=50, searched_phrases_out=searched_phrases)
        template_values.update({
                           'playlists': playlists,
                           'videos': videos,
                           'searched_phrases': searched_phrases
                           })
        self.render_template("searchresults.html", template_values)

class RedirectToJobvite(request_handler.RequestHandler):
    def get(self):
        self.redirect("http://hire.jobvite.com/CompanyJobs/Careers.aspx?k=JobListing&c=qd69Vfw7")

class RedirectToToolkit(request_handler.RequestHandler):
    def get(self):
        self.redirect("https://sites.google.com/a/khanacademy.org/schools/")

class PermanentRedirectToHome(request_handler.RequestHandler):
    def get(self):

        redirect_target = "/"
        relative_path = self.request.path.rpartition('/')[2].lower()

        # Permanently redirect old JSP version of the site to home
        # or, in the case of some special targets, to their appropriate new URL
        dict_redirects = {
            "sat.jsp": "/sat",
            "gmat.jsp": "/gmat",
        }

        if dict_redirects.has_key(relative_path):
            redirect_target = dict_redirects[relative_path]

        self.redirect(redirect_target, True)

class ViewRenderTemplate(request_handler.RequestHandler):
    def get(self):
        template = self.request_string('template', 'templatetest.html')
        self.render_template(template, { 'user_data': UserData.current() })

class ServeUserVideoCss(request_handler.RequestHandler):
    def get(self):
        user_data = UserData.current()
        if user_data == None:
            return

        user_video_css = models.UserVideoCss.get_for_user_data(user_data)
        self.response.headers['Content-Type'] = 'text/css'

        if user_video_css.version == user_data.uservideocss_version:
            # Don't cache if there's a version mismatch and update isn't finished
            self.response.headers['Cache-Control'] = 'public,max-age=1000000'

        self.response.out.write(user_video_css.video_css)

class RealtimeEntityCount(request_handler.RequestHandler):
    def get(self):
        if not App.is_dev_server:
            raise Exception("Only works on dev servers.")
        default_kinds = 'Exercise'
        kinds = self.request_string("kinds", default_kinds).split(',')
        for kind in kinds:
            count = getattr(models, kind).all().count(10000)
            self.response.out.write("%s: %d<br>" % (kind, count))

def main():

    application = webapp.WSGIApplication([
        ('/', homepage.ViewHomePage),
        ('/about', util_about.ViewAbout),
        ('/about/blog', blog.ViewBlog),
        ('/about/blog/.*', blog.ViewBlogPost),
        ('/about/the-team', util_about.ViewAboutTheTeam),
        ('/about/getting-started', util_about.ViewGettingStarted),
        ('/about/tos', ViewTOS ),
        ('/about/privacy-policy', ViewPrivacyPolicy ),
        ('/about/dmca', ViewDMCA ),
        ('/contribute', ViewContribute ),
        ('/contribute/credits', ViewCredits ),
        ('/frequently-asked-questions', util_about.ViewFAQ),
        ('/about/faq', util_about.ViewFAQ),
        ('/downloads', util_about.ViewDownloads),
        ('/about/downloads', util_about.ViewDownloads),
        ('/getinvolved', ViewGetInvolved),
        ('/donate', Donate),
        ('/exercisedashboard', exercises.ViewAllExercises),
        ('/library_content', library.GenerateLibraryContent),
        ('/youtube_list', YoutubeVideoList),
        ('/exerciseandvideoentitylist', ExerciseAndVideoEntityList),
        ('/exercises', exercises.ViewExercise),
        ('/khan-exercises/exercises/.*', exercises.RawExercise),
        ('/printexercise', PrintExercise),
        ('/printproblem', PrintProblem),
        ('/viewexercisesonmap', exercises.ViewAllExercises),
        ('/editexercise', exercises.EditExercise),
        ('/updateexercise', exercises.UpdateExercise),
        ('/moveexercisemapnode', exercises.MoveMapNode),
        ('/admin94040', exercises.ExerciseAdmin),
        ('/videoless', VideolessExercises),
        ('/video/.*', ViewVideo),
        ('/v/.*', ViewVideo),
        ('/video', ViewVideo), # Backwards URL compatibility
        ('/logvideoprogress', LogVideoProgress),
        ('/sat', ViewSAT),
        ('/gmat', ViewGMAT),
        ('/store', ViewStore),
        ('/reportissue', ReportIssue),
        ('/provide-feedback', ProvideFeedback),
        ('/search', Search),
        ('/autocomplete', autocomplete.Autocomplete),
        ('/savemapcoords', knowledgemap.SaveMapCoords),
        ('/saveexpandedallexercises', knowledgemap.SaveExpandedAllExercises),
        ('/showunusedplaylists', ShowUnusedPlaylists),
        ('/crash', Crash),

        ('/mobilefullsite', MobileFullSite),
        ('/mobilesite', MobileSite),

        ('/admin/reput', bulk_update.handler.UpdateKind),
        ('/admin/retargetfeedback', RetargetFeedback),
        ('/admin/fixvideoref', FixVideoRef),
        ('/admin/deletestalevideoplaylists', DeleteStaleVideoPlaylists),
        ('/admin/deletestalevideos', DeleteStaleVideos),
        ('/admin/fixplaylistref', FixPlaylistRef),
        ('/admin/deletestaleplaylists', DeleteStalePlaylists),
        ('/admin/startnewbadgemapreduce', util_badges.StartNewBadgeMapReduce),
        ('/admin/badgestatistics', util_badges.BadgeStatistics),
        ('/admin/startnewexercisestatisticsmapreduce', exercise_statistics.StartNewExerciseStatisticsMapReduce),
        ('/admin/startnewvotemapreduce', voting.StartNewVoteMapReduce),
        ('/admin/backfill', backfill.StartNewBackfillMapReduce),
        ('/admin/feedbackflagupdate', qa.StartNewFlagUpdateMapReduce),
        ('/admin/dailyactivitylog', activity_summary.StartNewDailyActivityLogMapReduce),
        ('/admin/youtubesync.*', youtube_sync.YouTubeSync),
        ('/admin/changeemail', ChangeEmail),
        ('/admin/rendertemplate', ViewRenderTemplate),
        ('/admin/realtimeentitycount', RealtimeEntityCount),


        ('/devadmin/emailchange', devpanel.Email),
        ('/devadmin/managedevs', devpanel.Manage),
        ('/devadmin/managecoworkers', devpanel.ManageCoworkers),

        ('/coaches', coaches.ViewCoaches),
        ('/students', coaches.ViewStudents),
        ('/registercoach', coaches.RegisterCoach),
        ('/unregistercoach', coaches.UnregisterCoach),
        ('/unregisterstudent', coaches.UnregisterStudent),
        ('/requeststudent', coaches.RequestStudent),
        ('/acceptcoach', coaches.AcceptCoach),

        ('/createstudentlist', coaches.CreateStudentList),
        ('/deletestudentlist', coaches.DeleteStudentList),
        ('/removestudentfromlist', coaches.RemoveStudentFromList),
        ('/addstudenttolist', coaches.AddStudentToList),

        ('/individualreport', coaches.ViewIndividualReport),
        ('/progresschart', coaches.ViewProgressChart),
        ('/sharedpoints', coaches.ViewSharedPoints),
        ('/classreport', coaches.ViewClassReport),
        ('/classtime', coaches.ViewClassTime),
        ('/charts', coaches.ViewCharts),

        ('/mailing-lists/subscribe', util_mailing_lists.Subscribe),

        ('/profile/graph/activity', util_profile.ActivityGraph),
        ('/profile/graph/focus', util_profile.FocusGraph),
        ('/profile/graph/exercisesovertime', util_profile.ExercisesOverTimeGraph),
        ('/profile/graph/exerciseproblems', util_profile.ExerciseProblemsGraph),
        ('/profile/graph/exerciseprogress', util_profile.ExerciseProgressGraph),
        ('/profile', util_profile.ViewProfile),

        ('/profile/graph/classexercisesovertime', util_profile.ClassExercisesOverTimeGraph),
        ('/profile/graph/classprogressreport', util_profile.ClassProgressReportGraph),
        ('/profile/graph/classenergypointsperminute', util_profile.ClassEnergyPointsPerMinuteGraph),
        ('/profile/graph/classtime', util_profile.ClassTimeGraph),
        ('/class_profile', util_profile.ViewClassProfile),

        ('/press/.*', ViewArticle),
        ('/login', Login),
        ('/login/mobileoauth', MobileOAuthLogin),
        ('/postlogin', PostLogin),
        ('/logout', Logout),

        ('/api-apps/register', oauth_apps.Register),

        # These are dangerous, should be able to clean things manually from the remote python shell

        ('/deletevideoplaylists', DeleteVideoPlaylists),
        ('/killliveassociations', KillLiveAssociations),

        # Below are all discussion related pages
        ('/discussion/addcomment', comments.AddComment),
        ('/discussion/pagecomments', comments.PageComments),

        ('/discussion/addquestion', qa.AddQuestion),
        ('/discussion/expandquestion', qa.ExpandQuestion),
        ('/discussion/addanswer', qa.AddAnswer),
        ('/discussion/editentity', qa.EditEntity),
        ('/discussion/answers', qa.Answers),
        ('/discussion/pagequestions', qa.PageQuestions),
        ('/discussion/clearflags', qa.ClearFlags),
        ('/discussion/flagentity', qa.FlagEntity),
        ('/discussion/voteentity', voting.VoteEntity),
        ('/discussion/updateqasort', voting.UpdateQASort),
        ('/admin/discussion/finishvoteentity', voting.FinishVoteEntity),
        ('/discussion/deleteentity', qa.DeleteEntity),
        ('/discussion/changeentitytype', qa.ChangeEntityType),
        ('/discussion/videofeedbacknotificationlist', notification.VideoFeedbackNotificationList),
        ('/discussion/videofeedbacknotificationfeed', notification.VideoFeedbackNotificationFeed),
        ('/discussion/moderatorlist', qa.ModeratorList),
        ('/discussion/flaggedfeedback', qa.FlaggedFeedback),

        ('/githubpost', github.NewPost),
        ('/githubcomment', github.NewComment),

        ('/toolkit', RedirectToToolkit),

        ('/paypal/ipn', paypal.IPN),

        ('/badges/view', util_badges.ViewBadges),
        ('/badges/custom/create', custom_badges.CreateCustomBadge),
        ('/badges/custom/award', custom_badges.AwardCustomBadge),

        ('/notifierclose', util_notify.ToggleNotify),
        ('/newaccount', Clone),

        ('/jobs', RedirectToJobvite),
        ('/jobs/.*', RedirectToJobvite),

        ('/dashboard', dashboard.Dashboard),
        ('/entityboard', dashboard.Entityboard),
        ('/admin/dashboard/record_statistics', dashboard.RecordStatistics),
        ('/admin/entitycounts', dashboard.EntityCounts),

        ('/sendtolog', SendToLog),

        ('/user_video_css', ServeUserVideoCss),

        ('/admin/exercisestats/collectfancyexercisestatistics', exercisestats.CollectFancyExerciseStatistics),
        ('/exercisestats/report', exercisestats.report.Test),
        ('/exercisestats/exerciseovertime', exercisestats.report_json.ExerciseOverTimeGraph),
        ('/exercisestats/geckoboardexerciseredirect', exercisestats.report_json.GeckoboardExerciseRedirect),
        ('/exercisestats/exercisestatsmap', exercisestats.report_json.ExerciseStatsMapGraph),
        ('/exercisestats/exerciseslastauthorcounter', exercisestats.report_json.ExercisesLastAuthorCounter),
        ('/exercisestats/exercisenumbertrivia', exercisestats.report_json.ExerciseNumberTrivia),
        ('/exercisestats/userlocationsmap', exercisestats.report_json.UserLocationsMap),
        ('/exercisestats/exercisescreatedhistogram', exercisestats.report_json.ExercisesCreatedHistogram),
        ('/exercisestats/admin/setallexercisecreationdates', exercisestats.report_json.SetAllExerciseCreationDates),

        # Redirect any links to old JSP version
        ('/.*\.jsp', PermanentRedirectToHome),
        ('/index\.html', PermanentRedirectToHome),

        ('/_ah/warmup.*', warmup.Warmup),

        ], debug=True)

    application = profiler.ProfilerWSGIMiddleware(application)
    application = GAEBingoWSGIMiddleware(application)
    application = request_cache.RequestCacheMiddleware(application)

    run_wsgi_app(application)

if __name__ == '__main__':
    main()
