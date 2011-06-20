import datetime
import sys

from google.appengine.api import users
from google.appengine.api import taskqueue
from mapreduce import control
from mapreduce import operation as op

import util
import models
import notifications

import layer_cache
import request_handler

import logging

def update(user,user_data,user_exercise,threshold = False):
    numquest = None
    if user_exercise != None:
        numquest = user_exercise.total_done
    numbadge = user_data.badges
    numpoint = user_data.points
    #numprof = proficient_exercises

    # Every 20 questions
    if numquest != None and numquest % 20 == 0:
        notifications.UserLoginNotifier.push_for_user(user,"You've answered "+str(numquest)+" questions so far! Login or register to save your progress")
    #Proficiency
    #if
    #    notifications.UserLoginNotifier.push_for_user(user,"You're proficient in yet another subject, "+prof+". Login or register to save your progress")
    #First Badge
    # if
    #     notifications.UserLoginNotifier.push_for_user(user,"Congrats on your first badge! You should login or register to save your progress")
    # #Every 5 badges
    # if
    #     notifications.UserLoginNotifier.push_for_user(user,"You've earned "+numbadge+" badges so far. Have you considered logging in or registering so you don't lose your progress?")
    #Every 2.5k points
    if threshold:
        numpoint = 2500*(numpoint/2500)+2500
        notifications.UserLoginNotifier.push_for_user(user,"You've earned over "+str(numpoint)+ " points! If you want to keep them, you'll need to login or register.")

    #notifications.UserLoginNotifier.push_for_user(user,"You need to login!!!")



