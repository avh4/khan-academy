import copy
import logging
import os

from google.appengine.ext.webapp import template

from app import App
import layer_cache
import request_handler
import monkey_patches

def two_pass_handler():
    def decorator(target):
        # Monkey patch up django template
        monkey_patches.patch()

        def wrapper(handler):
            cached_template = TwoPassTemplate.render_first_pass(handler, target)
            handler.response.out.write(cached_template.render_second_pass(handler))

        return wrapper
    return decorator

current_first_pass_fake_closure = None
class FirstPassFakeClosure:
    def __init__(self):
        self.dict = {}

    def __getitem__(self, name):
        return self.dict[name]

    def __setitem__(self, name, context):
        self.dict[name] = context

class TwoPassVariableContext:
    def __init__(self, target_name, args):
        self.target_name = target_name
        self.args = args

def two_pass_variable():
    def decorator(target):
        def wrapper(handler, *args, **kwargs):
            first_pass_call = kwargs.get("first_pass_call", True)

            if first_pass_call:
                variable_context = TwoPassVariableContext(target.__name__, args)
                current_first_pass_fake_closure[target.__name__] = variable_context
                return variable_context
            else:
                variable_context = kwargs.get("variable_context", TwoPassVariableContext("", []))
                def inner_wrapper(handler, *args, **kwargs):
                    return target(handler, *variable_context.args)
                return inner_wrapper

        return wrapper
    return decorator

class TwoPassTemplate():

    def __init__(self, source, first_pass_fake_closure, template_value_fxn_names, template_values):
        self.source = source
        self.first_pass_fake_closure = first_pass_fake_closure
        self.template_value_fxn_names = template_value_fxn_names
        self.template_values = template_values

    def render_second_pass(self, handler):
        compiled_template = template.Template(self.source)

        template_values = {}
        for key in self.template_values:
            template_values[key] = self.template_values[key]

        # Add second pass template values
        for key in self.template_value_fxn_names:
            fxn_name = self.template_value_fxn_names[key]
            wrapped_fxn = getattr(handler, fxn_name)
            variable_context = self.first_pass_fake_closure[fxn_name]
            template_values[key] = wrapped_fxn(first_pass_call=False, variable_context=variable_context)(handler)

        return compiled_template.render(template.Context(template_values))

    @staticmethod
#    @layer_cache.cache_with_key_fxn(
#            lambda handler, target: "two_pass_template[%s]" % handler.request.path, 
#            layer=layer_cache.Layers.Memcache
#            )
    def render_first_pass(handler, target):
        global current_first_pass_fake_closure
        current_first_pass_fake_closure = FirstPassFakeClosure()

        template_name, template_values = target(handler)

        # Remove two pass variable contexts for first pass render,
        # and keep references around for second pass
        template_value_fxn_names = {}
        for key in template_values.keys():
            val = template_values[key]
            if isinstance(val, TwoPassVariableContext):
                template_value_fxn_names[key] = val.target_name
                del template_values[key]

        monkey_patches.enable_first_pass_variable_resolution(True)

        try:
            path = os.path.join(os.path.dirname(__file__), "..", template_name)
            first_pass_source = template.render(path, template_values)
        finally:
            monkey_patches.enable_first_pass_variable_resolution(False)

        first_pass_fake_closure = copy.deepcopy(current_first_pass_fake_closure)
        current_first_pass_fake_closure = None

        return TwoPassTemplate(first_pass_source, first_pass_fake_closure, template_value_fxn_names, template_values)

class TwoPassTest(request_handler.RequestHandler):

    @two_pass_variable()
    def sheep(self, monkey):
        return monkey + self.request_int("inc", default=1)

    @two_pass_variable()
    def donkey(self, gorilla):
        return gorilla + self.request_int("inc", default=1)

    @two_pass_variable()
    def zebras(self):
        return "hrm"

    @two_pass_handler()
    def get(self):

        monkey = 5
        gorilla = 6

        template_values = {
            "sheep": self.sheep(monkey),
            "donkey": self.donkey(gorilla),
            "zebras": self.zebras(),
            "monkey": "ooh ooh aah aah",
            "monkeys": ["a", "b"],
        }

        return ("two_pass_template/two_pass_test.html", template_values)

