import re
import logging
import cgi
import math
from google.appengine.ext import webapp
from django import template
from django.template.defaultfilters import escape, slugify

from app import App
from templatefilters import seconds_to_time_string
import consts
import util
import topics_list

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def highlight(parser, token):
    try:
        tag_name, phrases_to_highlight, text = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly 2 arguments" % token.contents[0] 
    return HighlightNode(phrases_to_highlight, text)

class HighlightNode(template.Node):
    def __init__(self, phrases_to_highlight, text):
        self.phrases_to_highlight = phrases_to_highlight
        self.text = text
    
    def render(self, context):
        phrases = []
        text = ''
        try:
            phrases = template.resolve_variable(self.phrases_to_highlight, context)
            text = template.resolve_variable(self.text, context)
        except VariableDoesNotExist:
            pass
        phrases = [(re.escape(p)+r'\w*') for p in phrases]
        regex = re.compile("(%s)" % "|".join(phrases), re.IGNORECASE)
        text = cgi.escape(text)
        text = re.sub(regex, r'<span class="highlight">\1</span>', text)
        return text

@register.inclusion_tag("column_major_order_styles.html")
def column_major_order_styles(num_cols=3, column_width=300, gutter=20, font_size=12):
    col_list = range(0, num_cols)
    link_height = font_size * 1.5
    
    return {
        "columns": col_list,
        "font_size": font_size,
        "link_height": link_height,
        "column_width": column_width,
        "column_width_plus_gutter": column_width + gutter,
    }
@register.inclusion_tag(("column_major_order_videos.html", "../column_major_order_videos.html"))
def column_major_sorted_videos(videos, num_cols=3, column_width=300, gutter=20, font_size=12):
    items_in_column = len(videos) / num_cols
    remainder = len(videos) % num_cols
    link_height = font_size * 1.5
    current_playlist = videos[0]["playlist"].title.replace(' ', '-')
    # Calculate the column indexes (tops of columns). Since video lists won't divide evenly, distribute
    # the remainder to the left-most columns first, and correctly increment the indices for remaining columns
    column_indices = [(items_in_column * multiplier + (multiplier if multiplier <= remainder else remainder)) for multiplier in range(1, num_cols + 1)]
        
    return {
               "videos": videos,
               "column_width": column_width,
               "current_playlist": current_playlist,
               "column_indices": column_indices,
               "link_height": link_height,
               "list_height": column_indices[0] * link_height,
          }

@register.inclusion_tag(("youtube_player_embed.html", "../youtube_player_embed.html"))
def youtube_player_embed(youtube_id, width=800, height=480):
    return {"youtube_id": youtube_id, "width": width, "height": height}

@register.inclusion_tag(("flv_player_embed.html", "../flv_player_embed.html"))
def flv_player_embed(video_path, width=800, height=480, exercise_video=None):
    if exercise_video:
        video_path = video_path + exercise_video.video_folder + "/" + exercise_video.readable_id + ".flv"
    return {"video_path": video_path, "width": width, "height": height}

@register.inclusion_tag(("knowledgemap_embed.html", "../knowledgemap_embed.html"))
def knowledgemap_embed(exercises, map_coords):
    return {"App": App, "exercises": exercises, "map_coords": map_coords}

@register.inclusion_tag(("related_videos.html", "../related_videos.html"))
def related_videos_with_points(exercise_videos):
    return related_videos(exercise_videos, True)

@register.inclusion_tag(("related_videos.html", "../related_videos.html"))
def related_videos(exercise_videos, show_points=False):
    return {"exercise_videos": exercise_videos, "video_points_base": consts.VIDEO_POINTS_BASE, "show_points": show_points}

@register.inclusion_tag(("exercise_icon.html", "../exercise_icon.html"))
def exercise_icon(exercise, App):
    s_prefix = "proficient-badge"
    if exercise.summative:
        s_prefix = "challenge"

    src = ""
    if exercise.review:
        src = "/images/proficient-badge-review.png" # No reviews for summative exercises yet
    elif exercise.suggested:
        src = "/images/%s-suggested.png" % s_prefix
    elif exercise.proficient:
        src = "/images/%s-complete.png" % s_prefix
    else:
        src = "/images/%s-not-started.png" % s_prefix

    return {"src": src, "version": App.version }

