import logging
from functools import wraps
import urllib
import urllib2
import cgi

from google.appengine.ext import db

import flask
from flask import request, redirect
from flask import current_app

from app import App

from api import route
from oauth_provider.decorators import is_valid_request, validate_token
from oauth_provider.oauth import OAuthClient, OAuthConsumer, OAuthToken, OAuthRequest, OAuthError, OAuthSignatureMethod_HMAC_SHA1, build_authenticate_header
from oauth_provider.utils import initialize_server_request
from oauth_provider.stores import check_valid_callback

# Our API's OAuth authentication and authorization is designed to encapsulate the OAuth support
# of our identity providers (Google/Facebook), so each of our mobile apps and client applications 
# don't have to handle each auth provider independently. We behave as one single OAuth set of endpoints
# for them to interact with.

# OAuthMap creates a mapping between our OAuth credentials and our identity providers'.
class OAuthMap(db.Model):

    # Our tokens
    request_token = db.StringProperty()
    request_token_secret = db.StringProperty()
    access_token = db.StringProperty()
    access_token_secret = db.StringProperty()

    # Facebook tokens
    facebook_authorization_code = db.StringProperty()
    facebook_access_token = db.StringProperty()

    # Google tokens
    google_request_token = db.StringProperty()
    google_request_token_secret = db.StringProperty()
    google_access_token = db.StringProperty()
    google_access_token_secret = db.StringProperty()
    google_verification_code = db.StringProperty()

    # Expiration
    expires = db.DateTimeProperty()

    def uses_facebook(self):
        return self.facebook_authorization_code

    def uses_google(self):
        return self.google_request_token

    @staticmethod
    def get_by_id_safe(request_id):
        if not request_id:
            return None
        try:
            parsed_id = int(request_id)
        except ValueError:
            return None
        return OAuthMap.get_by_id(parsed_id)

    @staticmethod
    def get_from_request_token(request_token):
        if not request_token:
            return None
        return OAuthMap.all().filter("request_token =", request_token).get()

    @staticmethod
    def get_from_access_token(access_token):
        if not access_token:
            return None
        return OAuthMap.all().filter("access_token =", access_token).get()

def webapp_patched_request(request):
    request.arguments = lambda: request.values
    request.get = lambda key: request.values.get(key)
    return request

# Flask-friendly wrapper for validating an oauth request and storing the OAuthMap for use
# in the rest of the request.
def oauth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        webapp_req = webapp_patched_request(request)

        if is_valid_request(webapp_req):
            try:
                consumer, token, parameters = validate_token(webapp_req)
                if consumer and token:
                    # Store the OAuthMap containing all auth info in the request global
                    # for easy access during the rest of this request.
                    flask.g.oauth_map = OAuthMap.get_from_access_token(token.key_)

                    return func(*args, **kwargs)

            except OAuthError, e:
                return oauth_error(e)

        return oauth_error(OAuthError("Invalid OAuth parameters"))
    return wrapper

def current_oauth_map():
    if hasattr(flask.g, "oauth_map"):
        return flask.g.oauth_map
    return None

def oauth_error(e):
    return current_app.response_class("OAuth error. %s" % e.message, status=401, headers=build_authenticate_header(realm="http://www.khanacademy.org"))

