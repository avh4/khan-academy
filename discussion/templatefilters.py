# import the webapp module
import re
from google.appengine.ext import webapp
from django import template
from django.template.defaultfilters import linebreaksbr

register = webapp.template.create_template_register()

@register.filter
def linebreaksbr_ellipsis(content, ellipsis_content = "&hellip;"):

    # After a specified number of linebreaks, apply span with a CSS class
    # to the rest of the content so it can be optionall hidden or shown
    # based on its context.
    max_linebreaks = 4

    # We use django's built-in "linebreaksbr" filter, so we don't
    # need to worry about alternate representations of the <br /> tag.
    content = linebreaksbr(content.strip())

    rg_s = re.split("<br />", content)
    if len(rg_s) > (max_linebreaks + 1):
        # More than max_linebreaks <br />'s were found.
        # Place everything after the 3rd <br /> in a hidden span that can be exposed by CSS later, and
        # Append an ellipsis at the cutoff point with a class that can also be controlled by CSS.
        rg_s[max_linebreaks] = "<span class='ellipsisExpand'>%s</span><span class='hiddenExpand'>%s" % (ellipsis_content, rg_s[max_linebreaks])
        rg_s[-1] += "</span>"

    # Join the string back up w/ its original <br />'s
    return "<br />".join(rg_s)

@register.filter
def hash(dict, key):
    return dict[key]
