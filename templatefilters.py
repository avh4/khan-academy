# import the webapp module
from google.appengine.ext import webapp
from django import template

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix

register.filter(smart_truncate)

webapp.template.register_template_library('discussion.templatefilters')
