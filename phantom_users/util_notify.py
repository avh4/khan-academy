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

def update(user,user_data,user_exercise,threshold = False, isProf = False):
    if not phantom_util.is_phantom_email(user.email()):
        return False

    numquest = None
    numbadge = None
    numpoint = None
    # user_badges = memcache.get(badges.UserBadgeNotifier.key_for_user(user)) or []
    if user_exercise != None:
        numquest = user_exercise.total_done
        prof = str(user_exercise.exercise)
        prof = string.replace(prof,"_"," ")
        prof = prof.title() # clean up 'subtraction_1' to 'Subtraction 1', etc
    if user_data != None:
        numbadge = user_data.badges
        user_badges = memcache.get(badges.UserBadgeNotifier.key_for_user(user)) or [] #Only allow badge notifications when earned
        numpoint = user_data.points
    #numprof = proficient_exercises
    
    # Every 20 questions
    if numquest != None and numquest % 20 == 0:
        notifications.UserLoginNotifier.push_for_user(user,"You've answered "+str(numquest)+" questions so far! <a href='#'>Login</a> or <a href='#'>register</a> to save your progress")
    #Proficiency
    if isProf:
        notifications.UserLoginNotifier.push_for_user(user,"You're proficient in "+str(prof)+". <a href='#'>Login</a> or <a href='#'>register</a> to save your progress")
    #First Badge
    if numbadge != None and len(numbadge) == 1 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"Congrats on your first <a href='/profile'>badge</a>! You should <a href='#'>login</a> or <a href='#'>register</a> to save your progress")
    #Every 5 badges
    if numbadge != None and len(numbadge) % 5 == 0 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"You've earned <a href='/profile'>"+str(len(numbadge))+" badges</a> so far. Have you considered <a href='#'>logging</a> in or <a href='#'>registering</a> so you don't lose your progress?")
    #Every 2.5k points
    if numpoint != None and threshold:
        numpoint = 2500*(numpoint/2500)+2500
        notifications.UserLoginNotifier.push_for_user(user,"You've earned over <a href='/profile'>"+str(numpoint)+ " points</a>! If you want to keep them, you'll need to <a href='#'>login</a> or <a href='#'>register</a>.")

    #notifications.UserLoginNotifier.push_for_user(user,"You need to login!!!")

#Toggle Notify allows the user to close the notification bar (by deleting the memcache) until a new notification occurs. 
class ToggleNotify(request_handler.RequestHandler):
    def post(self):
        user = util.get_current_user(allow_phantoms=True)

        if user:
            memcache.delete(UserLoginNotifier.key_for_user(user))
