import os
import logging

from django import template
from inspect import getargspec
from django.utils.functional import curry
from google.appengine.ext import webapp

from app import App

def create_template_register():
  return Library()

Context = webapp.template.Context

class Library(template.Library):
    def __init__(self):
        super(Library, self).__init__()

    def inclusion_tag(self, file_name, context_class=Context, takes_context=False):
        """
        This override allows app engine to cache the file used for the template.
        App engine also makes paths easier, so this version of include_tag only works
        with a precise file_name (you can't pass in more than one value for file_name)
        """
        if hasattr(file_name, '__iter__'):
            raise Exception("This override of inclusion_tag can't be used with a sequence for file_name")
        def dec(func):
            params, xx, xxx, defaults = getargspec(func)
            if takes_context:
                if params[0] == 'context':
                    params = params[1:]
                else:
                    raise template.TemplateSyntaxError, "Any tag function decorated with takes_context=True must have a first argument of 'context'"

            class InclusionNode(template.Node):
                def __init__(self, vars_to_resolve):
                    self.vars_to_resolve = vars_to_resolve

                def render(self, context):
                    resolved_vars = [template.resolve_variable(var, context) for var in self.vars_to_resolve]
                    if takes_context:
                        args = [context] + resolved_vars
                    else:
                        args = resolved_vars

                    dict = func(*args)

                    if not getattr(self, 'nodelist', False):
                        t = webapp.template.load(os.path.join(App.root, file_name))
                        self.nodelist = t.nodelist
                    return self.nodelist.render(context_class(dict))

            compile_func = curry(template.generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, InclusionNode)
            compile_func.__doc__ = func.__doc__
            self.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
            return func
        return dec

# monkey patch webapp.template.load so we can log cache misses

import logging
import os
import django.template.loader

template_cache = webapp.template.template_cache
_swap_settings = webapp.template._swap_settings
_urlnode_render_replacement = webapp.template._urlnode_render_replacement
def load(path, debug=False):
  """Loads the Django template from the given path.

  It is better to use this function than to construct a Template using the
  class below because Django requires you to load the template with a method
  if you want imports and extends to work in the template.
  """
  abspath = os.path.abspath(path)

  if not debug:
    template = template_cache.get(abspath, None)
  else:
    template = None

  if not template:
    logging.warning("cache miss for file: %s", path)
    directory, file_name = os.path.split(abspath)
    new_settings = {
        'TEMPLATE_DIRS': (directory,),
        'TEMPLATE_DEBUG': debug,
        'DEBUG': debug,
        }
    old_settings = _swap_settings(new_settings)
    try:
      template = django.template.loader.get_template(file_name)
    finally:
      _swap_settings(old_settings)

    if not debug:
      template_cache[abspath] = template

    def wrap_render(context, orig_render=template.render):


      URLNode = django.template.defaulttags.URLNode
      save_urlnode_render = URLNode.render
      old_settings = _swap_settings(new_settings)
      try:
        URLNode.render = _urlnode_render_replacement
        return orig_render(context)
      finally:
        _swap_settings(old_settings)
        URLNode.render = save_urlnode_render

    template.render = wrap_render

  return template

webapp.template.load = load
