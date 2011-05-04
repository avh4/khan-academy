import os
import Cookie
import logging
import unicodedata
import urllib2

from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.api import urlfetch

from app import App
import facebook
import layer_cache
import request_cache

FACEBOOK_ID_EMAIL_PREFIX = "http://facebookid.khanacademy.org/"

def is_facebook_email(email):
    return email.startswith(FACEBOOK_ID_EMAIL_PREFIX)

def get_facebook_nickname_key(user):
    return "facebook_nickname_%s" % user.email()

@request_cache.cache_with_key_fxn(get_facebook_nickname_key)
@layer_cache.cache_with_key_fxn(
        get_facebook_nickname_key, 
        layer=layer_cache.Layers.Memcache | layer_cache.Layers.Datastore,
        persist_across_app_versions=True)
def get_facebook_nickname(user):

    email = user.email()
    id = email.replace(FACEBOOK_ID_EMAIL_PREFIX, "")
    graph = facebook.GraphAPI()

    try:
        profile = graph.get_object(id)
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        return unicodedata.normalize('NFKD', profile["name"]).encode('ascii', 'ignore')
    except (facebook.GraphAPIError, urlfetch.DownloadError, AttributeError, urllib2.HTTPError):
        # In the event of an FB error, don't cache the result.
        return layer_cache.UncachedResult(email)

def get_current_facebook_user():

    profile = get_facebook_profile()

    if profile is not None:
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        name = unicodedata.normalize('NFKD', profile["name"]).encode('ascii', 'ignore')

        # We create a fake user, substituting the user's Facebook uid for their email 
        user = users.User(FACEBOOK_ID_EMAIL_PREFIX+profile["id"])

        # Cache any future lookup of current user's facebook nickname in this request
        request_cache.set(get_facebook_nickname_key(user), name)

        return user

    return None

def get_facebook_profile():

    def get_profile_from_fb_user(fb_user):

        expires = int(fb_user["expires"])
        if expires == 0 and time.time() > expires:
            return None

        if not fb_user["access_token"]:
            logging.debug("Empty access token for fb_user")
            return None

        memcache_key = "facebook_profile_for_%s" % fb_user["access_token"]        
        profile = memcache.get(memcache_key)
        if profile is not None:
            return profile

        c_facebook_tries_left = 3
        while not profile and c_facebook_tries_left > 0:
            try:
                graph = facebook.GraphAPI(fb_user["access_token"])
                profile = graph.get_object("me")
            except (facebook.GraphAPIError, urlfetch.DownloadError, AttributeError, urllib2.HTTPError), error:
                if type(error) == urllib2.HTTPError and error.code == 400:
                    c_facebook_tries_left = 0
                    logging.debug("Ignoring '%s'. Assuming access_token is no longer valid: %s" % (error, fb_user["access_token"]))
                else:
                    c_facebook_tries_left -= 1
                    logging.debug("Ignoring Facebook graph error '%s'. Tries left: %s" % (error, c_facebook_tries_left))

        if profile:
            try:
                memcache.set(memcache_key, profile)
            except Exception, error:
                logging.warning("Facebook profile memcache set failed: %s", error)

        return profile

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
    if morsel is None:
        return None

    morsel_value = morsel.value
    fb_user = facebook.get_user_from_cookie(
        {morsel_key: morsel_value}, App.facebook_app_id, App.facebook_app_secret)

    if fb_user:
        return get_profile_from_fb_user(fb_user)

    return None
