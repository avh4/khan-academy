import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from gae_mini_profiler import profiler

register = webapp.template.create_template_register()

@register.simple_tag
def profiler_includes():
    if not profiler.request_id:
        return ""

    path = os.path.join(os.path.dirname(__file__), "includes.html")
    return template.render(path, {
        "request_id": profiler.request_id,
        "js_path": "/javascript/gae_mini_profiler/profiler.js",
        "css_path": "/stylesheets/gae_mini_profiler/profiler.css",
    })


