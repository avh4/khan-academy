# -*- coding: utf-8 -*-
import logging
import os
import shutil
import sys

def append_paths():

    os.environ["SERVER_SOFTWARE"] = ""
    os.environ["CURRENT_VERSION_ID"] = ""

    # Can only deploy on macs for now
    gae_path = "/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine"

    extra_paths = [
        os.path.abspath("."),
        gae_path,
        # These paths are required by the SDK.
        os.path.join(gae_path, 'lib', 'antlr3'),
        os.path.join(gae_path, 'lib', 'ipaddr'),
        os.path.join(gae_path, 'lib', 'webob'),
        os.path.join(gae_path, 'lib', 'simplejson'),
        os.path.join(gae_path, 'lib', 'yaml', 'lib'),
    ]

    for path in extra_paths:
        sys.path.append(path)

# Append app and GAE paths so we can simulate our app environment
# when precompiling templates (otherwise compilation will bail on errors)
#
append_paths()

# Pull in some jinja magic
from jinja2 import FileSystemLoader
import webapp2
from webapp2_extras import jinja2

# Using our app's standard jinja config so we pick up custom globals and filters
import config_django
import config_jinja

# Only compile .html files
def filter_templates(src):
    return os.path.basename(src).endswith(".html")

def compile_templates():

    src_path = os.path.join(os.path.dirname(__file__), "..", "templates")
    dest_path = os.path.join(os.path.dirname(__file__), "..", "compiled_templates.zip")

    jinja2.default_config["environment_args"]["loader"] = FileSystemLoader(src_path)

    env = jinja2.get_jinja2(app=webapp2.WSGIApplication()).environment

    try:
        shutil.rmtree(dest_path)
    except:
        pass

    env.compile_templates(dest_path, extensions=None, 
            ignore_errors=False, py_compile=False, zip='deflated',
            filter_func=filter_templates)

if __name__ == "__main__":
    compile_templates()