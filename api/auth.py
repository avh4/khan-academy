import logging
from functools import wraps
import urllib

from google.appengine.ext import db

from flask import request, redirect
from flask import current_app

import util
from app import App

from api import route
from oauth_provider.decorators import is_valid_request, validate_token
from oauth_provider.oauth import OAuthError, build_authenticate_header
from oauth_provider.utils import initialize_server_request
from oauth_provider.stores import check_valid_callback

# Our API's OAuth authentication and authorization is designed to encapsulate the OAuth support
# of our identity providers (Google/Facebook), so each of our mobile apps and client applications 
# don't have to handle each auth provider independently. We behave as one single OAuth set of endpoints
# for them to interact with.

# OAuthMap creates a mapping between our OAuth credentials and our identity providers.
class OAuthMap(db.Model):
    request_token = db.StringProperty()
    request_token_secret = db.StringProperty()
    access_token = db.StringProperty()
    access_token_secret = db.StringProperty()
    expires = db.DateTimeProperty()

    facebook_authorization_code = db.StringProperty()
    facebook_access_token = db.StringProperty()

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

# Flask-friendly port of oauth_providers.decorators.oauth_required
def oauth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        webapp_req = webapp_patched_request(request)

        if is_valid_request(webapp_req):
            try:
                consumer, token, parameters = validate_token(webapp_req)
                if consumer and token:
                    return func(*args, **kwargs)
            except OAuthError, e:
                return oauth_error(e)

        return oauth_error(OAuthError("Invalid OAuth parameters"))
    return wrapper

def oauth_error(e):
    return current_app.response_class(e.message, status=401, headers=build_authenticate_header(realm="http://www.khanacademy.org"))

@route("/api/auth/request_token", methods=["GET", "POST"])
def request_token_start():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))

    try:
        # create a request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, err:
        return oauth_error(err)

    continue_url = "http://local.kamenstestapp.appspot.com:8084/api/auth/request_token_finish?%s" % token.to_string()

    is_facebook_auth = True
    if is_facebook_auth:
        params = {
                    "client_id": App.facebook_app_id,
                    "redirect_uri": continue_url,
                    }
        return redirect("https://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(params))

# Flask-friendly port of oauth_providers.oauth_request.RequestTokenHandler
@route("/api/auth/request_token_finish", methods=["GET"])
def request_token_finish():

    oauth_map = OAuthMap()
    oauth_map.request_token_secret = request.values.get("oauth_token_secret")
    oauth_map.request_token = request.values.get("oauth_token")
    oauth_map.facebook_authorization_code = request.values.get("code")
    oauth_map.put()

    return "NEED TO REDIRECT HERE. request_token=%s&token_secret=%s" % (oauth_map.request_token, oauth_map.request_token_secret)

# Flask-friendly port of oauth_providers.oauth_request.AuthorizeHandler that doesn't
# require user authorization.
@route("/api/auth/authorize", methods=["GET", "POST"])
def authorize():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))

    try:
        # get the request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, err:
        return oauth_error(err)

    try:
        callback = oauth_server.get_callback(oauth_request)
        
        if not check_valid_callback(callback):
            return oauth_error(OAuthError("Invalid callback URL"))

    except OAuthError,err:
        callback = None
        
    try:
        user = util.get_current_user()

        if user:

            # For now we don't require user intervention to authorize our tokens,
            # since the user already authorized FB/Google. If we need to do this
            # for security reasons later, there's no reason we can't.
            token = oauth_server.authorize_token(token, user)

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
    
    except OAuthError, err:
        return oauth_error(err)

# Flask-friendly port of oauth_providers.oauth_request.AccessTokenHandler
@route("/api/auth/access_token", methods=["GET", "POST"])
def access_token():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))
    
    try:
        # Create access token
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

    except OAuthError, err:
        return oauth_error(err)

    continue_url = "http://local.kamenstestapp.appspot.com:8084/api/auth/access_token_finish?%s" % token.to_string()

    is_facebook_auth = True
    if is_facebook_auth:
        params = {
                    "client_id": App.facebook_app_id,
                    "client_secret": App.facebook_app_secret,
                    "redirect_uri": continue_url,
                    "code": oauth_map.facebook_authorization_code,
                    }
        return redirect("https://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(params))

@route("/api/auth/access_token_finish", methods=["GET"])
def access_token_finish():

    oauth_map = OAuthMap.get_from_access_token(request.values.get("oauth_token"))
    if not oauth_map:
        return oauth_error(OAuthError("Cannot find oauth mapping for access token."))

    oauth_map.facebook_access_token = request.values.get("access_token")
    # Add EXPIRES handling here
    oauth_map.put()

    return "NEED TO REDIRECT HERE. access_token=%s&token_secret=%s" % (oauth_map.access_token, oauth_map.access_token_secret)


