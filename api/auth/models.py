import datetime
import logging

from google.appengine.ext import db

import util
from api.auth.auth_util import append_url_params

# OAuthMap creates a mapping between our OAuth credentials and our identity providers'.
class OAuthMap(db.Model):

    # Our tokens
    request_token = db.StringProperty()
    request_token_secret = db.StringProperty()
    access_token = db.StringProperty()
    access_token_secret = db.StringProperty()
    verifier = db.StringProperty()

    # Facebook tokens
    facebook_authorization_code = db.StringProperty()
    facebook_access_token = db.StringProperty()

    # Google tokens
    google_request_token = db.StringProperty()
    google_request_token_secret = db.StringProperty()
    google_access_token = db.StringProperty()
    google_access_token_secret = db.StringProperty()
    google_verification_code = db.StringProperty()

    # Our internal callback URL
    callback_url = db.StringProperty()

    # Our view options for interacting w/ identity providers
    # that provide special views for mobile, etc
    view = db.StringProperty(default="normal")

    # Expiration
    expires = db.DateTimeProperty()

    def uses_facebook(self):
        return self.facebook_authorization_code

    def uses_google(self):
        return self.google_request_token

    def is_expired(self):
        return self.expires and self.expires < datetime.datetime.now()

    def is_mobile_view(self):
        return self.view == "mobile"

    def callback_url_with_request_token_params(self, include_verifier = False):
        params_callback = {
            "oauth_token": self.request_token, 
            "oauth_token_secret": self.request_token_secret
        }
        
        if include_verifier and self.verifier:
            params_callback["verifier"] = self.verifier

        return append_url_params(self.callback_url, params_callback)

    def get_user(self):
        if self.uses_google():
            return get_google_user_from_oauth_map(self)
        else:
            return get_facebook_user_from_oauth_map(self)

    @staticmethod
    def if_not_expired(oauth_map):
        if oauth_map and oauth_map.is_expired():
            logging.warning("Not returning expired OAuthMap.")
            return None
        return oauth_map

    @staticmethod
    def get_by_id_safe(request_id):
        if not request_id:
            return None
        try:
            parsed_id = int(request_id)
        except ValueError:
            return None
        logging.critical("A")
        return OAuthMap.if_not_expired(OAuthMap.get_by_id(parsed_id))

    @staticmethod
    def get_from_request_token(request_token):
        if not request_token:
            return None
        return OAuthMap.if_not_expired(OAuthMap.all().filter("request_token =", request_token).get())

    @staticmethod
    def get_from_access_token(access_token):
        if not access_token:
            return None
        return OAuthMap.if_not_expired(OAuthMap.all().filter("access_token =", access_token).get())

from api.auth.google_util import get_google_user_from_oauth_map
from ..facebook_util import get_facebook_user_from_oauth_map
