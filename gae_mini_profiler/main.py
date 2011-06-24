from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from gae_mini_profiler import profiler

application = webapp.WSGIApplication([("/gae_mini_profiler/request_stats", profiler.RequestStatsHandler)])

def main():
    run_wsgi_app(application)
