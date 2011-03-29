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

FACEBOOK_ID_EMAIL_PREFIX = "http://facebookid.khanacademy.org/"

def is_facebook_email(email):
    return email.startswith(FACEBOOK_ID_EMAIL_PREFIX)

def get_facebook_nickname(user):

    email = user.email()

    memcache_key = "facebook_nickname_%s" % email
    name = memcache.get(memcache_key)
    if name is not None:
        return name

    id = email.replace(FACEBOOK_ID_EMAIL_PREFIX, "")
    graph = facebook.GraphAPI()

    try:
        profile = graph.get_object(id)
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        name = unicodedata.normalize('NFKD', profile["name"]).encode('ascii', 'ignore')
        memcache.set(memcache_key, name)
    except (facebook.GraphAPIError, urlfetch.DownloadError, AttributeError):
        name = email

    return name

def get_current_facebook_user():

    profile = get_facebook_profile()

    if profile is not None:
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        name = unicodedata.normalize('NFKD', profile["name"]).encode('ascii', 'ignore')
        
        # We create a fake user, substituting the user's Facebook uid for their email 
        # and their name for their OpenID identifier since Facebook isn't an
        # OpenID provider at the moment, and GAE displays the OpenID identifier as the nickname().
        return users.User(FACEBOOK_ID_EMAIL_PREFIX+profile["id"], federated_identity = name)

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
                if str(error).find("Error validating access token") >= 0:
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

    cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))

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
