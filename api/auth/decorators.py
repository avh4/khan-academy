from functools import wraps

import flask
from flask import request

from api.auth.auth_util import webapp_patched_request, oauth_error_response
from api.auth.models import OAuthMap

from oauth_provider.decorators import is_valid_request, validate_token
from oauth_provider.oauth import OAuthError

import util

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

                    if not util.get_current_user():
                        # If our OAuth provider thinks you're logged in but the 
                        # identity providers we consume (Google/Facebook) disagree,
                        # we act as if our token is no longer valid.
                        return oauth_error_response(OAuthError("Unable to get current user from oauth token."))

                    return func(*args, **kwargs)

            except OAuthError, e:
                return oauth_error_response(e)

        return oauth_error_response(OAuthError("Invalid OAuth parameters"))
    return wrapper

