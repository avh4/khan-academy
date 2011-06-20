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

PHANTOM_ID_EMAIL_PREFIX = "http://nouserid.khanacademy.org/"

def is_phantom_email(email):
    return email.startswith(PHANTOM_ID_EMAIL_PREFIX)

def get_phantom_nickname_key(user):
    return "phantom_nickname_%s" % user.email()

# @request_cache.cache_with_key_fxn(get_phantom_nickname_key)
# @layer_cache.cache_with_key_fxn(
#         get_phantom_nickname_key, 
#         layer=layer_cache.Layers.Memcache | layer_cache.Layers.Datastore,
#         persist_across_app_versions=True)

def get_phantom_user_from_cookies():
    cookies = None
    try:
        cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
    except Cookie.CookieError, error:
        logging.debug("Ignoring Cookie Error: '%s'" % error)

    morsel_key = "ureg_id"
    morsel = cookies.get(morsel_key)
    if morsel:
        try:
            return users.User(morsel.value)
        except UserNotFoundError:
            return None
    else:
        return None

def create_phantom_user():
    rs = os.urandom(20)
    random_string = hashlib.md5(rs).hexdigest()
    return users.User(PHANTOM_ID_EMAIL_PREFIX+random_string)
