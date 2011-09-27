import re
import cgi
import math
import os
import simplejson as json

from jinja2.utils import escape

from app import App
from templatefilters import seconds_to_time_string, slugify
import consts
import util
import topics_list
import models
from api.auth import xsrf
import shared_jinja

def user_info(username, user_data):
    context = {"username": username, "user_data": user_data}
    return shared_jinja.get().render_template("user_info_only.html", **context)

def column_major_sorted_videos(videos, num_cols=3, column_width=300, gutter=20, font_size=12):
    items_in_column = len(videos) / num_cols
    remainder = len(videos) % num_cols
    link_height = font_size * 1.5
    # Calculate the column indexes (tops of columns). Since video lists won't divide evenly, distribute
    # the remainder to the left-most columns first, and correctly increment the indices for remaining columns
    column_indices = [(items_in_column * multiplier + (multiplier if multiplier <= remainder else remainder)) for multiplier in range(1, num_cols + 1)]

    template_values = {
        "videos": videos,
        "column_width": column_width,
        "column_indices": column_indices,
        "link_height": link_height,
        "list_height": column_indices[0] * link_height,
    }

    return shared_jinja.get().render_template("column_major_order_videos.html", **template_values)

def exercise_message(exercise, coaches, exercise_states):
    if exercise_states['endangered']:
        state = '_endangered'
    elif exercise_states['reviewing']:
        state = '_reviewing'
    elif exercise_states['proficient']:
        state = '_proficient'
    elif exercise_states['struggling']:
        state = '_struggling'
        exercise_states['exercise_videos'] = exercise.related_videos_fetch()
    else:
        return None

    filename = "exercise_message%s.html" % state
    return shared_jinja.get().render_template(filename, **exercise_states)

def user_points(user_data):
    if user_data:
        points = user_data.points
    else:
        points = 0

    return {"points": points}

def streak_bar(user_exercise_dict):

    progress = user_exercise_dict["progress"]
    streak = user_exercise_dict["streak"]
    longest_streak = user_exercise_dict["longest_streak"]
    required_streak = user_exercise_dict["required_streak"]

    user_data = models.UserData.current()
    use_old_bar = not user_data or (user_data.progress_bar_alternative == 'original')

    bar_max_width = 227
    bar_width = min(1.0, progress) * bar_max_width

    longest_streak_width = min(bar_max_width, math.ceil((bar_max_width / float(required_streak)) * longest_streak))
    streak_icon_width = min(bar_max_width - 2, max(43, bar_width)) # 43 is width of streak icon

    width_required_for_label = 20
    show_streak_label = bar_width > width_required_for_label
    show_longest_streak_label = longest_streak_width > width_required_for_label and (longest_streak_width - bar_width) > width_required_for_label

    levels = []
    if user_exercise_dict["summative"]:
        c_levels = required_streak / consts.REQUIRED_STREAK
        level_offset = bar_max_width / float(c_levels)
        for ix in range(c_levels - 1):
            levels.append(math.ceil((ix + 1) * level_offset) + 1)
    else:
        if streak > consts.MAX_STREAK_SHOWN:
            streak = 'Max'

        if longest_streak > consts.MAX_STREAK_SHOWN:
            longest_streak = 'Max'

    def progress_display(num):
        return '%.0f%%' % math.floor(num * 100.0) if num <= consts.MAX_PROGRESS_SHOWN else 'Max'

    template_values = {
        "use_old_bar": use_old_bar,
        "streak": streak,
        "longest_streak": longest_streak,
        "longest_streak_width": longest_streak_width,
        "streak_icon_width": streak_icon_width,
        "show_streak_label": show_streak_label,
        "show_longest_streak_label": show_longest_streak_label,
        "is_suggested": user_exercise_dict["suggested"],
        "is_proficient": user_exercise_dict["proficient"],
        "float_progress": progress,
        "progress": progress_display(progress),
        "bar_width": bar_width,
        "bar_max_width": bar_max_width,
        "levels": levels
    }

    return shared_jinja.get().render_template("streak_bar.html", **template_values)

def playlist_browser(browser_id):
    template_values = {
        'browser_id': browser_id, 'playlist_structure': topics_list.PLAYLIST_STRUCTURE
    }

    return shared_jinja.get().render_template("playlist_browser.html", **template_values)

def playlist_browser_structure(structure, class_name="", level=0):
    if type(structure) == list:

        s = ""
        class_next = "topline"
        for sub_structure in structure:
            s += playlist_browser_structure(sub_structure, class_name=class_next, level=level)
            class_next = ""
        return s

    else:

        s = ""
        name = structure["name"]

        if structure.has_key("playlist"):

            playlist_title = structure["playlist"]
            href = "#%s" % escape(slugify(playlist_title))

            # We have two special case playlist URLs to worry about for now. Should remove later.
            if playlist_title.startswith("SAT"):
                href = "/sat"

            if level == 0:
                s += "<li class='solo'><a href='%s' class='menulink'>%s</a></li>" % (href, escape(name))
            else:
                s += "<li class='%s'><a href='%s'>%s</a></li>" % (class_name, href, escape(name))

        else:
            items = structure["items"]

            if level > 0:
                class_name += " sub"

            s += "<li class='%s'>%s <ul>%s</ul></li>" % (class_name, escape(name), playlist_browser_structure(items, level=level + 1))

        return s

def video_name_and_progress(video):
    return "<span class='vid-progress v%d'>%s</span>" % (video.key().id(), escape(video.title.encode('utf-8', 'ignore')))