# REQUEST TOKEN GATHERING
#
# Flask-friendly version of oauth_providers.oauth_request.RequestTokenHandler that redirects to Google/Facebook
# to gather the appropriate request tokens.
@route("/api/auth/request_token", methods=["GET", "POST"])
def request_token_start():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))

    try:
        # Create our request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, e:
        return oauth_error(e)

    # Start a new OAuth mapping
    oauth_map = OAuthMap()
    oauth_map.request_token_secret = token.secret
    oauth_map.request_token = token.key_
    oauth_map.put()

    is_facebook_auth = False

    if is_facebook_auth:

        # Start Facebook request token process
        params = {
                    "client_id": App.facebook_app_id,
                    "redirect_uri": "http://local.kamenstestapp.appspot.com:8084/api/auth/facebook_token_callback?oauth_map_id=%s" % oauth_map.key().id(),
                    }
        return redirect("https://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(params))

    else:

        # Start Google request token process
        try:
            google_client = GoogleOAuthClient()
            google_token = google_client.fetch_request_token(oauth_map)
        except Exception, e:
            return oauth_error(OAuthError(e.message))

        oauth_map.google_request_token = google_token.key
        oauth_map.google_request_token_secret = google_token.secret
        oauth_map.put()

        return "NEED TO REDIRECT HERE. request_token=%s&token_secret=%s" % (oauth_map.request_token, oauth_map.request_token_secret)

# Associate our request or access token with Facebook's tokens
@route("/api/auth/facebook_token_callback", methods=["GET"])
def facebook_token_callback():
    oauth_map = OAuthMap.get_by_id_safe(request.values.get("oauth_map_id"))

    if not oauth_map:
        return oauth_error(OAuthError("Unable to find OAuthMap by id."))

    if not oauth_map.facebook_authorization_code:
        oauth_map.facebook_authorization_code = request.values.get("code")
        oauth_map.put()
        return "NEED TO REDIRECT HERE. request_token=%s&token_secret=%s" % (oauth_map.request_token, oauth_map.request_token_secret)

@route("/api/auth/google_token_callback", methods=["GET"])
def google_token_callback():
    oauth_map = OAuthMap.get_by_id_safe(request.values.get("oauth_map_id"))

    if not oauth_map:
        return oauth_error(OAuthError("Unable to find OAuthMap by id."))

    if not oauth_map.google_verification_code:
        oauth_map.google_verification_code = request.values.get("verifier")
        oauth_map.put()

    return "NEED TO REDIRECT HERE. authorized request_token=%s&token_secret=%s" % (oauth_map.request_token, oauth_map.request_token_secret)

# TOKEN AUTHORIZATION
#
# Flask-friendly version of oauth_providers.oauth_request.AuthorizeHandler that doesn't
# require user authorization, just logging in.
#
# We import util here, after definition of current_oauth_map, to avoid circular dependency.
import util
@route("/api/auth/authorize", methods=["GET", "POST"])
def authorize():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))

    try:
        # get the request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, e:
        return oauth_error(e)

    try:
        callback = oauth_server.get_callback(oauth_request)
        
        if not check_valid_callback(callback):
            return oauth_error(OAuthError("Invalid callback URL"))

    except OAuthError, e:
        callback = None
        
    try:
        # Force the use of cookie-based auth for this and *only* this part of API authentication
        user = util.get_current_user_from_cookies_unsafe()

        if user:

            # For now we don't require user intervention to authorize our tokens,
            # since the user already authorized FB/Google. If we need to do this
            # for security reasons later, there's no reason we can't.
            token = oauth_server.authorize_token(token, user)

            oauth_map = OAuthMap.get_from_request_token(token.key_)
            if not oauth_map:
                raise OAuthError("Unable to find oauth_map from request token during authorization.")

            if oauth_map.uses_google():

                params = { "oauth_token": oauth_map.google_request_token }
                return redirect("http://www.khanacademy.org/_ah/OAuthAuthorizeToken?%s" % urllib.urlencode(params))

            else:

                if callback:
                    if "?" in callback:
                        url_delimiter = "&"
                    else:
                        url_delimiter = "?"

                    query_args = token.to_string(only_key=True)
                    
                    return redirect(('%s%s%s' % (callback, url_delimiter, query_args)))
                else:
                    return current_app.response_class("Successfully authorized: %s" % token.to_string(only_key=True), status=200)

        else:

            #handle the fact that this might be a POST request and the 
            #required oauth_token (and possibly oauth_callback for
            # OAuth 1.0 requests) will not be on the request.uri
            #Hence we add it to it before redirecting to the login page
            
            continue_url = request.url
            
            if 'oauth_token' not in continue_url:
                if '?' not in continue_url:
                    continue_url += "?"
                else:
                    continue_url += "&"
                continue_url += token.to_string(only_key=True)

            if 'oauth_callback' not in continue_url:
                if '?' not in continue_url:
                    continue_url += "?"
                else:
                    continue_url += "&"
                continue_url += "oauth_callback=%s" % (callback)

            return redirect(util.create_login_url(continue_url))
    
    except OAuthError, e:
        return oauth_error(e)

