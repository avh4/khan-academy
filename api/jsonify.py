# Based on http://appengine-cookbook.appspot.com/recipe/extended-jsonify-function-for-dbmodel,
# with modifications for flask and performance.
import logging

from flask import request
import simplejson
from google.appengine.ext import db
from datetime import datetime

SIMPLE_TYPES = (int, long, float, bool, basestring)
def dumps(obj):
    if isinstance(obj, SIMPLE_TYPES):
        return obj
    elif obj == None:
        return None
    elif isinstance(obj, list):
        items = [];
        for item in obj:
            items.append(dumps(item))
        return items
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    elif isinstance(obj, dict):
        properties = {}
        for key in obj:
            logging.info("dumping key %s" % key)
            properties[key] = dumps(obj[key])
        return properties

    properties = dict();
    if isinstance(obj, db.Model):
        properties['kind'] = obj.kind()

    serialize_blacklist = []
    if hasattr(obj, "_serialize_blacklist"):
        serialize_blacklist = obj._serialize_blacklist

    serialize_list = dir(obj)
    if hasattr(obj, "_serialize_whitelist"):
        serialize_list = obj._serialize_whitelist

    for property in serialize_list:
        if is_visible_property(property, serialize_blacklist):
            try:
                value = obj.__getattribute__(property)
                valueClass = str(value.__class__)
                if is_visible_class_name(valueClass):
                    value = dumps(value)
                    logging.info("dumping prop %s" % property)
                    properties[property] = value
            except:
                continue

    if len(properties) == 0:
        return str(obj)
    else:
        return properties

def is_visible_property(property, serialize_blacklist):
    return property[0] != '_' and not property.startswith("INDEX_") and not property in serialize_blacklist

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
            ensure_ascii=False, indent=4, 
            cls=JSONModelEncoder)

