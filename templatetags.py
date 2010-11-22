import re
import cgi
from google.appengine.ext import webapp
from django import template

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

@register.inclusion_tag("column_major_order_videos.html")
def column_major_sorted_videos(videos, num_cols=3, column_width=300, gutter=20, font_size=12):

    items_in_column = len(videos) / num_cols
    remainder = len(videos) % num_cols
    link_height = font_size * 1.5 
    # Calculate the column indexes (tops of columns). Since video lists won't divide evenly, distribute
    # the remainder to the left-most columns first, and correctly increment the indices for remaining columns
    column_indices = [(items_in_column * multiplier + (multiplier if multiplier <= remainder else remainder)) for multiplier in range(1, num_cols + 1)]
        
    return {
               "videos": videos,
               "column_width": column_width,
               "column_width_plus_gutter": column_width + gutter,
               "font_size": font_size,
               "link_height": link_height,
               "column_indices": column_indices,
               "list_height": column_indices[0] * link_height,
          }

@register.inclusion_tag("youtube_player_embed.html")
def youtube_player_embed(youtube_id, width=800, height=480):
    return {"youtube_id": youtube_id, "width": width, "height": height}

@register.inclusion_tag("flv_player_embed.html")
def flv_player_embed(video_path, width=800, height=480, exercise_video=None):
    if exercise_video:
        video_path = video_path + exercise_video.video_folder + "/" + exercise_video.readable_id + ".flv"
    return {"video_path": video_path, "width": width, "height": height}

@register.inclusion_tag("knowledgemap_embed.html")
def knowledgemap_embed(exercises, map_coords):
    return {"exercises": exercises, "map_coords": map_coords}

@register.inclusion_tag("related_videos.html")
def related_videos(exercise_videos):
    return {"exercise_videos": exercise_videos}

@register.inclusion_tag("exercise_message.html")
def exercise_message(coaches, endangered, reviewing, proficient, struggling):
    return {
            "coaches": coaches,
            "endangered": endangered,
            "reviewing": reviewing,
            "proficient": proficient,
            "struggling": struggling
            }

@register.inclusion_tag("streak_bar.html")
def streak_bar(exercise):

    streak = exercise.streak
    longest_streak = 0

    if hasattr(exercise, "longest_streak"):
        longest_streak = exercise.longest_streak

    streak_max_width = 228
    streak_width = min(streak_max_width, int((streak_max_width / 10.0) * streak))
    longest_streak_width = min(streak_max_width, int((streak_max_width / 10.0) * longest_streak))
    streak_icon_width = min(streak_max_width - 2, max(43, streak_width)) # 43 is width of streak icon

    return {
            "streak": streak,
            "longest_streak": longest_streak,
            "streak_width": streak_width, 
            "longest_streak_width": longest_streak_width, 
            "streak_max_width": streak_max_width,
            "streak_icon_width": streak_icon_width
            }

register.tag(highlight)

webapp.template.register_template_library('discussion.templatetags')

