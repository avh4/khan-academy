from google.appengine.ext import webapp

from app import App
from js_css_packages import packages
import util

import template_cached
register = template_cached.create_template_register()

@register.simple_tag
def js_package(package_name):
    package = packages.javascript[package_name]
    src_dir = "/javascript/%s-package" % package_name

    if App.is_dev_server:
        list_js = []
        for filename in package["files"]:
            list_js.append("<script type='text/javascript' src='%s/%s'></script>" % (src_dir, filename))
        return "".join(list_js)
    else:
        return "<script type='text/javascript' src='%s/%s'></script>" % (util.static_url(src_dir), package["hashed-filename"])

@register.simple_tag
def css_package(package_name):
    package = packages.stylesheets[package_name]
    src_dir = "/stylesheets/%s-package" % package_name

    if App.is_dev_server:
        list_css = []
        for filename in package["files"]:
            list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" % (src_dir, filename))
        return "".join(list_css)
    else:
        return "<link rel='stylesheet' type='text/css' href='%s/%s'/>" % (util.static_url(src_dir), package["hashed-filename"])
