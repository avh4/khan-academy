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

register.tag(highlight)

