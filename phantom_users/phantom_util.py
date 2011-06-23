import os
import Cookie
import logging
import unicodedata
import urllib2
import hashlib

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from app import App
import layer_cache
import request_cache
import util

PHANTOM_ID_EMAIL_PREFIX = "http://nouserid.khanacademy.org/"

def is_phantom_email(email):
    return email.startswith(PHANTOM_ID_EMAIL_PREFIX)

def get_phantom_nickname_key(user):
    return "phantom_nickname_%s" % user.email()

def get_phantom_user_from_cookies():
    cookies = None
    try:
        cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
    except Cookie.CookieError, error:
        logging.critical("Ignoring Cookie Error: '%s'" % error)

    morsel_key = "ureg_id"
    morsel = cookies.get(morsel_key)
    if morsel:
        try:
            return users.User(PHANTOM_ID_EMAIL_PREFIX+morsel.value)
        except UserNotFoundError:
            return None
    else:
        return None

def create_phantom_user():
    rs = os.urandom(20)
    random_string = hashlib.md5(rs).hexdigest()
    return users.User(PHANTOM_ID_EMAIL_PREFIX+random_string)

def allow_phantoms(method):
    def wrapper(self):
        user = util.get_current_user(allow_phantoms=True)
        if not user:
            user = create_phantom_user()
        
        if util.is_phantom_user(user):
            # we set a 20 digit random string as the cookie, not the entire fake email
            cookie = user.email().split('http://nouserid.khanacademy.org/')[1]
            # set the cookie on the user's computer
            self.set_cookie('ureg_id', cookie)
            # pretend the user already had the cookie set
            self.request.cookies['ureg_id'] = cookie
        method(self)
    return wrapper
