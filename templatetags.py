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

@register.inclusion_tag("flv_player_embed.html")
def flv_player_embed(video_path, width=800, height=480, exercise_video=None):
    if exercise_video:
        video_path = video_path + exercise_video.video_folder + "/" + exercise_video.readable_id + ".flv"
    return {"video_path": video_path, "width": width, "height": height}

register.tag(highlight)

webapp.template.register_template_library('discussion.templatetags')

