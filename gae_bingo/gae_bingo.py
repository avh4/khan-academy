import hashlib
import time

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.datastore import entity_pb

from cache import BingoCache, bingo_and_identity_cache
from .models import create_experiment_and_alternatives

def ab_test(test_name, unparsed_alternatives, conversion):

    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()

    # TODO: short-circuit goes here

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
                experiment, alternatives = new_experiment_and_alternatives(test_name, unparsed_alternatives, conversion)
                bingo_cache.add_experiment(experiment, alternatives)

        finally:
            if got_lock:
                # Release the lock
                memcache.delete(lock_key)

    experiment, alternatives = bingo_cache.experiment_and_alternatives(test_name)

    if not experiment or not alternatives:
        raise Exception("Could not find experiment or alternatives with test_name %s" % test_name)

    alternative = find_alternative_for_user(test_name, alternatives)

    # TODO: multiple participation handling goes here
    if test_name not in bingo_identity_cache.participating_tests:
        bingo_identity_cache.participating_tests.append(test_name)

        # TODO: handle counter sharding or something of the sort
        alternative.participants += 1
        bingo_cache.update_alternative(alternative)

    return alternative.content

def bingo(param):

    if type(param) == list:

        # Bingo for all conversions in list
        for test_name in param:
            bingo(test_name)
        return

    elif type(param) == str:

        # Bingo for all experiments associated with this conversion
        for experiment_name in BingoCache.get().get_experiment_names_by_conversion_name(param):
            score_conversion(experiment_name)

def score_conversion(test_name):

    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()

    # TODO: assume participation logic goes here
    if test_name not in bingo_identity_cache.participating_tests:
        return

    # TODO: multiple participation handling goes here
    if test_name in bingo_identity_cache.converted_tests:
        return

    # TODO: is_human handling goes here

    alternative = find_alternative_for_user(test_name, bingo_cache.get_alternatives(test_name))

    # TODO: sharded counter handling
    alternative.conversions += 1
    bingo_cache.update_alternative(alternative)

    # TODO: multiple participation handling
    bingo_identity_cache.converted_tests[test_name] = 1

def find_alternative_for_user(test_name, alternatives):
    return alternatives[modulo_choice(test_name, len(alternatives))]

def module_choice(test_name, alternatives_count):

    # TODO: use real identity here
    identity = 5
    sig = hashlib.md5(test_name + str(identity)).hexdigest()
    sig_num = int(sig, base=16)
    return sig_num % alternatives_count
