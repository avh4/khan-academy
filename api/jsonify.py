# Based on http://appengine-cookbook.appspot.com/recipe/extended-jsonify-function-for-dbmodel,
# with modifications for flask.
import logging

from flask import request
import simplejson
from google.appengine.ext import db
from datetime import datetime

def dumps(obj):
    if isinstance(obj, str):
        return str(obj)
    elif obj == None:
        return None
    elif isinstance(obj, list):
        items = [];
        for item in obj:
            items.append(dumps(item))
        return items
    elif isinstance(obj, datetime):
        return obj.ctime()
    properties = dict();
    if isinstance(obj, db.Model):
        properties['kind'] = obj.kind()
        properties['key']  = str(obj.key())
    for property in dir(obj):
        if is_visible_property(property):
            try:
                value = obj.__getattribute__(property)
                valueClass = str(value.__class__)
                if is_visible_class_name(valueClass):
                    value = dumps(value)
                    if value != None:
                        properties[property] = value
                    else:
                        properties[property] = ""

            except: continue
    if len(properties) == 0:
        return str(obj)
    else:
        return properties

def is_visible_property(property):
    return property[0] != '_' and not property.startswith("INDEX_")

def is_visible_class_name(class_name):
    return not(
                ('function' in class_name) or 
                ('built' in class_name) or 
                ('method' in class_name) or
                ('db.Query' in class_name)
            )

class JSONModelEncoder(simplejson.JSONEncoder):
    def default(self, o):
        """jsonify default encoder"""
        return dumps(o)

def jsonify(data, **kwargs):
    """jsonify data in a standard (human friendly) way. If a db.Model
    entity is passed in it will be encoded as a dict.
    """
    return simplejson.dumps(data, skipkeys=True, sort_keys=True, 
            ensure_ascii=False, indent=None if request.is_xhr else 4, 
            cls=JSONModelEncoder)

