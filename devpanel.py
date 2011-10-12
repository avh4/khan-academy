import os, logging

from google.appengine.ext import db
from google.appengine.api import users
import util
from app import App
from models import UserData
import request_handler
import user_util
import itertools
from api.auth.xsrf import ensure_xsrf_cookie

import gdata.youtube
import gdata.youtube.data
import gdata.youtube.service
import urllib
import urllib2
import csv
from xml.etree import ElementTree as ET

class Email(request_handler.RequestHandler):

    @user_util.developer_only
    @ensure_xsrf_cookie
    def get(self):
        current_email = self.request.get('curremail') #email that is currently used 
        new_email = self.request.get('newemail') #email the user wants to change to
        swap = self.request.get('swap') #Are we changing emails?
        

        currdata = UserData.get_from_user_input_email(current_email)
        newdata = UserData.get_from_user_input_email(new_email)
        
        if swap and currdata: #are we swapping? make sure account exists
            currdata.current_user = users.User(new_email)
            currdata.user_email = new_email
            if newdata: #delete old account 
                currdata.user_id = newdata.user_id
                newdata.delete()
            currdata.put()

        template_values = {'App' : App, 'curremail': current_email, 'newemail':  new_email, 'currdata': currdata, 'newdata': newdata, "properties": UserData.properties()}

        self.render_jinja2_template('devemailpanel.html', template_values)
        
class Manage(request_handler.RequestHandler):

    @user_util.admin_only # only admins may add devs, devs cannot add devs
    @ensure_xsrf_cookie
    def get(self):
        developers = UserData.all()
        developers.filter('developer = ', True).fetch(1000)
        template_values = { "developers": developers }

        self.render_jinja2_template('managedevs.html', template_values) 
        
class ManageCoworkers(request_handler.RequestHandler):

    @user_util.developer_only
    @ensure_xsrf_cookie
    def get(self):

        user_data_coach = self.request_user_data("coach_email")
        user_data_coworkers = []

        if user_data_coach:
            user_data_coworkers = user_data_coach.get_coworkers_data()

        template_values = {
            "user_data_coach": user_data_coach,
            "user_data_coworkers": user_data_coworkers
        }

        self.render_jinja2_template("managecoworkers.html", template_values)
        
class CommonCore(request_handler.RequestHandler):
    
    @user_util.developer_only
    @ensure_xsrf_cookie
    def get(self):
        
        cc_videos = []
        auth_sub_url = ""
        youtube_account = ""
        cc_file = "common_core/"
        authsub_next = ""
        is_test = True # Change to False in production
        
        if is_test: 
            youtube_account = "khanacademyschools"
            cc_file += "test_data.csv"
            auth_sub_next = "http://localhost:8080/devadmin/commoncore"
        else:
            youtube_account = "khanacademy"
            cc_file += "cc_data.csv"
            auth_sub_next = "http://khanacademy.org/devadmin/commoncore"
        
        token = self.request_string("token")
        
        if token: # AuthSub token from YouTube API - load and tag videos            
            
            yt_service = gdata.youtube.service.YouTubeService()
            yt_service.SetAuthSubToken(token)
            yt_service.UpgradeToSessionToken()
            yt_service.developer_key = 'AI39si6eFsAasPBlI_xQLee6-Ii70lrEhGAXn_ryCSWQdMP8xW67wkawIjDYI_XieWc0FsdsH5HMPPpvenAtaEl5fCLmHX8A5w'
            
            f = open(cc_file, 'U')
            reader = csv.DictReader(f, dialect='excel')
            
            for record in reader:
                entry = yt_service.GetYouTubeVideoEntry(video_id=record["youtube_id"])
                
                video_url = "https://gdata.youtube.com/feeds/api/users/"+ youtube_account + "/uploads/" + record["youtube_id"]
                
                if entry.media.keywords.text:
                    keywords = entry.media.keywords.text
                else:
                    keywords = ""

                entry.media.keywords.text = keywords + "," + record["keyword"]

                updated_entry = yt_service.UpdateVideoEntry(entry, video_url)
                
                if not updated_entry:
                        logging.warning("***Video NOT updated*** Title: " + record["title"] + ", ID: " + record["youtube_id"])
                
                cc_videos.append(record)
            f.close() 
        
        else: # Get YouTube AuthSub token
            
            params = {
                'next': auth_sub_next,
                'scope': "http://gdata.youtube.com", 
                'session': "1", 
                'secure': "0"
            }
            
            base_url = "https://www.google.com/accounts/AuthSubRequest?"
            auth_sub_url = base_url + urllib.urlencode(params)
                        
        template_values = {
            "token" : token,
            "auth_sub_url" : auth_sub_url,
            "cc_videos" : cc_videos,
        }
        
        self.render_jinja2_template("commoncore.html", template_values)