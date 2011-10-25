import logging
from pickle import dumps, loads
from functools import wraps
import zlib

def pickle(func):
    @wraps(func)
    def pickled(*args, **kwargs):
        return dumps(func(*args, **kwargs))
    return pickled

def unpickle(func):
    @wraps(func)
    def unpickled(*args, **kwargs):
        return loads(func(*args, **kwargs))
    return unpickled

def compress(func):
    @wraps(func)
    def compressed(*args, **kwargs):
        return zlib.compress(func(*args, **kwargs))
    return compressed

def decompress(func):
    @wraps(func)
    def decompressed(*args, **kwargs):
        return zlib.decompress(func(*args, **kwargs))
    return decompressed

