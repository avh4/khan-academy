import logging
import urllib
import os

import flask
from flask import request, redirect
from flask import current_app

from api import route
from api.auth.models import OAuthMap
from api.auth.auth_util import webapp_patched_request, oauth_error_response, append_url_params
from api.auth.google_util import google_request_token_handler, google_authorize_token_handler, google_access_token_handler
from api.auth.facebook_util import facebook_request_token_handler, facebook_authorize_token_handler, facebook_access_token_handler

from oauth_provider.oauth import OAuthError
from oauth_provider.utils import initialize_server_request
from oauth_provider.stores import check_valid_callback

import util

# Our API's OAuth authentication and authorization is designed to encapsulate the OAuth support
# of our identity providers (Google/Facebook), so each of our mobile apps and client applications 
# don't have to handle each auth provider independently. We behave as one single OAuth set of endpoints
# for them to interact with.

# Request token endpoint
#
# Flask-friendly version of oauth_providers.oauth_request.RequestTokenHandler that 
# hands off to Google/Facebook to gather the appropriate request tokens.
@route("/api/auth/request_token", methods=["GET", "POST"])
def request_token():

    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error_response(OAuthError('Invalid request parameters.'))

    # Force the use of cookie-based auth for request_token and authorize_token parts of API authentication *only*
    user = util.get_current_user_from_cookies_unsafe()

    if user:

        try:
            # Create our request token
            token = oauth_server.fetch_request_token(oauth_request)
        except OAuthError, e:
            return oauth_error_response(e)

        # Start a new OAuth mapping
        oauth_map = OAuthMap()
        oauth_map.request_token_secret = token.secret
        oauth_map.request_token = token.key_
        oauth_map.callback_url = request.values.get("oauth_callback")
        oauth_map.put()

        if util.is_facebook_user(user):
            return facebook_request_token_handler(oauth_map)
        else:
            return google_request_token_handler(oauth_map)

    else:

        # Ask user to login, then redirect to start of request_token process.
        return redirect(util.create_login_url(request.url))

# Token authorization endpoint
#
# Flask-friendly version of oauth_providers.oauth_request.AuthorizeHandler that doesn't
# require user authorization for our side of the OAuth. Just log in, and we'll authorize.
@route("/api/auth/authorize", methods=["GET", "POST"])
def authorize_token():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error_response(OAuthError('Invalid request parameters.'))

    # Force the use of cookie-based auth for request_token and authorize_token parts of API authentication *only*
    user = util.get_current_user_from_cookies_unsafe()
    if not user:
        return oauth_error(OAuthError("User not logged in during authorize_token process."))

    try:
        # get the request token
        token = oauth_server.fetch_request_token(oauth_request)
    except OAuthError, e:
        return oauth_error_response(e)

    try:
        # For now we don't require user intervention to authorize our tokens,
        # since the user already authorized FB/Google. If we need to do this
        # for security reasons later, there's no reason we can't.
        token = oauth_server.authorize_token(token, user)

        oauth_map = OAuthMap.get_from_request_token(token.key_)
        if not oauth_map:
            raise OAuthError("Unable to find oauth_map from request token during authorization.")

        oauth_map.verifier = token.verifier
        oauth_map.put()

        if oauth_map.uses_google():
            return google_authorize_token_handler(oauth_map)
        else:
            return facebook_authorize_token_handler(oauth_map)

    except OAuthError, e:
        return oauth_error_response(e)

# Access token endpoint
#
# Flask-friendly version of oauth_providers.oauth_request.AccessTokenHandler
# that creates our access token and then hands off to Google/Facebook to let them
# create theirs before associating the two.
@route("/api/auth/access_token", methods=["GET", "POST"])
def access_token():
    webapp_req = webapp_patched_request(request)

    oauth_server, oauth_request = initialize_server_request(webapp_req)

    if oauth_server is None:
        return oauth_error_response(OAuthError('Invalid request parameters.'))
    
    try:
        # Create our access token
        token = oauth_server.fetch_access_token(oauth_request)
        if not token:
            return oauth_error_response(OAuthError("Cannot find corresponding access token."))

        # Grab the mapping of access tokens to our identity providers 
        oauth_map = OAuthMap.get_from_request_token(request.values.get("oauth_token"))
        if not oauth_map:
            return oauth_error_response(OAuthError("Cannot find oauth mapping for request token."))

        oauth_map.access_token = token.key_
        oauth_map.access_token_secret = token.secret
        oauth_map.put()

    except OAuthError, e:
        return oauth_error_response(e)

    if oauth_map.uses_facebook():
        return facebook_access_token_handler(oauth_map)
    elif oauth_map.uses_google():
        return google_access_token_handler(oauth_map)
