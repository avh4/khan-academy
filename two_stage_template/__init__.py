import logging

from google.appengine.ext.webapp import template

import layer_cache
import request_handler
import monkey_patches

def two_stage_render():
    def decorator(target):

        monkey_patches.patch()

        def wrapper(handler, *args, **kwargs):
            cached_template = FirstStageTemplates.get(handler, target, *args, **kwargs)
            handler.response.out.write(cached_template.render({}))

        return wrapper
    return decorator

class FirstStageTemplates():

    @staticmethod
    def get(handler, target, *args, **kwargs):
        template_source = FirstStageTemplates.get_source(handler, target, *args, **kwargs)
        compiled_template = template.Template(template_source)
        return compiled_template

    @staticmethod
    @layer_cache.cache_with_key_fxn(
            lambda handler, *args, **kwargs: "first_stage_template[%s]" % handler.request.path, 
            layer=layer_cache.Layers.Memcache
            )
    def get_source(handler, target, *args, **kwargs):

        template_name, template_values = target(handler, *args, **kwargs)

        # Remove callable keys for first stage render
        for key in template_values.keys():
            if callable(template_values[key]):
                del template_values[key]

        return handler.render_template_to_string(template_name, template_values)

class TwoStageTest(request_handler.RequestHandler):

    @two_stage_render()
    def get(self):
        template_values = {
            "sheep": (lambda: 1),
            "monkey": "ooh ooh aah aah",
        }

        return ("two_stage_template/two_stage_test.html", template_values)

