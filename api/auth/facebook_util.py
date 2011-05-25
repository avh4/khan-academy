import datetime
import logging
import urllib

from flask import request, redirect

from app import App

from api import route
from api.auth.auth_util import oauth_error_response, get_response, get_parsed_params, append_url_params, authorize_token_redirect
from api.auth.models import OAuthMap

KA_URL_BASE = "http://local.kamenstestapp.appspot.com:8084"
FB_URL_OAUTH_DIALOG = "https://www.facebook.com/dialog/oauth"
FB_URL_ACCESS_TOKEN = "https://graph.facebook.com/oauth/access_token"

def facebook_request_token_handler(oauth_map):
    # Start Facebook request token process
    ka_callback_url = request.values.get("oauth_callback")

    params = {
                "client_id": App.facebook_app_id,
                "redirect_uri": get_facebook_token_callback_url(oauth_map, ka_callback_url),
            }

    return redirect("%s?%s" % (FB_URL_OAUTH_DIALOG, urllib.urlencode(params)))

def facebook_access_token_handler(oauth_map):
    # Start Facebook access token process
    ka_callback_url = request.values.get("oauth_callback")

    params = {
                "client_id": App.facebook_app_id,
                "client_secret": App.facebook_app_secret,
                "redirect_uri": get_facebook_token_callback_url(oauth_map, ka_callback_url),
                "code": oauth_map.facebook_authorization_code,
                }

    try:
        response = get_response(FB_URL_ACCESS_TOKEN, params)
    except Exception, e:
        return oauth_error_response(OAuthError(e.message))

    response_params = get_parsed_params(response)
    if not response_params or not response_params.get("access_token"):
        return oauth_error_response(OAuthError("Cannot get access_token from Facebook's /oauth/access_token response"))
     
    # Associate our access token and Google/Facebook's
    oauth_map.facebook_access_token = response_params["access_token"][0]

    expires_seconds = 0
    try:
        expires_seconds = int(response_params["expires"][0])
    except ValueError:
        pass

    if expires_seconds:
        oauth_map.expires = datetime.datetime.now() + datetime.timedelta(seconds=expires_seconds)
    oauth_map.put()

    return "NEED TO REDIRECT HERE. access_token=%s&token_secret=%s" % (oauth_map.access_token, oauth_map.access_token_secret)

# Associate our request or access token with Facebook's tokens
@route("/api/auth/facebook_token_callback", methods=["GET"])
def facebook_token_callback():
    oauth_map = OAuthMap.get_by_id_safe(request.values.get("oauth_map_id"))
    ka_callback_url = request.values.get("oauth_callback")

    if not oauth_map:
        return oauth_error_response(OAuthError("Unable to find OAuthMap by id."))

    if not oauth_map.facebook_authorization_code:
        oauth_map.facebook_authorization_code = request.values.get("code")
        oauth_map.put()

    ka_callback_url = append_url_params(ka_callback_url, {"request_token": oauth_map.request_token, "token_secret": oauth_map.request_token_secret})
    return authorize_token_redirect(oauth_map, ka_callback_url)

def get_facebook_token_callback_url(oauth_map, ka_callback_url):
    return "%s/api/auth/facebook_token_callback?oauth_map_id=%s&oauth_callback=%s" % (KA_URL_BASE, oauth_map.key().id(), ka_callback_url)
