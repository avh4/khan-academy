import time

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.datastore import entity_pb

from gae_bingo.cache import BingoCache, bingo_and_identity_cache
from gae_bingo.models import Experiment

def ab_test(test_name, alternatives, conversion):

    # TODO: short-circuit goes here

    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()

    if test_name not in bingo_cache.experiments:

        # Creation logic w/ high concurrency protection
        client = memcache.Client()
        lock_key = "_gae_bingo_test_creation_lock"
        got_lock = False

        try:

            # Make sure only one experiment gets created
            while not got_lock:
                if not client.gets(lock_key):
                    # If lock is empty, try to get it with compare and set (expiration of 10 seconds)
                    got_lock = client.cas(lock_key, True, time=10)
                
                if not got_lock:
                    # If we didn't get it or it wasn't empty, wait a bit and try again
                    time.sleep(0.1)

            # We have the lock, go ahead and create the experiment if still necessary
            if test_name not in BingoCache.get().experiments:
                experiment = Experiment(test_name, alternatives, conversion)
                bingo_cache.add_experiment(experiment, alternatives)

        finally:
            if got_lock:
                # Release the lock
                memcache.delete(lock_key)

    alternative = find_alternative_for_user(test_name, alternatives)

    # TODO: multiple participation handling here
    if test_name not in bingo_identity_cache.participating_tests:
        bingo_identity_cache.participating_tests.append(test_name)

        # TODO: handle counter sharding or something of the sort
        alternative.participants += 1
        bingo_cache.update_alternative(alternative)

    return alternative.content

def find_alternative_for_user(test_name, alternatives):
    pass
