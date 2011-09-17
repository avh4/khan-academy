# Jinja2 config

from webapp2_extras import jinja2

from urllib import quote_plus
import simplejson as json

from models import UserData
from templateext import escapejs
from templatetags import playlist_browser, column_major_sorted_videos, streak_bar
from templatefilters import slugify, find_column_index, column_height, in_list
from api.auth.xsrf import render_xsrf_js
from phantom_users.templatetags import login_notifications
from js_css_packages.templatetags import css_package, js_package
from badges.templatetags import badge_notifications, badge_counts
from gae_mini_profiler.templatetags import profiler_includes
from mailing_lists.templatetags import mailing_list_signup_form
from discussion.templatetags import video_comments, video_qa
from util import static_url, thousands_separated_number, create_login_url
from app import App

# TODO: globals "custom tag" loading

jinja2.default_config = {
    "template_path": "templates", 
    "compiled_path": "compiled_templates.zip",
    "force_compiled": not App.is_dev_server, # Only use compiled templates in production 
    "cache_size": 0 if App.is_dev_server else -1, # Only cache in production
    "auto_reload": App.is_dev_server, # Don't check for template updates in production
    "globals": {
        "css_package": css_package,
        "js_package": js_package,
        "render_xsrf_js": render_xsrf_js,
        "login_notifications": login_notifications,
        "badge_notifications": badge_notifications,
        "badge_counts": badge_counts,
        "profiler_includes": profiler_includes,
        "mailing_list_signup_form": mailing_list_signup_form,
        "playlist_browser": playlist_browser,
        "column_major_sorted_videos": column_major_sorted_videos,
        "streak_bar": streak_bar,
        "UserData": UserData,
        "hash": hash,
        "json": json,
        "App": App,
    }, 
    "filters": {
        "escapejs": escapejs,
        "urlencode": lambda s: quote_plus(s or ""),
        "static_url": static_url,
        "login_url": create_login_url,
        "slugify": slugify,
        "find_column_index": find_column_index,
        "in_list": in_list,
        "column_height": column_height,
        "thousands_separated": thousands_separated_number,
    }, 
    "environment_args": {
        "autoescape": False, 
        "extensions": [],
        }, 
    }

