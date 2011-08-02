import os
import Cookie
import logging
import unicodedata
import urllib2

from google.appengine.api import memcache
from google.appengine.api import urlfetch

from app import App
import facebook
import layer_cache
import request_cache

FACEBOOK_ID_EMAIL_PREFIX = "http://facebookid.khanacademy.org/"

def is_facebook_user(user_id):
    return user_id.startswith(FACEBOOK_ID_EMAIL_PREFIX)

def get_facebook_nickname_key(user_id):
    return "facebook_nickname_%s" % user_id

@request_cache.cache_with_key_fxn(get_facebook_nickname_key)
@layer_cache.cache_with_key_fxn(
        get_facebook_nickname_key, 
        layer=layer_cache.Layers.Memcache | layer_cache.Layers.Datastore,
        persist_across_app_versions=True)
def get_facebook_nickname(user_id):

    id = user_id.replace(FACEBOOK_ID_EMAIL_PREFIX, "")
    graph = facebook.GraphAPI()

    try:
        profile = graph.get_object(id)
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        # Bug fixed, utf-8 and nonascii is okay
        return unicodedata.normalize('NFKD', profile["name"]).encode('utf-8', 'ignore')
    except (facebook.GraphAPIError, urlfetch.DownloadError, AttributeError, urllib2.HTTPError):
        # In the event of an FB error, don't cache the result.
        return layer_cache.UncachedResult(user_id)

def get_current_facebook_user_id_from_cookies():
    return get_user_id_from_profile(get_profile_from_cookies())

def get_facebook_user_from_oauth_map(oauth_map):
    if oauth_map:
        return get_user_id_from_profile(get_profile_from_fb_token(oauth_map.facebook_access_token))
    return None

def get_user_id_from_profile(profile):

    if profile is not None:
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        name = unicodedata.normalize('NFKD', profile["name"]).encode('utf-8', 'ignore')

        user_id = FACEBOOK_ID_EMAIL_PREFIX+profile["id"]

        # Cache any future lookup of current user's facebook nickname in this request
        request_cache.set(get_facebook_nickname_key(user_id), name)

        return user_id

    return None

def get_profile_from_cookies():

    if App.facebook_app_secret is None:
        return None

    cookies = None
    try:
        cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
    except Cookie.CookieError, error:
        logging.debug("Ignoring Cookie Error, skipping Facebook login: '%s'" % error)

    if cookies is None:
        return None

    morsel_key = "fbs_" + App.facebook_app_id
    morsel = cookies.get(morsel_key)
    if morsel:
        fb_user_dict = facebook.get_user_from_cookie(
            {morsel_key: morsel.value}, App.facebook_app_id, App.facebook_app_secret)
        if fb_user_dict:
            return get_profile_from_fb_token(fb_user_dict["access_token"])
    
    return None

def get_profile_from_fb_token(access_token):

    if App.facebook_app_secret is None:
        return None

    if not access_token:
        logging.debug("Empty access token")
        return None

    memcache_key = "facebook_profile_for_%s" % access_token
    profile = memcache.get(memcache_key)
    if profile is not None:
        return profile

    c_facebook_tries_left = 3
    while not profile and c_facebook_tries_left > 0:
        try:
            graph = facebook.GraphAPI(access_token)
            profile = graph.get_object("me")
        except (facebook.GraphAPIError, urlfetch.DownloadError, AttributeError, urllib2.HTTPError), error:
            if type(error) == urllib2.HTTPError and error.code == 400:
                c_facebook_tries_left = 0
                logging.debug("Ignoring '%s'. Assuming access_token is no longer valid: %s" % (error, access_token))
            else:
                c_facebook_tries_left -= 1
                logging.debug("Ignoring Facebook graph error '%s'. Tries left: %s" % (error, c_facebook_tries_left))

    if profile:
        try:
            memcache.set(memcache_key, profile)
        except Exception, error:
            logging.warning("Facebook profile memcache set failed: %s", error)

    return profile

