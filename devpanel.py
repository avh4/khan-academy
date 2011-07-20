import os, logging

from google.appengine.ext import db
from google.appengine.api import users
import util
from app import App
import models
from models import UserData
import request_handler
import util
import itertools
            
            
class Email(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin() and not UserData.current().developer:
            self.redirect(users.create_login_url(self.request.uri))
            return
            
        current_email = self.request.get('curremail') #email that is currently used 
        new_email = self.request.get('newemail') #email the user wants to change to
        swap = self.request.get('swap') #Are we changing emails?
        

        currdata = UserData.get_from_user_input_email(current_email)
        newdata = UserData.get_from_user_input_email(new_email)
        
        if swap:
            currdata.current_user = users.User(new_email)
            currdata.put()
            # newdata.delete()
        
        template_values = {'App' : App, 'curremail': current_email, 'newemail':  new_email, 'currdata': currdata, 'newdata': newdata, "properties": UserData.properties()}

        self.render_template('devemailpanel.html', template_values)
        
        
class Manage(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin():
            self.redirect(users.create_login_url(self.request.uri))
            return
   
        add_dev = self.request.get('adddev', None) #email that is currently used 
        remove_dev = self.request.get('removedev', None) #email the user wants to change to     
    
        if add_dev:
            dev = UserData.get_from_user_input_email(add_dev)
            dev.developer = True
            dev.put()
    
        if remove_dev:
            dev = UserData.get_from_user_input_email(remove_dev)
            dev.developer = False
            dev.put()
   
        developers = UserData.all()
        developers.filter('developer = ', True).fetch(1000)
        template_values = {'App' : App,  "developers": developers}

        self.render_template('managedevs.html', template_values) 
        