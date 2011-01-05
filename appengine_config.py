# Uncomment this function to enable AppStats performance recording:
# http://code.google.com/appengine/docs/python/tools/appstats.html
#
# Do not leave uncommented unless actively profiling, because AppStats logging
# incurs a slight performance penalty.
#def webapp_add_wsgi_middleware(app):
#    from google.appengine.ext.appstats import recording
#    app = recording.appstats_wsgi_middleware(app)
#    return app

