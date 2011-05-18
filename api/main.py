from wsgiref.handlers import CGIHandler

from app import App
from api import api_app

from api import v0
from api import v1

def main():
    if App.is_dev_server:
        # Run debugged app
        from werkzeug_debugger_appengine import get_debugged_app
        api_app.debug=True
        debugged_app = get_debugged_app(api_app)
        CGIHandler().run(debugged_app)
    else:
        # Run production app
        from google.appengine.ext.webapp.util import run_wsgi_app
        run_wsgi_app(api_app)

# Use App Engine app caching
if __name__ == "__main__":
    main()

