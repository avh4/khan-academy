# import the webapp module
import re
from google.appengine.ext import webapp
from google.appengine.api import users
from django import template
from django.template.defaultfilters import linebreaksbr
from django.template.defaultfilters import timesince

import models
from comments import video_comments_context
from qa import video_qa_context

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

@register.inclusion_tag("discussion/video_comments.html")
def video_comments(video, page=0):
    return video_comments_context(video, page)

@register.inclusion_tag("discussion/video_qa.html")
def video_qa(video, page=0, qa_expand_id=None):
    return video_qa_context(video, page, qa_expand_id)

@register.inclusion_tag(("discussion/signature.html", "signature.html"))
def signature(author, date, key, verb=None):
    return {"author": author, "date": date, "key": key, "verb": verb, "is_admin": users.is_current_user_admin()}

@register.inclusion_tag(("discussion/question_answers.html", "question_answers.html"))
def question_answers(answers):
    return {"answers": answers}

@register.inclusion_tag(("discussion/honeypots.html", "honeypots.html"))
def honeypots():
    # Honeypots are used to attact spam bots
    return {}

@register.filter
def youtube_timestamp_links(content):
    dict_replaced = {}
    html_template = "<span class='youTube' seconds='%s'>%s</span>"

    for match in re.finditer("(\d+:\d{2})", content):
        time = match.group(0)

        if not dict_replaced.has_key(time):
            rg_time = time.split(":")
            minutes = int(rg_time[0])
            seconds = int(rg_time[1])
            html_link = html_template % ((minutes * 60) + seconds, time)
            content = content.replace(time, html_link)
            dict_replaced[time] = True

    return content

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
def timesince_ago(content):
    if not content:
        return ""
    return re.sub("^0 minutes ago", "just now", timesince(content) + " ago")
