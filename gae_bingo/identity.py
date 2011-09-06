from __future__ import absolute_import

import base64
import random

from google.appengine.ext import db

from gae_bingo import cookies
from models import UserData
from .models import GAEBingoIdentityModel

def unique_bingo_identity():
    # This should return either:
    #       A) a db.Model that identifies the current user, or
    #       B) a unique string that consistently identifies the current user
    #
    # Ideally, this should be connected to your app's existing identity system.
    # If this function returns None, gae_bingo will automatically use a random unique identifier.
    #
    # To get the strongest identity tracking, return a model that inherits from GaeBingoIdentityModel.
    # See docs for details.

    # Examples:
    #   return models.UserData.current()
    #         or
    #   return users.get_current_user().unique_id() if users.get_current_user() else None

    # TODO: clean up this file for open source version
    return UserData.current()

IDENTITY_CACHE = None
IDENTITY_COOKIE_KEY = "gae_b_id"

def identity():
    global IDENTITY_CACHE

    if IDENTITY_CACHE is None:
        # Try to get unique (hopefully persistent) identity from user's implementation,
        # otherwise grab the current cookie value, otherwise grab random value.
        IDENTITY_CACHE = str(get_unique_bingo_identity_value() or get_identity_cookie_value() or get_random_identity_value())

    return IDENTITY_CACHE

def get_unique_bingo_identity_value():
    val = unique_bingo_identity()

    if val is None:
        return None

    if isinstance(val, db.Model):

        if isinstance(val, GAEBingoIdentityModel):
            # If it's a db.Model that inherited from GAEBingoIdentityModel, return bingo identity
            return val.gae_bingo_identity

        # If it's just a normal db instance, just use its unique key
        return str(val.key())

    # Otherwise it's just a plain unique string
    return str(val)

def get_random_identity_value():
    return random.randint(0, 10 ** 10)

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
