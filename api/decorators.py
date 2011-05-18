import simplejson

from functools import wraps
from flask import request
from flask import current_app

def jsonp(func):
    @wraps(func)
    def jsonp_enabled(*args, **kwargs):
        obj = func(*args, **kwargs)
        json = obj if type(obj) == str else simplejson.dumps(obj, ensure_ascii=False, indent=None if request.is_xhr else 4)

        val = json
        callback = request.values.get("callback")
        if callback:
            val = "%s(%s)" % (callback, json)

        return current_app.response_class(val, mimetype="application/json")
    return jsonp_enabled
