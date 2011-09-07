import logging
import hashlib
import time

from google.appengine.api import memcache

from .cache import BingoCache, bingo_and_identity_cache
from .models import create_experiment_and_alternatives
from .identity import identity

def ab_test(experiment_name, alternative_params = None, conversion_name = None):

    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()

    if experiment_name not in bingo_cache.experiments:

        # Creation logic w/ high concurrency protection
        client = memcache.Client()
        lock_key = "_gae_bingo_test_creation_lock"
        got_lock = False

        try:

            # Make sure only one experiment gets created
            while not got_lock:
                locked = client.gets(lock_key)

                while locked is None:
                    # Initialize the lock if necessary
                    client.set(lock_key, False)
                    locked = client.gets(lock_key)

                if not locked:
                    # Lock looks available, try to take it with compare and set (expiration of 10 seconds)
                    got_lock = client.cas(lock_key, True, time=10)
                
                if not got_lock:
                    # If we didn't get it, wait a bit and try again
                    time.sleep(0.1)

            # We have the lock, go ahead and create the experiment if still necessary
            if experiment_name not in BingoCache.get().experiments:
                experiment, alternatives = create_experiment_and_alternatives(experiment_name, alternative_params, conversion_name)
                bingo_cache.add_experiment(experiment, alternatives)
                bingo_cache.store_if_dirty()

        finally:
            if got_lock:
                # Release the lock
                client.set(lock_key, False)

    experiment, alternatives = bingo_cache.experiment_and_alternatives(experiment_name)

    if not experiment or not alternatives:
        raise Exception("Could not find experiment or alternatives with experiment_name %s" % experiment_name)

    if not experiment.live:
        # Experiment has ended. Short-circuit and use selected winner before user has had a chance to remove relevant ab_test code.
        return experiment.short_circuit_content

    alternative = find_alternative_for_user(experiment_name, alternatives)

    # TODO: multiple participation handling goes here
    if experiment_name not in bingo_identity_cache.participating_tests:
        bingo_identity_cache.participate_in(experiment_name)

        alternative.increment_participants()
        bingo_cache.update_alternative(alternative)

    return alternative.content

def bingo(param):

    if type(param) == list:

        # Bingo for all conversions in list
        for experiment_name in param:
            bingo(experiment_name)
        return

    elif type(param) == str:

        # Bingo for all experiments associated with this conversion
        for experiment_name in BingoCache.get().get_experiment_names_by_conversion_name(param):
            score_conversion(experiment_name)

def score_conversion(experiment_name):

    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()

    # TODO: assume participation logic goes here
    if experiment_name not in bingo_identity_cache.participating_tests:
        return

    # TODO: multiple participation handling goes here
    if experiment_name in bingo_identity_cache.converted_tests:
        return

    # TODO: is_human handling goes here

    alternative = find_alternative_for_user(experiment_name, bingo_cache.get_alternatives(experiment_name))

    alternative.increment_conversions()
    bingo_cache.update_alternative(alternative)

    # TODO: multiple participation handling
    bingo_identity_cache.convert_in(experiment_name)

def find_alternative_for_user(experiment_name, alternatives):
    return alternatives[modulo_choice(experiment_name, len(alternatives))]

def modulo_choice(experiment_name, alternatives_count):
    sig = hashlib.md5(experiment_name + str(identity())).hexdigest()
    sig_num = int(sig, base=16)
    return sig_num % alternatives_count
