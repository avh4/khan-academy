import copy
import inspect
import logging
import os

from google.appengine.ext.webapp import template
from django.template.loader_tags import BlockNode

from app import App
import layer_cache
import monkey_patches
import pickle_context

def two_pass_handler(key_fxn=lambda handler: handler.request.path):

    def decorator(target):
        # Monkey patch up django template
        monkey_patches.patch()

        def wrapper(handler, first_pass_override=False):
            cached_template = TwoPassTemplate.render_first_pass(handler, target, key_fxn)

            if cached_template:
                if first_pass_override or handler.request_bool("first_pass", default=False):
                    handler.response.out.write(cached_template.source)
                else:
                    handler.response.out.write(cached_template.render_second_pass(handler))

        return wrapper
    return decorator

def second_pass_context(last=False):
    def decorator(target):
        target.second_pass_context = True
        target.second_pass_last = last
        return target
    return decorator

class TwoPassTemplate():

    def __init__(self, name, source, template_values):
        self.name = name
        self.source = source
        self.template_values = template_values

    @staticmethod
    def get_second_pass_context_fxns(handler):
        fxns = []
        for member in inspect.getmembers(handler):
            fxn = member[1]
            if fxn and hasattr(fxn, "second_pass_context"):
                fxns.append(fxn)
        return sorted(fxns, key=lambda f: f.second_pass_last)

    def render_second_pass(self, handler):
        compiled_template = template.Template(self.source)

        for fxn in TwoPassTemplate.get_second_pass_context_fxns(handler):
            self.template_values = fxn(self.template_values)

        self.replace_blocks_during_second_pass(compiled_template)

        # Need the following settings swap to correctly render a template in App Engine land.
        # See http://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/ext/webapp/template.py
        abspath = os.path.abspath(os.path.join(__file__, ".."))
        directory, file_name = os.path.split(abspath)
        new_settings = {
            'TEMPLATE_DIRS': (directory,),
            'TEMPLATE_DEBUG': False,
            'DEBUG': False,
        }
        old_settings = template._swap_settings(new_settings)
        try:
            result = compiled_template.render(template.Context(self.template_values))
        finally:
            template._swap_settings(old_settings)

        return result

    def replace_blocks_during_second_pass(self, compiled_template):
        block_nodes_compiled = compiled_template.nodelist.get_nodes_by_type(BlockNode)
        if block_nodes_compiled:
            path = os.path.join(os.path.dirname(__file__), "..", self.name)
            original_template = template.load(path)
            block_nodes_original = original_template.nodelist.get_nodes_by_type(BlockNode)

            for block_node_compiled in block_nodes_compiled:
                block_node_match = None
                for block_node_original in block_nodes_original:
                    if block_node_original.name == block_node_compiled.name:
                        block_node_match = block_node_original
                        break
                if block_node_match:
                    block_node_compiled.nodelist = block_node_match.nodelist

    @staticmethod
    def first_pass_key(key_fxn, handler, target):
        if App.is_dev_server:
            return "two_pass[%s][%s][%s]" % (target.__name__, key_fxn(handler), App.last_modified_date())
        else:
            return "two_pass[%s][%s]" % (target.__name__, key_fxn(handler))

    @staticmethod
    @layer_cache.cache_with_key_fxn(
            lambda handler, target, key_fxn: TwoPassTemplate.first_pass_key(key_fxn, handler, target),
            layer=layer_cache.Layers.Memcache)
    def render_first_pass(handler, target, key_fxn):
        pair = target(handler)
        if not pair:
            return None

        template_name, template_values = pair

        path = os.path.join(os.path.dirname(__file__), "..", template_name)

        try:
            monkey_patches.enable_first_pass(True)
            first_pass_source = template.render(path, template_values)
        finally:
            monkey_patches.enable_first_pass(False)

        template_values_pickled = pickle_context.PickleContextDict()
        template_values_pickled.add_pickled(template_values)

        return TwoPassTemplate(template_name, first_pass_source, template_values_pickled)
