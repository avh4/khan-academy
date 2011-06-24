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
PHANTOM_MORSEL_KEY = 'ureg_id'

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

    morsel = cookies.get(PHANTOM_MORSEL_KEY)
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
    '''Decorator used to create phantom users if necessary.

    Warnings:
    - Only use on get methods where a phantom user should be allowed to
    experiment, and would be forced to login otherwise.
    - Don't use on get methods with more arguments than just self (this could
    easily be changed).
    '''

    def wrapper(self):
        # This first section of code is duplicated from util.get_current_user.
        # The reason we can't just use the code over is because
        # get_current_user is cached so if we call it here and it returns none,
        # then we create a phantom user, it will continue to return None in the
        # future.
        user = None

        oauth_map = util.current_oauth_map()
        if oauth_map:
            user = util.get_current_user_from_oauth_map(oauth_map)

        if not user and util.allow_cookie_based_auth():
            user = util.get_current_user_from_cookies_unsafe(allow_phantoms=True)

        # End duplicated code

        if not user:
            user = create_phantom_user()
        
            # we set a 20 digit random string as the cookie, not the entire fake email
            cookie = user.email().split(PHANTOM_ID_EMAIL_PREFIX)[1]
            # set the cookie on the user's computer
            self.set_cookie(PHANTOM_MORSEL_KEY, cookie)

            # pretend the user already had the cookie set
            try:
                allcookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
            except Cookie.CookieError, error:
                logging.critical("Ignoring Cookie Error: '%s'" % error)

            # now set a fake cookie for this request
            allcookies[PHANTOM_MORSEL_KEY] = str(cookie)
            os.environ['HTTP_COOKIE'] = allcookies.output()
        method(self)
    return wrapper
