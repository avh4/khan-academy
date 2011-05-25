import datetime
import logging
import urllib

from flask import request, redirect

from app import App

from api import route
from api.auth.auth_util import oauth_error_response, get_response, get_parsed_params
from api.auth.models import OAuthMap

def facebook_request_token_handler(oauth_map):
    # Start Facebook request token process
    params = {
                "client_id": App.facebook_app_id,
                "redirect_uri": "http://local.kamenstestapp.appspot.com:8084/api/auth/facebook_token_callback?oauth_map_id=%s" % oauth_map.key().id(),
            }
    return redirect("https://www.facebook.com/dialog/oauth?%s" % urllib.urlencode(params))

def facebook_access_token_handler(oauth_map):
    # Start Facebook access token process

    continue_url = "http://local.kamenstestapp.appspot.com:8084/api/auth/facebook_token_callback?oauth_map_id=%s" % oauth_map.key().id()

    params = {
                "client_id": App.facebook_app_id,
                "client_secret": App.facebook_app_secret,
                "redirect_uri": continue_url,
                "code": oauth_map.facebook_authorization_code,
                }

    try:
        response = get_response("https://graph.facebook.com/oauth/access_token", params)
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

    if not oauth_map:
        return oauth_error_response(OAuthError("Unable to find OAuthMap by id."))

    if not oauth_map.facebook_authorization_code:
        oauth_map.facebook_authorization_code = request.values.get("code")
        oauth_map.put()
        return "NEED TO REDIRECT HERE. request_token=%s&token_secret=%s" % (oauth_map.request_token, oauth_map.request_token_secret)
