import os, logging

from google.appengine.ext import db
from google.appengine.api import users
import util
from app import App
from models import UserData
import request_handler
import util
import itertools
            
            
class Email(request_handler.RequestHandler):

    def get(self): #devs or admins may change emails
        if not UserData.current() or (not users.is_current_user_admin() and not UserData.current().developer):
            self.redirect(users.create_login_url(self.request.uri))
            return
            
        current_email = self.request.get('curremail') #email that is currently used 
        new_email = self.request.get('newemail') #email the user wants to change to
        swap = self.request.get('swap') #Are we changing emails?
        

        currdata = UserData.get_from_user_input_email(current_email)
        newdata = UserData.get_from_user_input_email(new_email)
        
        if swap and currdata: #are we swapping? make sure account exists
            currdata.current_user = users.User(new_email)
            currdata.put()
            if newdata: #delete old account 
                newdata.delete()

        template_values = {'App' : App, 'curremail': current_email, 'newemail':  new_email, 'currdata': currdata, 'newdata': newdata, "properties": UserData.properties()}

        self.render_template('devemailpanel.html', template_values)
        
        
class Manage(request_handler.RequestHandler):

    def get(self):
        if not users.is_current_user_admin(): #Only admins may add devs, devs cannot add devs.
            self.redirect(users.create_login_url(self.request.uri))
            return
        errormessage = ""
        add_dev = self.request.get('adddev', None) #email that is currently used 
        remove_dev = self.request.get('removedev', None) #email the user wants to change to     
        if add_dev and not UserData.get_from_user_input_email(add_dev):
            errormessage = "You can't add a user that doesn't exist!"
        
        if remove_dev and not UserData.get_from_user_input_email(remove_dev):
            errormessage = "You can't remove a user that doesn't exist!"
            
        
        if add_dev and errormessage == "":
            dev = UserData.get_from_user_input_email(add_dev)
            if dev.developer == True:
                errormessage = "%s is already flagged as a developer!" % add_dev
            else:
                dev.developer = True
                dev.put()
    
        if remove_dev and errormessage == "":
            dev = UserData.get_from_user_input_email(remove_dev)
            if dev.developer == True:
                errormessage = "%s is not a developer to begin with" % remove_dev
            else:
                dev.developer = False
                dev.put()
   
        developers = UserData.all()
        developers.filter('developer = ', True).fetch(1000)
        template_values = {'App' : App,  "developers": developers, "errormessage":errormessage}

        self.render_template('managedevs.html', template_values) 
        
