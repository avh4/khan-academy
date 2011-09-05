from cache import flush_request_cache, store_if_dirty

class GAEBingoWSGIMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        flush_request_cache()

        result = self.app(environ, start_response)
        for value in result:
            yield value

        store_if_dirty()
        flush_request_cache()
