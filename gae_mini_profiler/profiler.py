import datetime
import logging
import pickle
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

        self.response.headers["Content-Type"] = "application/json"

        request_stats = RequestStats.get(self.request.get("request_id"))

        dict_request_stats = {}
        for property in RequestStats.serialized_properties:
            dict_request_stats[property] = request_stats.__getattribute__(property)

        self.response.out.write(simplejson.dumps(dict_request_stats))

class RequestStats(object):

    serialized_properties = ["request_id", "path", "query_string", "s_dt", "profiler_results", "appstats_results"]

    def __init__(self, request_id, environ, middleware):
        self.request_id = request_id
        self.path = environ.get("PATH_INFO")
        self.query_string = environ.get("QUERY_STRING")
        self.s_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.profiler_results = RequestStats.calc_profiler_results(middleware)
        self.appstats_results = RequestStats.calc_appstats_results(middleware)

    def store(self):
        # Store compressed results so we stay under the memcache 1MB limit
        pickled = pickle.dumps(self)
        compressed_pickled = zlib.compress(pickled)

        return memcache.set(RequestStats.memcache_key(self.request_id), compressed_pickled)

    @staticmethod
    def get(request_id):
        if request_id:
            compressed_pickled = memcache.get(RequestStats.memcache_key(request_id))

            if compressed_pickled:
                pickled = zlib.decompress(compressed_pickled)
                return pickle.loads(pickled)

        return None

    @staticmethod
    def memcache_key(request_id):
        if not request_id:
            return None
        return "__gae_mini_profiler_request_%s" % request_id

    @staticmethod
    def calc_profiler_results(middleware):
        import pstats

        stats = pstats.Stats(middleware.prof)
        stats.sort_stats("cumulative")

        results = {
            "total_calls": stats.total_calls,
            "total_ms": stats.total_tt,
            "calls": []
        }

        width, list_func_names = stats.get_print_list([80])
        for func_name in list_func_names:
            primitive_call_count, total_call_count, total_time, cumulative_time, callers = stats.stats[func_name]

            results["calls"].append({
                "primitive call count": primitive_call_count, 
                "total call count": total_call_count, 
                "total time": total_time, 
                "per call": (total_time / total_call_count) if total_call_count else "",
                "cumulative time": cumulative_time, 
                "per call cumulative": (cumulative_time / primitive_call_count) if primitive_call_count else "",
                "func_desc": pstats.func_std_string(func_name),
                "callers": str(callers),
            })

        return results
        
    @staticmethod
    def calc_appstats_results(middleware):
        if middleware.recorder:
            return {"json": middleware.recorder.json()}

        return None

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
            RequestStats(request_id, environ, self).store()

            # Just in case we're using up memory in the recorder and profiler
            self.recorder = None
            self.prof = None
            request_id = None

        else:
            result = self.app(environ, start_response)
            for value in result:
                yield value
