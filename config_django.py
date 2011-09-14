import os

from google.appengine.dist import use_library
use_library('django', '0.96')

import django.conf

ORIG_TEMPLATE_DIRS = (os.path.dirname(__file__),)

try:
    django.conf.settings.configure(
        DEBUG=False,
        TEMPLATE_DEBUG=False,
        TEMPLATE_LOADERS=(
          'django.template.loaders.filesystem.load_template_source',
        ),
        TEMPLATE_DIRS=ORIG_TEMPLATE_DIRS
    )
except EnvironmentError:
    pass

# monkey patch webapp.template.load to fix the following issue:
# http://code.google.com/p/googleappengine/issues/detail?id=1520
from google.appengine.ext.webapp import template

def _swap_settings_override(new):
    settings = django.conf.settings
    old = {}
    for key, value in new.iteritems():
        old[key] = getattr(settings, key, None)
        if key == 'TEMPLATE_DIRS' and value[-len(ORIG_TEMPLATE_DIRS):] != ORIG_TEMPLATE_DIRS:
            value = value + ORIG_TEMPLATE_DIRS
        setattr(settings, key, value)
    return old

template._swap_settings = _swap_settings_override

# Jinja2 config

from webapp2_extras import jinja2

from api.auth.xsrf import render_xsrf_js
from phantom_users.templatetags import login_notifications
from js_css_packages.templatetags import css_package, js_package
from badges.templatetags import badge_notifications

# TODO: tweak config for production speed
# TODO: globals 'custom tag' loading
# TODO: combine some macros into single files (user_points, user_info, etc)

jinja2.default_config = {
    'template_path': 'templates', 
    'force_compiled': False, 
    'globals': {
        "css_package": css_package,
        "js_package": js_package,
        "render_xsrf_js": render_xsrf_js,
        "login_notifications": login_notifications,
        "badge_notifications": badge_notifications,
    }, 
    'filters': None, 
    'environment_args': {
        'autoescape': False, 
        'extensions': []
        }, 
    'compiled_path': None
    }


