from google.appengine.ext import webapp

from app import App
from js_css_packages import packages
import util

import template_cached
register = template_cached.create_template_register()

@register.simple_tag
def js_package(package_name):
    package = packages.javascript[package_name]
    base_url = package.get("base_url") or "/javascript/%s-package" % package_name

    if App.is_dev_server:
        list_js = []
        for filename in package["files"]:
            list_js.append("<script type='text/javascript' src='%s/%s'></script>" % (base_url, filename))
        return "".join(list_js)
    else:
        return "<script type='text/javascript' src='%s/%s'></script>" % (util.static_url(base_url), package["hashed-filename"])

@register.simple_tag
def css_package(package_name):
    package = packages.stylesheets[package_name]
    base_url = package.get("base_url") or "/stylesheets/%s-package" % package_name

    list_css = []

    if App.is_dev_server:
        for filename in package["files"]:
            list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
                % (base_url, filename))
    elif package_name+'-non-ie' not in packages.stylesheets:
        list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
            % (util.static_url(base_url), package["hashed-filename"]))
    else:
        # Thank you Jammit (https://github.com/documentcloud/jammit) for the
        # conditional comments.
        non_ie_package = packages.stylesheets[package_name+'-non-ie']

        list_css.append("<!--[if (!IE)|(gte IE 8)]><!-->")

        # Stylesheets using data-uris
        list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
            % (util.static_url(base_url), non_ie_package["hashed-filename"]))

        list_css.append("<!--<![endif]-->")
        list_css.append("<!--[if lte IE 7]>")

        # Without data-uris, for IE <= 7
        list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
            % (util.static_url(base_url), package["hashed-filename"]))

        list_css.append("<![endif]-->")

    return "".join(list_css)
