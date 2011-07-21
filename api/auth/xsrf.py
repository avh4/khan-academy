
import datetime
import cookie_util
import base64
import os
from functools import wraps
import logging

XSRF_COOKIE_KEY = "fkey"
XSRF_HEADER_KEY = "HTTP_X_KA_FKEY"

def ensure_xsrf_cookie(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        if not get_xsrf_cookie_value():

            xsrf_value = base64.urlsafe_b64encode(os.urandom(30))

            # Set an http-only cookie containing the XSRF value.
            # A matching header value will be required by validate_xsrf_cookie.
            self.set_cookie(XSRF_COOKIE_KEY, xsrf_value, httponly=True)
            cookie_util.set_request_cookie(XSRF_COOKIE_KEY, xsrf_value)

        return func(self, *args, **kwargs)

    return wrapper

def get_xsrf_cookie_value():
    return cookie_util.get_cookie_value(XSRF_COOKIE_KEY)

def validate_xsrf_value():
    header_value = os.environ.get(XSRF_HEADER_KEY)
    return header_value and header_value == get_xsrf_cookie_value()

def render_xsrf_js():
    return "<script>var fkey = '%s';</script>" % get_xsrf_cookie_value();

