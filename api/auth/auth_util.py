import cgi
import urllib
import urllib2

import flask
from flask import current_app, redirect

from oauth_provider.oauth import build_authenticate_header

# Patch up a flask request object to behave a little more like webapp.RequestHandler
# for the sake of our 3rd party oauth_provider library
def webapp_patched_request(request):
    request.arguments = lambda: request.values
    request.get = lambda key: request.values.get(key)
    return request

def oauth_error_response(e):
    return current_app.response_class("OAuth error. %s" % e.message, status=401, headers=build_authenticate_header(realm="http://www.khanacademy.org"))

def authorize_token_redirect(oauth_map, ka_callback_url):
    params = {
        "oauth_token": oauth_map.request_token,
        "oauth_token_secret": oauth_map.request_token_secret,
        "oauth_callback": ka_callback_url,
    }
    return redirect(append_url_params("http://localhost:8084/api/auth/authorize", params))

def current_oauth_map():
    if hasattr(flask.g, "oauth_map"):
        return flask.g.oauth_map
    return None

def get_response(url, params={}):
    url = append_url_params(url, params)

    response = ""
    file = None
    try:
        file = urllib2.urlopen(url)
        response = file.read()
    finally:
        if file:
            file.close()

    return response

def append_url_params(url, params={}):
    if params:
        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += urllib.urlencode(params)
    return url

def get_parsed_params(resp):
    if not resp:
        return {}
    return cgi.parse_qs(resp)

