# import the webapp module
import re
from google.appengine.ext import webapp
from google.appengine.api import users
from django import template
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
    html_template = "<span class='youTube' seconds='{0}'>{1}</span>"

    for match in re.finditer("(\d+:\d{2})", content):
        time = match.group(0)

        if not dict_replaced.has_key(time):
            rg_time = time.split(":")
            minutes = int(rg_time[0])
            seconds = int(rg_time[1])
            html_link = html_template.format((minutes * 60) + seconds, time)
            content = content.replace(time, html_link)
            dict_replaced[time] = True

    return content


@register.filter
def timesince_ago(content):
    if not content:
        return ""
    return re.sub("^0 minutes ago", "just now", timesince(content) + " ago")
