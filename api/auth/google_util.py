import urllib

from google.appengine.api import oauth as google_oauth
from google.appengine.api import users

from flask import request, redirect

from oauth_provider.oauth import OAuthError

import layer_cache

from api import route
from api.auth.auth_util import current_oauth_map, authorize_token_redirect, access_token_response, append_url_params, oauth_error_response
from api.auth.google_oauth_client import GoogleOAuthClient
from api.auth.models import OAuthMap

# Utility request handler to let Google authorize the OAuth token/request and 
# return the authorized user's email.
@route("/api/auth/current_google_oauth_email")
def current_google_oauth_email():
    user = google_oauth.get_current_user()
    if user:
        return user.email()
    return ""

def get_current_google_user_from_oauth():
    oauth_map = current_oauth_map()
    if oauth_map and oauth_map.uses_google():
        email = get_google_email_from_oauth_map(oauth_map)
        if email:
            return users.User(email)
    return None

@layer_cache.cache_with_key_fxn(lambda oauth_map: "google_email_from_oauth_token_%s" % oauth_map.google_access_token, layer=layer_cache.Layers.Memcache)
def get_google_email_from_oauth_map(oauth_map):
    email = ""
    try:
        google_client = GoogleOAuthClient()
        email = google_client.access_user_email(oauth_map)
    except Exception, e:
        raise OAuthError(e.message)

    return email

def google_request_token_handler(oauth_map):
    # Start Google request token process
    try:
        google_client = GoogleOAuthClient()
        google_token = google_client.fetch_request_token(oauth_map)
    except Exception, e:
        return oauth_error_response(OAuthError(e.message))

    oauth_map.google_request_token = google_token.key
    oauth_map.google_request_token_secret = google_token.secret
    oauth_map.put()

    return authorize_token_redirect(oauth_map)

def google_authorize_token_handler(oauth_map):
    params = { "oauth_token": oauth_map.google_request_token }

    if oauth_map.is_mobile_view():
        # Add google-specific mobile view identifier
        params["btmpl"] = "mobile"

    return redirect("http://www.khanacademy.org/_ah/OAuthAuthorizeToken?%s" % urllib.urlencode(params))

def google_access_token_handler(oauth_map):
    # Start Google access token process
    try:
        google_client = GoogleOAuthClient()
        google_token = google_client.fetch_access_token(oauth_map)
    except Exception, e:
        return oauth_error_response(OAuthError(e.message))

    oauth_map.google_access_token = google_token.key
    oauth_map.google_access_token_secret = google_token.secret
    oauth_map.put()

    return access_token_response(oauth_map)

@route("/api/auth/google_token_callback", methods=["GET"])
def google_token_callback():
    oauth_map = OAuthMap.get_by_id_safe(request.values.get("oauth_map_id"))

    if not oauth_map:
        return oauth_error_response(OAuthError("Unable to find OAuthMap by id."))

    if not oauth_map.google_verification_code:
        oauth_map.google_verification_code = request.values.get("oauth_verifier")
        oauth_map.put()

    return redirect(oauth_map.callback_url_with_request_token_params(include_verifier=True))