# ACCESS TOKEN GATHERING
#
# Flask-friendly version of oauth_providers.oauth_request.AccessTokenHandler
# that creates our access token and then redirects to Google/Facebook to let them
# create theirs.
@route("/api/auth/access_token", methods=["GET", "POST"])
def access_token():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))
    
    try:
        # Create our access token
        token = oauth_server.fetch_access_token(oauth_request)
        if not token:
            return oauth_error(OAuthError("Cannot find corresponding access token."))

        # Grab the mapping of access tokens to our identity providers 
        oauth_map = OAuthMap.get_from_request_token(request.values.get("oauth_token"))
        if not oauth_map:
            return oauth_error(OAuthError("Cannot find oauth mapping for request token."))

        oauth_map.access_token = token.key_
        oauth_map.access_token_secret = token.secret
        oauth_map.put()

    except OAuthError, e:
        raise
        return oauth_error(e)

    if oauth_map.uses_facebook():

        # Start Facebook access token process

        continue_url = "http://local.kamenstestapp.appspot.com:8084/api/auth/facebook_token_callback?oauth_map_id=%s" % oauth_map.key().id()

        params = {
                    "client_id": App.facebook_app_id,
                    "client_secret": App.facebook_app_secret,
                    "redirect_uri": continue_url,
                    "code": oauth_map.facebook_authorization_code,
                    }

        try:
            response = get_response("https://graph.facebook.com/oauth/access_token", params)
        except Exception, e:
            return oauth_error(OAuthError(e.message))

        response_params = get_parsed_params(response)
        if not response_params or not response_params.get("access_token"):
            return oauth_error(OAuthError("Cannot get access_token from Facebook's /oauth/access_token response"))
         
        # Associate our access token and Google/Facebook's
        oauth_map.facebook_access_token = response_params["access_token"][0]
        # Add EXPIRES handling here
        oauth_map.put()

        return "NEED TO REDIRECT HERE. access_token=%s&token_secret=%s" % (oauth_map.access_token, oauth_map.access_token_secret)

    elif oauth_map.uses_google():

        # Start Google access token process
        try:
            google_client = GoogleOAuthClient()
            google_token = google_client.fetch_access_token(oauth_map)
        except Exception, e:
            raise
            return oauth_error(OAuthError(e.message))

        oauth_map.google_access_token = google_token.key
        oauth_map.google_access_token_secret = google_token.secret
        oauth_map.put()

        return "NEED TO REDIRECT HERE. access_token=%s&token_secret=%s" % (oauth_map.access_token, oauth_map.access_token_secret)

def get_response(url, params={}):
    if params:
        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += urllib.urlencode(params)

    response = ""
    file = None
    try:
        file = urllib2.urlopen(url)
        response = file.read()
    finally:
        if file:
            file.close()

    return response

def get_parsed_params(resp):
    if not resp:
        return {}
    return cgi.parse_qs(resp)

class GoogleOAuthClient(object):

    Consumer = OAuthConsumer(App.google_consumer_key, App.google_consumer_secret)

    def fetch_request_token(self, oauth_map):
        oauth_request = OAuthRequest.from_consumer_and_token(
                GoogleOAuthClient.Consumer,
                http_url = "http://www.khanacademy.org/_ah/OAuthGetRequestToken",
                callback = "http://localhost:8084/api/auth/google_token_callback?oauth_map_id=%s" % oauth_map.key().id()
                )

        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), GoogleOAuthClient.Consumer, None)

        response = get_response(oauth_request.to_url())

        return OAuthToken.from_string(response)

    def fetch_access_token(self, oauth_map):

        token = OAuthToken(oauth_map.google_request_token, oauth_map.google_request_token_secret)

        oauth_request = OAuthRequest.from_consumer_and_token(
                GoogleOAuthClient.Consumer,
                token = token,
                verifier = oauth_map.google_verification_code,
                http_url = "http://www.khanacademy.org/_ah/OAuthGetAccessToken"
                )

        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), GoogleOAuthClient.Consumer, token)

        response = get_response(oauth_request.to_url())

        return OAuthToken.from_string(response)
