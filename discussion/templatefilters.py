# import the webapp module
import re
from google.appengine.ext import webapp
from django import template

import template_cached
register = template_cached.create_template_register()

@register.filter
def hash(dict, key):
    return dict[key]
