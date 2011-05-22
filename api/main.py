from wsgiref.handlers import CGIHandler

from app import App
from api import api_app
from api import auth

from api import v0
from api import v1

def real_main():
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

def profile_main():
    # This is the main function for profiling
    # We've renamed our original main() above to real_main()
    import cProfile, pstats
    prof = cProfile.Profile()
    prof = prof.runctx("real_main()", globals(), locals())
    print "<pre>"
    stats = pstats.Stats(prof)
    stats.sort_stats("cumulative")  # time or cumulative
    stats.print_stats(80)  # 80 = how many to print
    # The rest is optional.
    # stats.print_callees()
    stats.print_callers()
    print "</pre>"
    
main = real_main
# Uncomment the following line to enable profiling 
# main = profile_main

# Use App Engine app caching
if __name__ == "__main__":
    main()

