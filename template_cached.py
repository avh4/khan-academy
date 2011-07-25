from django import template
from inspect import getargspec
from django.utils.functional import curry
from google.appengine.ext import webapp

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
                        t = webapp.template.load(file_name)
                        self.nodelist = t.nodelist
                    return self.nodelist.render(context_class(dict))

            compile_func = curry(template.generic_tag_compiler, params, defaults, getattr(func, "_decorated_function", func).__name__, InclusionNode)
            compile_func.__doc__ = func.__doc__
            self.tag(getattr(func, "_decorated_function", func).__name__, compile_func)
            return func
        return dec
