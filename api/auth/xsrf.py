
import datetime
import cookie_util
import os
from functools import wraps
import logging

XSRF_COOKIE_KEY = "fkey"
XSRF_HEADER_KEY = ""

def ensure_xsrf_cookie(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        logging.critical(os.environ)
        if not get_xsrf_cookie():

            xsrf_value = str(datetime.datetime.now())

            # Set an http-only cookie containing the XSRF value.
            # A matching header value will be required by validate_xsrf_cookie.
            self.set_cookie(XSRF_COOKIE_KEY, xsrf_value, httponly=True)
            cookie_util.set_request_cookie(XSRF_COOKIE_KEY, xsrf_value)

        return func(self, *args, **kwargs)

    return wrapper

def get_xsrf_cookie():
    return cookie_util.get_cookie_value(XSRF_COOKIE_KEY)

def validate_xsrf_cookie():

    header_value = os.environ.get

    pass # os.environ magic

def render_xsrf_js():
    pass # templatetag magic
