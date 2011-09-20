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
BASE_VIDEO_URL = "http://khanacademy.org/video?v=%s"
BASE_EXERCISE_URL = "http://khanacademy.org/exercisedashboard"
BASE_BADGE_URL = "http://khanacademy.org/"

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_badge(desc, icon, extended_desc, activity, event_description=None):
    context = {}
    if desc and icon and extended_desc:
        context = { 'type': 'badge', 
                    'desc': desc, 
                    'icon': icon, 
                    'extended_desc': extended_desc,
                    'activity': activity, 
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_video(name, desc, youtube_id, event_description=None):
    context = {}
    if name and desc and id:
        context = { 'type': 'video',
                    'name': name,
                    'desc': desc,
                    'id': youtube_id,
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/facebook_share.html")
def facebook_share_exercise(problem_count, proficiency, name, event_description=None):
    context = {}
    if problem_count and name:
        context = { 'type': 'exercise',
                    'problem_count': problem_count, 
                    'plural': pluralize(problem_count),
                    'proficiency': ("to achieve proficiency in" if proficiency else "in"),
                    'name': name,
                    'event_description': event_description }
    return context
    
@register.inclusion_tag("social/twitter_share.html")
def twitter_share_video(title, youtube_id, event_description=None):
    context = {}
    if title and youtube_id :
        url = BASE_VIDEO_URL % youtube_id
        text = "just learned about %s" % title 
        context = { 'type': 'video',
                    'url': url,
                    'text': text,
                    'tagline': SITE_TAGLINE, 
                    'event_description': event_description } 
    return context
    
@register.inclusion_tag("social/twitter_share.html")
def twitter_share_badge(desc, activity, event_description=None):
    context= {}
    if desc:
        url = BASE_BADGE_URL
        text = "just earned the %s%s on" % (desc, ( "" if not activity else " in " + activity ))
        context = { 'type': 'badge',
                    'url': url,
                    'text': text,
                    'tagline': SITE_TAGLINE,
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/twitter_share.html")
def twitter_share_exercise(name, problems, proficiency, event_description=None):
    context = {}
    if name and problems:
        url = BASE_EXERCISE_URL
        text = "just answered %s question%s right %s %s" % (problems, pluralize(problems), ( "to achieve proficiency in" if proficiency else "in" ), name)
        context = { 'url': url, 
                    'text': text,
                    'tagline': SITE_TAGLINE,
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/email_share.html")
def email_share_video(title, youtube_id, event_description=None):
    contex = {}
    if title and youtube_id:
        subject = "I just learned about %s on Khan Academy" % title
        body = "You can learn about it too. Check out %s" % ( BASE_VIDEO_URL % youtube_id )
        context = { 'subject': subject,
                    'body': body,
                    'event_description': event_description }
    return context

@register.inclusion_tag("social/email_share.html")
def email_share_badge(desc, activity, event_description=None):
    contex = {}
    if desc:
        subject = "I just earned the %s %s on Khan Academy" % (desc, ( "" if not activity else "in " + activity ))
        body = "You should check it out %s" % BASE_BADGE_URL
        context = { 'subject': subject,
                    'body': body,
                    'event_description': event_description }
    return context
    
@register.inclusion_tag("social/email_share.html")
def email_share_exercise(name, problems, proficiency, event_description=None):
    contex = {}
    if name and problems:
        subject = "I was just working on about %s on Khan Academy" % name
        body = "And I answered %s question%s right %s You can try it too: %s" % (problems, pluralize(problems), ( "to earn proficiency!" if proficiency else "." ), BASE_EXERCISE_URL)
        context = { 'subject': subject,
                    'body': body,
                    'event_description': event_description }
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