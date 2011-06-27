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

        func = allow_cross_origin(func)

        # Fix endpoint names for decorated functions by using the rule for names
        return api_app.add_url_rule(rule, rule, func, **options)

    return api_route_wrap

def allow_cross_origin(func):
    @wraps(func)
    def cross_origin_allowed(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, current_app.response_class):
            result.headers["Access-Control-Allow-Origin"] = "*"

        return result

    return cross_origin_allowed
