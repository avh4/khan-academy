import base64
import random

import cookies

def unique_bingo_identity():
    # This should return any unique string that consistently identifies the current user.
    # You should connect this to your app's existing identity system.

    # Example:
    #   return users.get_current_user().unique_id()
    return str(random.randint(0, 10 ** 10))

IDENTITY_CACHE = None
IDENTITY_COOKIE_KEY = "gae_b_id"

def identity():
    global IDENTITY_CACHE

    if IDENTITY_CACHE is None:
        # TODO: get logged-in identity to override previously set random one
        IDENTITY_CACHE = get_identity_cookie_value() or unique_bingo_identity()
    return IDENTITY_CACHE

def get_identity_cookie_value():
    cookie_val = cookies.get_cookie_value(IDENTITY_COOKIE_KEY)

    if cookie_val:
        try:
            return base64.urlsafe_b64decode(cookie_val)
        except:
            pass

    return None

def set_identity_cookie_header():
    return cookies.set_cookie_value(IDENTITY_COOKIE_KEY, base64.urlsafe_b64encode(identity()))

def flush_identity_cache():
    global IDENTITY_CACHE
    IDENTITY_CACHE = None
