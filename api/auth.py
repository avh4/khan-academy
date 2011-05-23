import logging
from functools import wraps

from google.appengine.ext import db

from flask import request, redirect
from flask import current_app

import util
from api import route
from oauth_provider.decorators import is_valid_request, validate_token
from oauth_provider.oauth import OAuthError, build_authenticate_header
from oauth_provider.utils import initialize_server_request
from oauth_provider.stores import check_valid_callback

class OAuthMap(db.Model):
    request_token = db.StringProperty()
    access_token = db.StringProperty()
    expires = db.DateTimeProperty()

    facebook_authorization_code = db.StringProperty()
    facebook_access_token = db.StringProperty()

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

# Flask-friendly port of oauth_providers.oauth_request.RequestTokenHandler
@route("/api/auth/request_token", methods=["GET", "POST"])
def request_token():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(OAuthError('Invalid request parameters.'))

    try:
        # create a request token
        token = oauth_server.fetch_request_token(oauth_request)
        # return the token
        return current_app.response_class(token.to_string(), status=200)
    except OAuthError, err:
        return oauth_error(err)

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
        # get the request callback, though there might not be one if this is OAuth 1.0a
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

# Flask-friendly port of oauth_providers.oauth_request.AcessTokenHandler
@route("/api/auth/access_token", methods=["GET", "POST"])
def authorize():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error(oauth.OAuthError('Invalid request parameters.'))
    
    try:
        # create an access token
        token = oauth_server.fetch_access_token(oauth_request)

        if token == None:
            return oauth_error(oauth.OAuthError("Cannot find corresponding access token."))

        return current_app.response_class(token.to_string(), status=200)
    except OAuthError, err:
        return oauth_error(err)
