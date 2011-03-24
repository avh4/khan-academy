import datetime
import math
import urllib
from google.appengine.api import users
from django.template.defaultfilters import pluralize

import nicknames
import facebook_util

def get_current_user():

    appengine_user = users.get_current_user()
    if appengine_user is not None:
        return appengine_user

    facebook_user = facebook_util.get_current_facebook_user()
    if facebook_user is not None:
        return facebook_user

    return None

def get_nickname_for(user):
    return nicknames.get_nickname_for(user)

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)

def create_logout_url(dest_url):
    return "/logout?continue=%s" % urllib.quote(dest_url)

def seconds_since(dt):
    return seconds_between(dt, datetime.datetime.now())

def seconds_between(dt1, dt2):
    timespan = dt2 - dt1
    return float(timespan.seconds + (timespan.days * 24 * 3600))

def minutes_between(dt1, dt2):
    return seconds_between(dt1, dt2) / 60.0

def seconds_to_time_string(seconds_init, short_display = True):

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
    elif days and hours:
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


