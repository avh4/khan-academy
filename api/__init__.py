import sys, os
import logging
from functools import wraps

from app import App

package_dir = os.path.abspath(os.path.join(__file__, "..", "packages"))

# Allow unzipped packages to be imported
# from packages folder
sys.path.insert(0, package_dir)

# Append zip archives to path for zipimport
for filename in os.listdir(package_dir):
    if filename.endswith((".zip", ".egg")):
        sys.path.insert(0, "%s/%s" % (package_dir, filename))

from flask import Flask
from flask import current_app

api_app = Flask('api')
api_app.secret_key = App.flask_secret_key

def route(rule, **options):
    def api_route_wrap(func):

        func = format_api_errors(func)
        func = allow_cross_origin(func)
        func = add_api_header(func)

        rule_desc = rule
        for key in options:
            rule_desc += "[%s=%s]" % (key, options[key])

        # Fix endpoint names for decorated functions by using the rule for names
        return api_app.add_url_rule(rule, rule_desc, func, **options)

    return api_route_wrap

def add_api_header(func):
    @wraps(func)
    def api_header_added(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, current_app.response_class):
            result.headers["X-KA-API-Response"] = "true"

        return result

    return api_header_added

def allow_cross_origin(func):
    @wraps(func)
    def cross_origin_allowed(*args, **kwargs):
        result = func(*args, **kwargs)

        # Let our mobile apps make API calls from their local files, and rely on oauth for security
        if isinstance(result, current_app.response_class):
            result.headers["Access-Control-Allow-Origin"] = os.environ.get("HTTP_ORIGIN") or "*"
            result.headers["Access-Control-Allow-Credentials"] = "true"

        return result

    return cross_origin_allowed

def format_api_errors(func):
    @wraps(func)
    def api_errors_formatted(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            # If any exception makes it all the way up to the top of an API request,
            # send possibly helpful message down for consumer
            logging.exception(e)
            return current_app.response_class("API error. %s" % e.message, status=500)

    return api_errors_formatted
