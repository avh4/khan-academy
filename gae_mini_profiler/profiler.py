import logging
import simplejson
import StringIO
import sys
from types import GeneratorType
import zlib

from google.appengine.api import users
from google.appengine.ext.webapp import template, RequestHandler
from google.appengine.api import memcache

# request_id is a per-request identifier accessed by a couple other pieces of gae_mini_profiler
request_id = None

class RequestStatsHandler(RequestHandler):

    def get(self):
        request_stats = RequestStats.get(self.request.get("request_id"))
        if request_stats:
            self.response.out.write(request_stats.request_id)
            self.response.out.write("<hr><hr><hr><hr><hr><hr>")
            self.response.out.write("<hr><hr><hr><hr><hr><hr>")
            self.response.out.write(request_stats.profiler_results)
            self.response.out.write("<hr><hr><hr><hr><hr><hr>")
            self.response.out.write("<hr><hr><hr><hr><hr><hr>")
            self.response.out.write(request_stats.appstats_results)
        else:
            self.response.out.write("NOPE")

class RequestStats(object):

    def __init__(self, request_id, middleware):
        self.request_id = request_id

        # Store compressed results so we stay under the memcache 1MB limit
        self.compressed_profiler_results = RequestStats.compress(RequestStats.calc_profiler_results(middleware))
        self.compressed_appstats_results = RequestStats.compress(RequestStats.calc_appstats_results(middleware))

    @property
    def profiler_results(self):
        return RequestStats.decompress(self.compressed_profiler_results)

    @property
    def appstats_results(self):
        return RequestStats.decompress(self.compressed_appstats_results)

    def store(self):
        result = memcache.set(RequestStats.memcache_key(self.request_id), self)

    @staticmethod
    def get(request_id):
        if request_id:
            return memcache.get(RequestStats.memcache_key(request_id))
        return None

    @staticmethod
    def memcache_key(request_id):
        if not request_id:
            return None
        return "__gae_mini_profiler_request_%s" % request_id

    @staticmethod
    def compress(v):
        return zlib.compress(v.encode('utf-8'))

    @staticmethod
    def decompress(v):
        return zlib.decompress(v).decode('utf-8')

    @staticmethod
    def calc_profiler_results(middleware):
        import pstats

        stats = pstats.Stats(middleware.prof)
        stats.sort_stats("cumulative")

        dict_list = []
        width, list_func_names = stats.get_print_list([80])
        for func_name in list_func_names:
            primitive_call_count, total_call_count, total_time, cumulative_time, callers = stats.stats[func_name]

            dict_list.append({
                "primitive call count": primitive_call_count, 
                "total call count": total_call_count, 
                "total time": total_time, 
                "per call": (total_time / total_call_count) if total_call_count else "",
                "cumulative time": cumulative_time, 
                "per call cumulative": (cumulative_time / primitive_call_count) if primitive_call_count else "",
                "func_desc": pstats.func_std_string(func_name),
                "callers": str(callers),
            })

        return simplejson.dumps(dict_list)
        
    @staticmethod
    def calc_appstats_results(middleware):
        if middleware.recorder:
            return simplejson.dumps(middleware.recorder.json())

        return ""

class ProfilerMiddleware(object):

    def __init__(self, app):
        template.register_template_library('gae_mini_profiler.templatetags')
        self.app = app
        self.app_clean = app
        self.prof = None
        self.recorder = None

    def should_profile(self):
        user = users.get_current_user()
        return user and user.email() == "test@example.com"

    def __call__(self, environ, start_response):

        global request_id
        request_id = None

        # Start w/ a non-profiled app at the beginning of each request
        self.app = self.app_clean
        self.prof = None
        self.recorder = None

        if self.should_profile():

            # Set a random ID for this request so we can look up stats later
            import base64
            import os
            request_id = base64.b64encode(os.urandom(30))

            # Configure AppStats output
            from google.appengine.ext.appstats import recording
            recording.config.MAX_REPR = 150

            # Turn on AppStats monitoring for this request
            old_app = self.app
            def wrapped_appstats_app(environ, start_response):
                # Use this wrapper to grab the app stats recorder for RequestStats.save()
                self.recorder = recording.recorder
                return old_app(environ, start_response)
            self.app = recording.appstats_wsgi_middleware(wrapped_appstats_app)

            # Turn on cProfile profiling for this request
            import cProfile
            self.prof = cProfile.Profile()

            # Get profiled wsgi result
            result = self.prof.runcall(lambda *args, **kwargs: self.app(environ, start_response), None, None)

            self.recorder = recording.recorder

            # If we're dealing w/ a generator, profile all of the .next calls as well
            if type(result) == GeneratorType:

                while True:
                    try:
                        yield self.prof.runcall(result.next)
                    except StopIteration:
                        break

            else:
                for value in result:
                    yield value

            # Store stats for later access
            RequestStats(request_id, self).store()

            # Just in case we're using up memory in the recorder and profiler
            self.recorder = None
            self.prof = None
            request_id = None

        else:
            result = self.app(environ, start_response)
            for value in result:
                yield value
