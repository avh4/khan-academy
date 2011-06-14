import sys, os
import logging

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
api_app = Flask('api')
api_app.secret_key = App.flask_secret_key

def route(rule, **options):
    def fix_endpoint_names_for_decorated_functions(f):
        return api_app.add_url_rule(rule, rule, f, **options)
    return fix_endpoint_names_for_decorated_functions

