import os
import datetime
import math
import urllib
import logging
import request_cache
import layer_cache

from google.appengine.api import users
from django.template.defaultfilters import pluralize
from asynctools import AsyncMultiTask, QueryTask

from models import UserData
from app import App
import nicknames
import facebook_util

@request_cache.cache()
def get_current_user():
    user = users.get_current_user()
    if user is not None and user.user_id() is not None:
        # It's a Google account, so get the first user to join with that email address.
        return get_first_matching_user(user)
        
    if not user:
        user = facebook_util.get_current_facebook_user()
    return user

@layer_cache.cache_with_key_fxn(lambda user: "layer_cache_key_util_get_first_matching_user(User(%s,%s))" % (user.user_id(),user.email()))
def get_first_matching_user(user):
    # When a user's personal Google account is replaced by their transitioned Google Apps account with the same email,
    # the Google user ID changes and the new User object's are not considered equal to the old User object's with the same
    # email, so querying the datastore for entities referring to the new User object return nothing.  To avoid losing the user's 
    # history we want to use the old User object instead.  This method finds that old User object by using an inequality
    # query of the UserData entities to find users with matching email addresses and then returns the User object of the first
    # of those users to join. 
    email = user.email()
    gt_user = users.User(email[:-1] + chr(ord(email[-1])-1) + chr(127))
    lt_user = users.User(email + chr(0))
    first_to_join = None
    for ud in UserData.all().filter("user >", gt_user).filter("user <", lt_user):
        if first_to_join is None or ud.joined < first_to_join.joined:
            first_to_join = ud
    if first_to_join is not None:
        return first_to_join.user
    return user

def get_nickname_for(user):
    return nicknames.get_nickname_for(user)

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)

def create_post_login_url(dest_url):
    return "/postlogin?continue=%s" % urllib.quote(dest_url)

def create_logout_url(dest_url):
    return "/logout?continue=%s" % urllib.quote(dest_url)

def seconds_since(dt):
    return seconds_between(dt, datetime.datetime.now())

def seconds_between(dt1, dt2):
    timespan = dt2 - dt1
    return float(timespan.seconds + (timespan.days * 24 * 3600))

def minutes_between(dt1, dt2):
    return seconds_between(dt1, dt2) / 60.0

def seconds_to_time_string(seconds_init, short_display = True, show_hours = True):

    seconds = seconds_init

    years = math.floor(seconds / (86400 * 365))
    seconds -= years * (86400 * 365)

    days = math.floor(seconds / 86400)
    seconds -= days * 86400

    hours = math.floor(seconds / 3600)
    seconds -= hours * 3600

    minutes = math.floor(seconds / 60)
    seconds -= minutes * 60

    if years and days:
        return "%d year%s and %d day%s" % (years, pluralize(years), days, pluralize(days))
    elif years:
        return "%d year%s" % (years, pluralize(years))
    elif days and hours and show_hours:
        return "%d day%s and %d hour%s" % (days, pluralize(days), hours, pluralize(hours))
    elif days:
        return "%d day%s" % (days, pluralize(days))
    elif hours:
        if not short_display and minutes:
            return "%d hour%s and %d minute%s" % (hours, pluralize(hours), minutes, pluralize(minutes))
        else:
            return "%d hour%s" % (hours, pluralize(hours))
    else:
        if not short_display and seconds and not minutes:
            return "%d second%s" % (seconds, pluralize(seconds))
        return "%d minute%s" % (minutes, pluralize(minutes))

def thousands_separated_number(x):
    # See http://stackoverflow.com/questions/1823058/how-to-print-number-with-commas-as-thousands-separators-in-python-2-x
    if x < 0:
        return '-' + thousands_separated_number(-x)
    result = ''
    while x >= 1000:
        x, r = divmod(x, 1000)
        result = ",%03d%s" % (r, result)
    return "%d%s" % (x, result)

def async_queries(queries, limit=100000):

    task_runner = AsyncMultiTask()
    for query in queries:
        task_runner.append(QueryTask(query, limit=limit))
    task_runner.run()

    return task_runner

def static_url(relative_url):
    if App.is_dev_server or not os.environ['HTTP_HOST'].lower().endswith(".khanacademy.org"):
        return relative_url
    else:
        return "http://khanexercises.appspot.com%s" % relative_url