@register.inclusion_tag("exercise_message.html")
def exercise_message(exercise, coaches, exercise_states):
    return dict({"exercise": exercise, "coaches": coaches}, **exercise_states)

@register.inclusion_tag(("user_points.html", "../user_points.html"))
def user_points(user_data):
    if user_data:
        points = user_data.points
    else:
        points = 0
    return {"points": points}

@register.inclusion_tag(("possible_points_badge.html", "../possible_points_badge.html"))
def possible_points_badge(points, possible_points):
    return {"points": points, "possible_points": possible_points}

@register.inclusion_tag(("simple_student_info.html", "../simple_student_info.html"))
def simple_student_info(user_data):
    coach_count = len(user_data.coaches)

    return { 
            "first_coach": user_data.coaches[0] if coach_count >= 1 else None,
            "additional_coaches": coach_count - 1 if coach_count > 1 else None,
            "member_for": seconds_to_time_string(util.seconds_since(user_data.joined), show_hours=False),
           }

@register.inclusion_tag(("streak_bar.html", "../streak_bar.html"))
def streak_bar(user_exercise):

    streak = user_exercise.streak
    longest_streak = 0

    if hasattr(user_exercise, "longest_streak"):
        longest_streak = user_exercise.longest_streak

    streak_max_width = 228

    streak_width = min(streak_max_width, math.ceil((streak_max_width / float(user_exercise.required_streak())) * streak))
    longest_streak_width = min(streak_max_width, math.ceil((streak_max_width / float(user_exercise.required_streak())) * longest_streak))
    streak_icon_width = min(streak_max_width - 2, max(43, streak_width)) # 43 is width of streak icon

    width_required_for_label = 20
    show_streak_label = streak_width > width_required_for_label
    show_longest_streak_label = longest_streak_width > width_required_for_label and (longest_streak_width - streak_width) > width_required_for_label

    levels = []
    if user_exercise.summative:
        c_levels = user_exercise.required_streak() / consts.REQUIRED_STREAK
        level_offset = streak_max_width / float(c_levels)
        for ix in range(c_levels - 1):
            levels.append(math.ceil((ix + 1) * level_offset) + 1)
    else:
        if streak > consts.MAX_STREAK_SHOWN:
            streak = "Max"

        if longest_streak > consts.MAX_STREAK_SHOWN:
            longest_streak = "Max"

    return {
            "streak": streak,
            "longest_streak": longest_streak,
            "streak_width": streak_width, 
            "longest_streak_width": longest_streak_width, 
            "streak_max_width": streak_max_width,
            "streak_icon_width": streak_icon_width,
            "show_streak_label": show_streak_label,
            "show_longest_streak_label": show_longest_streak_label,
            "levels": levels
            }

@register.inclusion_tag(("reports_navigation.html", "../reports_navigation.html"))
def reports_navigation(coach_email, current_report="classreport"):
    return {'coach_email': coach_email, 'current_report': current_report }
    
@register.inclusion_tag(("playlist_browser.html", "../playlist_browser.html"))
def playlist_browser(browser_id):
    return {'browser_id': browser_id, 'playlist_structure': topics_list.PLAYLIST_STRUCTURE}

@register.simple_tag
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
            elif playlist_title.startswith("GMAT"):
                href = "/gmat"

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

@register.simple_tag
def static_url(relative_url):
    return util.static_url(relative_url)

@register.inclusion_tag(("empty_class_instructions.html", "../empty_class_instructions.html"))
def empty_class_instructions(class_is_empty=True):
    user = util.get_current_user()
    coach_email = "Not signed in. Please sign in to see your Coach ID."
    if user:
        coach_email = user.email()
            
    return {'App': App, 'class_is_empty': class_is_empty, 'coach_email': coach_email }

register.tag(highlight)

webapp.template.register_template_library('templatetags')    
webapp.template.register_template_library('discussion.templatetags')
webapp.template.register_template_library('badges.templatetags')
webapp.template.register_template_library('profiles.templatetags')
webapp.template.register_template_library('mailing_lists.templatetags')
webapp.template.register_template_library('js_css_packages.templatetags')

