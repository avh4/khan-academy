
# Yahoo Util uses Yahoo's OAuth API as both authentication and authorization, which is a little
# non-standard. In the future we may use OpenID for auth, but we aren't ready to enable
# OpenID on GAE for various reasons (bugs).
#
# For more info and examples see:
#   https://github.com/simplegeo/python-oauth2
#   http://developer.yahoo.com/oauth/guide/oauth-requesttoken.html
#   https://github.com/yahoo/yos-social-python/blob/master/examples/appengine/yosdemo.py
#   https://github.com/simplegeo/python-oauth2/blob/master/example/client.py

import httplib
import logging
import time
import cgi
import os
import unicodedata
import urlparse
import Cookie

from django.utils import simplejson
from google.appengine.api import users
from google.appengine.api import memcache

from app import App
import models
import oauth2 as oauth
import request_handler

REQUEST_TOKEN_URL = "https://api.login.yahoo.com/oauth/v2/get_request_token"
ACCESS_TOKEN_URL = "https://api.login.yahoo.com/oauth/v2/get_token"
AUTHORIZATION_URL = "https://api.login.yahoo.com/oauth/v2/request_auth"
PROFILE_URL = "http://social.yahooapis.com/v1/user/%s/profile/tinyusercard?format=JSON"

YAHOO_ID_EMAIL_PREFIX = "http://yahooid.khanacademy.org/"
YAHOO_COOKIE_NAME = "yoa_khanacademy"

def is_yahoo_email(email):
    return email.startswith(YAHOO_ID_EMAIL_PREFIX)

def get_current_yahoo_user():
    profile = get_yahoo_profile()

    if profile is not None:
        # Workaround http://code.google.com/p/googleappengine/issues/detail?id=573
        name = unicodedata.normalize('NFKD', profile["nickname"]).encode('ascii', 'ignore')
        
        # We create a fake user, substituting the user's Facebook uid for their email 
        # and their name for their OpenID identifier since Facebook isn't an
        # OpenID provider at the moment, and GAE displays the OpenID identifier as the nickname().
        return users.User(YAHOO_ID_EMAIL_PREFIX+profile["guid"], federated_identity = name)

    return None

def get_yahoo_profile():
    if App.yahoo_consumer_secret is None:
        return None

    oauth_hash = get_oauth_hash_from_cookie()
    if oauth_hash:
        return get_yahoo_profile_from_oauth_hash(oauth_hash)

    return None

def get_oauth_hash_from_cookie():
    cookies = Cookie.BaseCookie(os.environ.get("HTTP_COOKIE", ""))

    morsel = cookies.get(YAHOO_COOKIE_NAME)
    if morsel is None:
        return None

    return morsel.value 

def get_yahoo_profile_from_oauth_hash(oauth_hash):
    memcache_key = "yahoo_profile_%s" % oauth_hash
    profile = memcache.get(memcache_key)

    if not profile:
        cred = models.OAuthCred.get_by_key_name(oauth_hash)

        if not cred or not cred.access_key or not cred.guid:
            return None

        # TOKEN REFRESH
        url = PROFILE_URL % cred.guid
        token = oauth.Token(key=cred.access_key, secret=cred.secret)

        consumer = oauth.Consumer(App.yahoo_consumer_key, App.yahoo_consumer_secret)
        client = oauth.Client(consumer, token)
        resp, content = client.request(url)

        if resp["status"] != "200":
            logging.warning("Yahoo OAuth request for tinyusercard failed for guid %s" % cred.guid)
            return None

        try:
            json = simplejson.loads(content)
            profile = json['profile']
        except:
            logging.warning("Failed to parse json result of Yahoo OAuth request for tinyusercard for guid %s" % cred.guid)
            return None

        if profile:
            memcache.set(memcache_key, profile)

    return profile

def logout(handler):
    if get_oauth_hash_from_cookie():
        handler.delete_cookie(YAHOO_COOKIE_NAME)

class StartYahooLogin(request_handler.RequestHandler):
    def get(self):
        if get_current_yahoo_user():
            self.redirect("/")
            return

        consumer = oauth.Consumer(App.yahoo_consumer_key, App.yahoo_consumer_secret)
        client = oauth.Client(consumer)

        host = '/'.join(self.request.url.split('/')[:3])
        callback_url = "%s/finishyahoologin?continue=%s" % (host, self.request_string("continue", default="/"))

        resp, content = client.request(REQUEST_TOKEN_URL, "POST", body="oauth_callback=%s" % callback_url)
        if resp["status"] != "200":
            logging.warning("Yahoo OAuth request for request token failed")
            self.redirect("/")
            return

        request_token = dict(cgi.parse_qsl(content))
        if not request_token or \
                not request_token.has_key("oauth_token") or \
                not request_token.has_key("oauth_token_secret"):
            logging.warning("Yahoo OAuth request token or secret missing")
            self.redirect("/")
            return

        cred = models.OAuthCred.generate_with_random_hash()
        cred.request_token = request_token["oauth_token"]
        cred.secret = request_token["oauth_token_secret"]
        cred.put()

        # When Python 2.6 is available on App Engine we should add httponly=True
        self.set_cookie(YAHOO_COOKIE_NAME, value=cred.key().name(), max_age=60*60*24*14)
        self.redirect("%s?oauth_token=%s" % (AUTHORIZATION_URL, cred.request_token))

class FinishYahooLogin(request_handler.RequestHandler):
    def get(self):
        oauth_hash = get_oauth_hash_from_cookie()
        cred = models.OAuthCred.get_by_key_name(oauth_hash)

        if not cred:
            self.redirect("/")
            return

        consumer = oauth.Consumer(App.yahoo_consumer_key, App.yahoo_consumer_secret)

        token = oauth.Token(cred.request_token, cred.secret)
        token.set_verifier(self.request_string("oauth_verifier"))
        client = oauth.Client(consumer, token)

        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        if resp["status"] != "200":
            logging.warning("Yahoo OAuth request for exchanging request token for access token failed")
            self.redirect("/")
            return

        access_token = dict(cgi.parse_qsl(content))

        if not access_token or \
                not access_token.has_key("xoauth_yahoo_guid") or \
                not access_token.has_key("oauth_session_handle") or \
                not access_token.has_key("oauth_token") or \
                not access_token.has_key("oauth_token_secret"):
            logging.warning("Yahoo OAuth access token, guid, session_handle, or secret missing")
            self.redirect("/")
            return

        cred.access_key = access_token['oauth_token']
        cred.secret = access_token['oauth_token_secret']
        cred.session_handle = access_token['oauth_session_handle']
        cred.guid = access_token['xoauth_yahoo_guid']
        cred.put()

        self.redirect(self.request_string("continue", default="/"))
