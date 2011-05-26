import datetime
import logging

from google.appengine.ext import db

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

    # Our internal callback URL
    callback_url = db.StringProperty()

    # Expiration
    expires = db.DateTimeProperty()

    def uses_facebook(self):
        return self.facebook_authorization_code

    def uses_google(self):
        return self.google_request_token

    def is_expired(self):
        return self.expires and self.expires < datetime.datetime.now()

    def callback_url_with_request_token_params(self, include_verifier = False):
        params_callback = {
            "request_token": self.request_token, 
            "token_secret": self.request_token_secret
        }
        
        if include_verifier:
            params_callback["verifier"] = self.verifier

        return append_url_params(self.callback_url, params_callback)

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


