import datetime
import sys
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.api import taskqueue
from mapreduce import control
from mapreduce import operation as op

import util
import models
import notifications
from notifications import UserLoginNotifier
import phantom_util
import layer_cache
import request_handler
from badges import badges
import logging
import string

def update(user_data,user_exercise,threshold = False, isProf = False):
    if user_data == None:
        return False
    user = user_data.user
    if not phantom_util.is_phantom_email(user.email()):
        return False

    numquest = None
    numbadge = None
    numpoint = None

    if user_exercise != None:
        numquest = user_exercise.total_done
        prof = str(user_exercise.exercise)
    
    
    numbadge = user_data.badges
    user_badges = memcache.get(badges.UserBadgeNotifier.key_for_user(user)) or [] #Only allow badge notifications when earned
    numpoint = user_data.points
    
    #numprof = proficient_exercises
    
    # Every 10 questions
    if numquest != None and numquest % 10 == 0:
        notifications.UserLoginNotifier.push_for_user(user,"You've answered "+str(numquest)+" questions so far! <span class='notification-bar-login'><a href='#'>Login</a> or <a href='#'>register</a></span> to save your progress")
    #Proficiency
    if isProf:
        notifications.UserLoginNotifier.push_for_user(user,"You're proficient in "+str(prof)+". <span class='notification-bar-login'><a href='#'>Login</a> or <a href='#'>register</a></span> to save your progress")
    #First Badge
    if numbadge != None and len(numbadge) == 1 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"Congrats on your first <a href='/profile'>badge</a>! You should <span class='notification-bar-login'><a href='#'>login</a> or <a href='#'>register</a></span> to save your progress")
    #Every 5 badges
    if numbadge != None and len(numbadge) % 5 == 0 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"You've earned <a href='/profile'>"+str(len(numbadge))+" badges</a> so far. Have you considered <span class='notification-bar-login'><a href='#'>logging</a></span> in or <a href='#'>registering</a> so you don't lose your progress?")
    #Every 2.5k points
    if numpoint != None and threshold:
        numpoint = 2500*(numpoint/2500)+2500
        notifications.UserLoginNotifier.push_for_user(user,"You've earned over <a href='/profile'>"+str(numpoint)+ " points</a>! If you want to keep them, you'll need to <span class='notification-bar-login'><a href='#'>login</a> or <a href='#'>register</a></span>.")

    #notifications.UserLoginNotifier.push_for_user(user,"You need to login!!!")


#Toggle Notify allows the user to close the notification bar (by deleting the memcache) until a new notification occurs. 
class ToggleNotify(request_handler.RequestHandler):
    def post(self):
        user = util.get_current_user()

        if user:
            memcache.delete(UserLoginNotifier.key_for_user(user))
