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
            currdata.user_id = newdata.user_id
            currdata.put()
            if newdata: #delete old account 
                newdata.delete()

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
