# Jinja2 config

from webapp2_extras import jinja2

from urllib import quote_plus

from api.auth.xsrf import render_xsrf_js
from phantom_users.templatetags import login_notifications
from js_css_packages.templatetags import css_package, js_package
from badges.templatetags import badge_notifications, badge_counts
from gae_mini_profiler.templatetags import profiler_includes
from mailing_lists.templatetags import mailing_list_signup_form
from templateext import escapejs
from util import static_url, thousands_separated_number
from app import App
from models import UserData

# TODO: tweak config for production speed
# TODO: globals "custom tag" loading

jinja2.default_config = {
    "template_path": "templates", 
    "force_compiled": False, 
    "globals": {
        "css_package": css_package,
        "js_package": js_package,
        "render_xsrf_js": render_xsrf_js,
        "login_notifications": login_notifications,
        "badge_notifications": badge_notifications,
        "badge_counts": badge_counts,
        "profiler_includes": profiler_includes,
        "mailing_list_signup_form": mailing_list_signup_form,
        "UserData": UserData,
        "App": App,
    }, 
    "filters": {
        "escapejs": escapejs,
        "urlencode": quote_plus,
        "static_url": static_url,
        "thousands_separated": thousands_separated_number,
    }, 
    "environment_args": {
        "autoescape": False, 
        "extensions": []
        }, 
    "compiled_path": None
    }

