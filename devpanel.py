import os, logging

from google.appengine.ext import db
from google.appengine.api import users
import util
from app import App
import models
from models import UserData
import request_handler
import user_util
import itertools


class Email(request_handler.RequestHandler):

    @user_util.developer_only
    def get(self):
        current_email = self.request.get('curremail') #email that is currently used 
        new_email = self.request.get('newemail') #email the user wants to change to
        swap = self.request.get('swap') #Are we changing emails?
        

        currdata = UserData.get_from_user_email(current_email)
        newdata = UserData.get_from_user_email(new_email)
        
        if swap and currdata: #are we swapping? make sure account exists
            currdata.current_user = users.User(new_email)
            currdata.user_email = new_email
            currdata.user_id = new_data.user_id
            currdata.put()
            if newdata: #delete old account 
                newdata.delete()

        template_values = {'App' : App, 'curremail': current_email, 'newemail':  new_email, 'currdata': currdata, 'newdata': newdata, "properties": UserData.properties()}

        self.render_template('devemailpanel.html', template_values)
        
        
class Manage(request_handler.RequestHandler):

    @user_util.admin_only # only admins may add devs, devs cannot add devs
    def get(self):
        errormessage = ""
        add_dev = self.request.get('adddev', None) #email that is currently used 
        remove_dev = self.request.get('removedev', None) #email the user wants to change to     
        if add_dev and not UserData.get_from_user_email(add_dev):
            errormessage = "You can't add a user that doesn't exist!"
        
        if remove_dev and not UserData.get_from_user_email(remove_dev):
            errormessage = "You can't remove a user that doesn't exist!"
            
        
        if add_dev and errormessage == "":
            dev = UserData.get_from_user_email(add_dev)
            if dev.developer == True:
                errormessage = "%s is already flagged as a developer!" % add_dev
            else:
                dev.developer = True
                dev.put()
    
        if remove_dev and errormessage == "":
            dev = UserData.get_from_user_email(remove_dev)
            if dev.developer == True:
                dev.developer = False
                dev.put()
            else:
                errormessage = "%s is not a developer to begin with" % remove_dev
   
        developers = UserData.all()
        developers.filter('developer = ', True).fetch(1000)
        template_values = {'App' : App,  "developers": developers, "errormessage":errormessage}

        self.render_template('managedevs.html', template_values) 
        