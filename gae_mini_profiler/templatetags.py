import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from gae_mini_profiler import profiler

register = webapp.template.create_template_register()

@register.simple_tag
def profiler_includes():
    if not profiler.request_id:
        return ""

    path = os.path.join(os.path.dirname(__file__), "templates/includes.html")
    return template.render(path, {
        "request_id": profiler.request_id,
        "js_path": "/gae_mini_profiler/static/js/profiler.js",
        "css_path": "/gae_mini_profiler/static/css/profiler.css",
    })

