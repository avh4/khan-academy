import re
import datetime
import math

from google.appengine.ext import webapp
from django import template
from django.template.defaultfilters import timesince, pluralize

import util

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix

@register.filter
def greater_than(x, y):
    return x > y

@register.filter
def hash(h, key):
    try:
        return h[key]
    except KeyError:
        return None

@register.filter
def timesince_ago(content):
    if not content:
        return ""
    return append_ago(timesince(content))

@register.filter
def timesince_ago_short(content):
    if not content:
        return ""
    return append_ago(seconds_to_time_string(util.seconds_since(content)))

def seconds_to_time_string(seconds_init, short_display = True, show_hours = True):

    seconds = seconds_init

    years = math.floor(seconds / (86400 * 365))
    seconds -= years * (86400 * 365)

    days = math.floor(seconds / 86400)
    seconds -= days * 86400

    hours = math.floor(seconds / 3600)
    seconds -= hours * 3600

    minutes = math.floor(seconds / 60)
    seconds -= minutes * 60

    if years and days:
        return "%d year%s and %d day%s" % (years, pluralize(years), days, pluralize(days))
    elif years:
        return "%d year%s" % (years, pluralize(years))
    elif days and hours and show_hours:
        return "%d day%s and %d hour%s" % (days, pluralize(days), hours, pluralize(hours))
    elif days:
        return "%d day%s" % (days, pluralize(days))
    elif hours:
        if not short_display and minutes:
            return "%d hour%s and %d minute%s" % (hours, pluralize(hours), minutes, pluralize(minutes))
        else:
            return "%d hour%s" % (hours, pluralize(hours))
    else:
        if not short_display and seconds and not minutes:
            return "%d second%s" % (seconds, pluralize(seconds))
        return "%d minute%s" % (minutes, pluralize(minutes))

@register.filter
def utc_to_ctz(content, tz_offset):
    return content + datetime.timedelta(minutes=tz_offset)

@register.filter
def thousands_separated(content):
    return util.thousands_separated_number(content)

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
            html_link = youtube_jump_link(time, (minutes * 60) + seconds)
            content = content.replace(time, html_link)
            dict_replaced[time] = True

    return content

@register.simple_tag
def youtube_jump_link(content, seconds):
    return "<span class='youTube' seconds='%s'>%s</span>" % (seconds, content)

def append_ago(s_time):
    if not s_time:
        return ""
    return re.sub("^0 minutes ago", "just now", s_time + " ago")

def mod(content, i):
    return content % i

def multiply(x, y):
    return (x * y)
    
def in_list(content, list):
    return content in list

def find_column_index(content, column_index_list):
    for index, column_breakpoint in enumerate(column_index_list):
        if (content < column_breakpoint):
            return index
    return len(column_index_list)

def column_height(list_item_index, column_breakpoints):
    height = list_item_index
    if not column_breakpoints.index(list_item_index) == 0:
        height = list_item_index - column_breakpoints[column_breakpoints.index(list_item_index) - 1]
    return height

register.filter(smart_truncate)
register.filter(mod)
register.filter(multiply)
register.filter(in_list)
register.filter(find_column_index)
register.filter(column_height)

webapp.template.register_template_library('templatefilters')
webapp.template.register_template_library('discussion.templatefilters')
