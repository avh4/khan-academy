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


def update(user,user_data,user_exercise,threshold = False, isProf = False):
    if not phantom_util.is_phantom_email(user.email()):
        return False

    numquest = None
    numbadge = None
    numpoint = None
    # user_badges = memcache.get(badges.UserBadgeNotifier.key_for_user(user)) or []
    if user_exercise != None:
        numquest = user_exercise.total_done
    if user_data != None:
        numbadge = user_data.badges
        user_badges = memcache.get(badges.UserBadgeNotifier.key_for_user(user)) or [] #Only allow badge notifications when earned
        numpoint = user_data.points
    #numprof = proficient_exercises
    
    # Every 20 questions
    if numquest != None and numquest % 20 == 0:
        notifications.UserLoginNotifier.push_for_user(user,"You've answered "+str(numquest)+" questions so far! Login or register to save your progress")
    #Proficiency
    if isProf:
        notifications.UserLoginNotifier.push_for_user(user,"You're proficient in "+str(user_exercise.exercise)+". Login or register to save your progress")
    #First Badge
    if numbadge != None and len(numbadge) == 1 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"Congrats on your first badge! You should login or register to save your progress")
    #Every 5 badges
    if numbadge != None and len(numbadge) % 5 == 0 and (len(user_badges) > 0):
        notifications.UserLoginNotifier.push_for_user(user,"You've earned "+str(len(numbadge))+" badges so far. Have you considered logging in or registering so you don't lose your progress?")
    #Every 2.5k points
    if numpoint != None and threshold:
        numpoint = 2500*(numpoint/2500)+2500
        notifications.UserLoginNotifier.push_for_user(user,"You've earned over "+str(numpoint)+ " points! If you want to keep them, you'll need to login or register.")

    #notifications.UserLoginNotifier.push_for_user(user,"You need to login!!!")


class ToggleNotify(request_handler.RequestHandler):
    def post(self):
        user = util.get_current_user(allow_phantoms=True)

        if user:
            memcache.delete(UserLoginNotifier.key_for_user(user))
