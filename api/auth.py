import logging
from functools import wraps

from flask import request
from flask import current_app

from oauth_provider.decorators import is_valid_request, validate_token
from oauth_provider.oauth import OAuthError, build_authenticate_header

# Flask-friendly version of oauth_providers.decorators.oauth_required
def oauth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request.arguments = lambda: request.values
        request.get = lambda key: request.values.get(key)

        if is_valid_request(request):
            try:
                consumer, token, parameters = validate_token(request)
                if consumer and token:
                    return func(*args, **kwargs)
            except OAuthError, e:
                return oauth_error(e)

        return oauth_error(OAuthError("Invalid OAuth parameters"))
    return wrapper

def oauth_error(e):
    return current_app.response_class(e.message, status=401, headers=build_authenticate_header(realm="http://www.khanacademy.org"))

