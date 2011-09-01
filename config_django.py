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
