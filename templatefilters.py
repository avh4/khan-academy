# import the webapp module
from google.appengine.ext import webapp
from django import template

# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()

def smart_truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return content[:length].rsplit(' ', 1)[0]+suffix

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

webapp.template.register_template_library('discussion.templatefilters')