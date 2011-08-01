import os
import datetime
import urllib
import request_cache

from google.appengine.api import users
from google.appengine.api import oauth
from asynctools import AsyncMultiTask, QueryTask

from app import App
import nicknames
import facebook_util
from phantom_users.phantom_util import get_phantom_user_id_from_cookies, \
    is_phantom_id

from api.auth.google_util import get_google_user_from_oauth_map
from api.auth.auth_util import current_oauth_map, allow_cookie_based_auth

@request_cache.cache()
def get_current_user_id(bust_cache=False):
    user_id = None

    oauth_map = current_oauth_map()
    if oauth_map:
        user_id = get_current_user_from_oauth_map(oauth_map)

    if not user_id and allow_cookie_based_auth():
        user_id = get_current_user_id_from_cookies_unsafe()

    return user_id

def get_current_user_from_oauth_map(oauth_map):
    user = get_google_user_from_oauth_map(oauth_map)
    if not user:
        user = facebook_util.get_facebook_userid__from_oauth_map(oauth_map)
    return user

# _get_current_user_from_cookies_unsafe is labeled unsafe because it should
# never be used in our JSONP-enabled API. All calling code should just use _get_current_user.
def get_current_user_id_from_cookies_unsafe():
    user = users.get_current_user()
    if user:
        user_id = "G"+user.user_id()
    if not user:
        user_id = facebook_util.get_current_facebook_user_id_from_cookies()
    if not user:
        user_id = get_phantom_user_id_from_cookies()
    return user_id

def is_phantom_user(user_id):
    return user_id and is_phantom_id(user_id)

def create_login_url(dest_url):
    return "/login?continue=%s" % urllib.quote(dest_url)

def create_mobile_oauth_login_url(dest_url):
    return "/login/mobileoauth?continue=%s" % urllib.quote(dest_url)

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
