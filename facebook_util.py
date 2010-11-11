import os
import Cookie
import logging
import unicodedata
from google.appengine.api import users
from google.appengine.api import memcache

from app import App
import facebook

FACEBOOK_ID_EMAIL_PREFIX = "http://facebookid.khanacademy.org/"

# Force cached facebook info expiration at least once every 30 days,
# even though memcache will probably have cleared before then due to external
# memory pressure.
FACEBOOK_CACHE_EXPIRATION_SECONDS = 60 * 60 * 24 * 30

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
        memcache.set(memcache_key, name, time=FACEBOOK_CACHE_EXPIRATION_SECONDS)
    except facebook.GraphAPIError:
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
    def get_profile_from_cookie(cookie):
        expires = int(cookie["expires"])
        if expires == 0 and time.time() > expires:
            return None
        memcache_key = "facebook_profile_for_%s" % cookie["access_token"]        
        profile = memcache.get(memcache_key)
        if profile is not None:
            return profile
        try:
            graph = facebook.GraphAPI(cookie["access_token"])
            profile = graph.get_object("me")
            memcache.set(memcache_key, profile, time=FACEBOOK_CACHE_EXPIRATION_SECONDS)
        except facebook.GraphAPIError, error:
            logging.debug("Ignoring %s.  Assuming access_token is no longer valid." % error)
        return profile

    if App.facebook_app_secret is None:
        return None
    cookies = Cookie.BaseCookie(os.environ.get('HTTP_COOKIE',''))
    morsel_key = "fbs_" + App.facebook_app_id
    morsel = cookies.get(morsel_key)
    if morsel is None:
        return None
    morsel_value = morsel.value
    cookie = facebook.get_user_from_cookie(
        {morsel_key: morsel_value}, App.facebook_app_id, App.facebook_app_secret)
    if cookie:
        return get_profile_from_cookie(cookie)
    return None
