import cgi
import logging
import urllib
import urlparse

from google.appengine.api import urlfetch

import flask
from flask import current_app, request, redirect

from oauth_provider.oauth import build_authenticate_header, OAuthError

def oauth_error_response(e):
    logging.error("Returning oauth_error: %s" % e.message)
    return current_app.response_class("OAuth error. %s" % e.message, status=401, headers=build_authenticate_header(realm="http://www.khanacademy.org"))

def access_token_response(oauth_map):
    if not oauth_map:
        raise OAuthError("Missing oauth_map while returning access_token_response")

    return "oauth_token=%s&oauth_token_secret=%s" % (oauth_map.access_token, oauth_map.access_token_secret)

def authorize_token_redirect(oauth_map):
    if not oauth_map:
        raise OAuthError("Missing oauth_map while returning authorize_token_redirect")

    if not oauth_map.callback_url:
        raise OAuthError("Missing callback URL during authorize_token_redirect")

    params = {
        "oauth_token": oauth_map.request_token,
        "oauth_token_secret": oauth_map.request_token_secret,
        "oauth_callback": oauth_map.callback_url_with_request_token_params(),
    }
    return redirect(append_url_params("/api/auth/authorize", params))

def custom_scheme_redirect(url_redirect):
    # urlparse.urlsplit doesn't currently handle custom schemes,
    # which we want our callback URLs to support so mobile apps can register
    # their own callback scheme handlers.
    # See http://bugs.python.org/issue9374
    # and http://stackoverflow.com/questions/1417958/parse-custom-uris-with-urlparse-python

    scheme = urlparse.urlsplit(url_redirect)[0]

    scheme_lists = [urlparse.uses_netloc, urlparse.uses_query, urlparse.uses_fragment, urlparse.uses_params, urlparse.uses_relative]
    scheme_lists_modified = []

    # Modify urlparse's internal scheme lists so it properly handles custom schemes
    if scheme:
        for scheme_list in scheme_lists:
            if scheme not in scheme_list:
                scheme_list.append(scheme)
                scheme_lists_modified.append(scheme_list)

    # Clear cache before re-parsing url_redirect
    urlparse.clear_cache()

    # Grab flask/werkzeug redirect result
    redirect_result = redirect(url_redirect)

    # Restore previous urlparse scheme list
    for scheme_list in scheme_lists_modified:
        scheme_list.remove(scheme)

    return redirect_result

def requested_oauth_callback():
    return request.values.get("oauth_callback") or ("%sapi/auth/default_callback" % request.host_url)

def current_oauth_map():
    if hasattr(flask.g, "oauth_map"):
        return flask.g.oauth_map
    return None

def get_response(url, params={}):
    url_with_params = append_url_params(url, params)

    result = None
    try:
        result = urlfetch.fetch(url_with_params, deadline=10)
    except urlfetch.DownloadError, e:
        raise OAuthError("Error in get_response for url %s, urlfetch download error: %s" % (url, e.message))

    if result:
        if result.status_code == 200:
            return result.content
        else:
            raise OAuthError("Error in get_response, received status %s for url %s" % (result.status_code, url))

    return ""

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

