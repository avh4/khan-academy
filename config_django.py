import os

from google.appengine.dist import use_library
use_library('django', '0.96')

import django.conf

try:
    django.conf.settings.configure(
        DEBUG=False,
        TEMPLATE_DEBUG=False,
        TEMPLATE_LOADERS=(
          'django.template.loaders.filesystem.load_template_source',
        ),
        TEMPLATE_DIRS=(os.path.dirname(__file__),)
    )
except EnvironmentError:
    pass

