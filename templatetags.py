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
    remainder_indices = range(0, len(videos) % num_cols)
    link_height = font_size * 1.5 
    column_indices = [(items_in_column * multiplier) for multiplier in range(1, num_cols + 1)]
    
    for remainder_index in remainder_indices:
        column_indices[remainder_index] += 1
        for i, v in enumerate(column_indices):
            if i > remainder_index:
                column_indices[i] += 1
        
    return {
               "videos": videos,
               "items_in_column": items_in_column,
               "column_width": column_width,
               "column_width_plus_gutter": column_width + gutter,
               "font_size": font_size,
               "link_height": link_height,
               "column_indices": column_indices,
               "list_height": column_indices[0] * link_height,
          }

register.tag(highlight)

webapp.template.register_template_library('discussion.templatetags')

