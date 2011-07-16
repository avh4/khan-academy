from google.appengine.ext import webapp

from app import App
from js_css_packages import packages
import util

register = webapp.template.create_template_register()

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

    ie_package = packages.stylesheets[package_name+'-ie']

    list_css = []
    list_css.append("<!--[if (!IE)|(gte IE 8)]><!-->")

    if App.is_dev_server:
        for filename in package["files"]:
            list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
                % (src_dir, filename))
    else:
        list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
            % (util.static_url(src_dir), package["hashed-filename"]))

    list_css.append("<!--<![endif]-->")
    list_css.append("<!--[if lte IE 7]>")

    if App.is_dev_server:
        for filename in ie_package["files"]:
            list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
                % (src_dir, filename))
    else:
        list_css.append("<link rel='stylesheet' type='text/css' href='%s/%s'/>" \
            % (util.static_url(src_dir), ie_package["hashed-filename"]))

    list_css.append("<![endif]-->")
    return "".join(list_css)
