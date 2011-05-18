import simplejson

from functools import wraps
from flask import request

def jsonp(func):
    @wraps(func)
    def jsonp_enabled(*args, **kwargs):
        obj = func(*args, **kwargs)
        json = obj if type(obj) == str else simplejson.dumps(obj, ensure_ascii=False, indent=4)

        callback = request.values.get("callback")
        if callback:
            return "%s(%s)" % (callback, json)
        else:
            return json
    return jsonp_enabled
