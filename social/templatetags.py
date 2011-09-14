import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from django.template.defaultfilters import pluralize

from urllib import urlencode

from templateext import escapejs

import template_cached
register = template_cached.create_template_register()
SITE_TAGLINE = "Trying to make a world-class education available to anyone, anywhere."

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_badge(desc, icon, extended_desc, activity, event_info=None):
    context = {}
    if desc and icon and extended_desc:
        context = { 'type': 'badge', 
                    'desc': desc, 
                    'icon': icon, 
                    'extended_desc': extended_desc,
                    'activity': activity, 
                    'event_info': event_info }
    return context

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_video(name, desc, youtube_id, event_info=None):
    context = {}
    if name and desc and id:
        context = { 'type': 'video',
                    'name': name,
                    'desc': desc,
                    'id': youtube_id,
                    'event_info': event_info }
    return context

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_exercise(problem_count, proficiency, name, event_info=None):
    context = {}
    if problem_count and name:
        context = { 'type': 'exercise',
                    'problem_count': problem_count, 
                    'plural': pluralize(problem_count),
                    'proficiency': ("to achieve proficiency in" if proficiency else "in"),
                    'name': name,
                    'event_info': event_info }
    return context
    
@register.inclusion_tag("social/twitter_share.html")
def twitter_share_video(title, youtube_id, event_info=None):
    context = {}
    if title and youtube_id :
        url = "http://khanacademy.org/video?v=%s" % youtube_id
        text = "just learned about %s" % title 
        context = { 'type': 'video',
                    'url': url,
                    'text': text,
                    'tagline': SITE_TAGLINE, 
                    'event-info': event_info } 
    return context
    
@register.inclusion_tag("social/twitter_share.html")
def twitter_share_badge(desc, activity, event_info=None):
    context= {}
    if desc:
        url = "http://khanacademy.org"
        text = "just earned the %s%s on" % (desc, ( "" if not activity else " in " + activity ))
        context = { 'type': 'badge',
                    'url': url,
                    'text': text,
                    'tagline': SITE_TAGLINE,
                    'event-info': event_info }
    return context

@register.inclusion_tag("social/twitter_share.html")
def twitter_share_exercise(name, problems, proficiency, event_info=None):
    context = {}
    if name and problems:
        url = "http://khanacademy.org/exercisedashboard"
        text = "just answered %s question%s right %s %s" % (problems, pluralize(problems), ( "to achieve proficiency in" if proficiency else "in" ), name)
        context = { 'url': url, 
                    'text': text,
                    'tagline': SITE_TAGLINE,
                    'event_info': event_info }
    return context

@register.inclusion_tag("social/share_button.html")
def share_video_button(video_title, description, youtube_id, event_description=None):
    context = {}
    if video_title and description and youtube_id:
        context = { 'type': 'video',
                    'video_title': video_title,
                    'description': description,
                    'youtube_id': youtube_id,
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/share_button.html")
def share_badge_button(description, icon_src, extended_description, context_name, event_description=None):
    context = {}
    if description and icon_src and extended_description:
        context = { 'type': 'badge',
                    'description': description,
                    'icon_src': icon_src,
                    'extended_description': extended_description,
                    'target_context_name': context_name,
                    'event_description': event_description }
    return context
    
@register.inclusion_tag("social/share_button.html")
def share_exercise_button(problem_count, proficiency, name, event_description=None):
    context = {}
    if problem_count and name:
        context = { 'type': 'exercise',
                    'problem_count': problem_count,
                    'proficiency': proficiency,
                    'name': name,
                    'event_description': event_description }
    return context