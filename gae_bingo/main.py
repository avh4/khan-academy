from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from gae_bingo import cache

application = webapp.WSGIApplication([
    ("/gae_bingo/persist", cache.PersistToDatastore),
])

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

