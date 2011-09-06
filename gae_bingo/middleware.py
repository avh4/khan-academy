from cache import flush_request_cache, store_if_dirty
from identity import identity, get_identity_cookie_value, set_identity_cookie_header, flush_identity_cache

class GAEBingoWSGIMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        flush_request_cache()
        flush_identity_cache()

        def gae_bingo_start_response(status, headers, exc_info = None):

            if identity() != get_identity_cookie_value():
                headers.append(("Set-Cookie", set_identity_cookie_header()))

            return start_response(status, headers, exc_info)

        result = self.app(environ, gae_bingo_start_response)
        for value in result:
            yield value

        store_if_dirty()
        flush_request_cache()
        flush_identity_cache()
