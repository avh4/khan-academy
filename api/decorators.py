import logging
import hashlib
import zlib
from functools import wraps

from flask import request
from flask import current_app
import api.jsonify as apijsonify

def etag(func_tag_content):
    def etag_wrapper(func):
        @wraps(func)
        def etag_enabled(*args, **kwargs):
            etag_server = "\"%s\"" % hashlib.md5(func_tag_content()).hexdigest()
            etag_client = request.headers.get("If-None-Match")
            if etag_client and etag_client == etag_server:
                return current_app.response_class(status=304)
            
            result = func(*args, **kwargs)

            if isinstance(result, current_app.response_class):
                result.headers["ETag"] = etag_server
                return result
            else:
                return current_app.response_class(result, headers={"Etag": etag_server})
        return etag_enabled
    return etag_wrapper

def jsonify(func):
    @wraps(func)
    def jsonified(*args, **kwargs):
        obj = func(*args, **kwargs)
        return obj if type(obj) == str else apijsonify.jsonify(obj)
    return jsonified

def jsonp(func):
    @wraps(func)
    def jsonp_enabled(*args, **kwargs):
        val = func(*args, **kwargs)
        callback = request.values.get("callback")
        if callback:
            val = "%s(%s)" % (callback, val)
        return current_app.response_class(val, mimetype="application/json")
    return jsonp_enabled

def compress(func):
    @wraps(func)
    def compressed(*args, **kwargs):
        return zlib.compress(func(*args, **kwargs).encode('utf-8'))
    return compressed

def decompress(func):
    @wraps(func)
    def decompressed(*args, **kwargs):
        return zlib.decompress(func(*args, **kwargs)).decode('utf-8')
    return decompressed


