import logging

from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import memcache
from google.appengine.datastore import entity_pb
from google.appengine.ext.webapp import RequestHandler

from .models import _GAE_Bingo_Experiment, _GAE_Bingo_Alternative, _GAE_Bingo_Identity, persist_gae_bingo_identity
from identity import identity

# REQUEST_CACHE is cleared before and after every requests by gae_bingo.middleware.
# NOTE: this will need a bit of a touchup once Python 2.7 is released for GAE and concurrent requests are enabled.
REQUEST_CACHE = {}

def flush_request_cache():
    global REQUEST_CACHE
    REQUEST_CACHE = {}

class BingoCache(object):

    MEMCACHE_KEY = "_gae_bingo_cache"

    @staticmethod
    def get():
        if not REQUEST_CACHE.get(BingoCache.MEMCACHE_KEY):
            REQUEST_CACHE[BingoCache.MEMCACHE_KEY] = memcache.get(BingoCache.MEMCACHE_KEY) or BingoCache.load_from_datastore()
        return REQUEST_CACHE[BingoCache.MEMCACHE_KEY]

    def __init__(self):
        self.dirty = False

        self.experiments = {} # Protobuf version of experiments for extremely fast (de)serialization
        self.experiment_models = {} # Deserialized experiment models

        self.alternatives = {} # Protobuf version of alternatives for extremely fast (de)serialization
        self.alternative_models = {} # Deserialized alternative models

        self.experiment_names_by_conversion_name = {} # Mapping of conversion names to experiment names

    def store_if_dirty(self):

        # Only write to memcache if a change has been made
        if not self.dirty:
            return

        # Wipe out deserialized models before serialization for speed
        self.experiment_models = {}
        self.alternative_models = {}

        # No longer dirty
        self.dirty = False

        memcache.set(BingoCache.MEMCACHE_KEY, self)

    def persist_to_datastore(self):

        # Persist current state of experiment and alternative models to datastore.
        # Their sums might be slightly out-of-date during any given persist, but not by much.
        for experiment_name in self.experiments:
            experiment_model = self.get_experiment(experiment_name)
            if experiment_model:
                experiment_model.put()

        for experiment_name in self.alternatives:
            alternative_models = self.get_alternatives(experiment_name)
            for alternative_model in alternative_models:
                # When persisting to datastore, we want to store the most recent value we've got
                alternative_model.load_latest_counts()
                alternative_model.put()

    @staticmethod
    def load_from_datastore():

        # This shouldn't happen often (should only happen when memcache has been completely evicted),
        # but we still want to be as fast as possible.

        bingo_cache = BingoCache()

        experiment_dict = {}
        alternatives_dict = {}

        # TODO: parallelize these datastore calls
        experiments = _GAE_Bingo_Experiment.all().filter("live =", True)
        for experiment in experiments:
            experiment_dict[experiment.name] = experiment

        alternatives = _GAE_Bingo_Alternative.all().filter("live =", True)
        for alternative in alternatives:
            if alternative.experiment_name not in alternatives_dict:
                alternatives_dict[alternative.experiment_name] = []
            alternatives_dict[alternative.experiment_name].append(alternative)

        for experiment_name in experiment_dict:
            bingo_cache.add_experiment(experiment_dict.get(experiment_name), alternatives_dict.get(experiment_name))

        # Immediately store in memcache as soon as possible after loading from datastore to minimize # of datastore loads
        bingo_cache.store_if_dirty()

        return bingo_cache

    def add_experiment(self, experiment, alternatives):

        if not experiment or not alternatives:
            raise Exception("Cannot add empty experiment or empty alternatives to BingoCache")

        self.experiment_models[experiment.name] = experiment
        self.experiments[experiment.name] = db.model_to_protobuf(experiment).Encode()

        if not experiment.conversion_name in self.experiment_names_by_conversion_name:
            self.experiment_names_by_conversion_name[experiment.conversion_name] = []
        self.experiment_names_by_conversion_name[experiment.conversion_name].append(experiment.name)

        for alternative in alternatives:
            self.update_alternative(alternative)

        self.dirty = True

    def update_alternative(self, alternative):
        if not alternative.experiment_name in self.alternative_models:
            self.alternative_models[alternative.experiment_name] = {}

        if not alternative.experiment_name in self.alternatives:
            self.alternatives[alternative.experiment_name] = {}

        self.alternative_models[alternative.experiment_name][alternative.number] = alternative
        self.alternatives[alternative.experiment_name][alternative.number] = db.model_to_protobuf(alternative).Encode()

        self.dirty = True

    def experiment_and_alternatives(self, test_name):
        return self.get_experiment(test_name), self.get_alternatives(test_name)

    def get_experiment(self, test_name):
        if test_name not in self.experiment_models:
            if test_name in self.experiments:
                self.experiment_models[test_name] = db.model_from_protobuf(entity_pb.EntityProto(self.experiments[test_name]))

        return self.experiment_models.get(test_name)

    def get_alternatives(self, test_name):
        if test_name not in self.alternative_models:
            if test_name in self.alternatives:
                self.alternative_models[test_name] = []
                for alternative_number in self.alternatives[test_name]:
                    self.alternative_models[test_name].append(db.model_from_protobuf(entity_pb.EntityProto(self.alternatives[test_name][alternative_number])))

        return self.alternative_models.get(test_name) or []

    def get_experiment_names_by_conversion_name(self, conversion_name):
        return self.experiment_names_by_conversion_name.get(conversion_name) or []

class BingoIdentityCache(object):

    MEMCACHE_KEY = "_gae_bingo_identity_cache:%s"

    @staticmethod
    def key_for_identity(identity):
        return BingoIdentityCache.MEMCACHE_KEY % identity

    @staticmethod
    def get_for_identity(identity):
        # TODO: collapse both memcached and datastore requests into a single bulk get
        key = BingoIdentityCache.key_for_identity(identity)
        if not REQUEST_CACHE.get(key):
            REQUEST_CACHE[key] = memcache.get(key) or BingoIdentityCache.load_from_datastore()
        return REQUEST_CACHE[key]

    def store_for_identity_if_dirty(self, identity):
        if not self.dirty:
            return

        # No longer dirty
        self.dirty = False

        # TODO: maybe collapse both memcached sets into a single bulk set
        memcache.set(BingoIdentityCache.key_for_identity(identity), self)

        # Always fire off a task queue to persist bingo identity cache
        # since there's no cron job persisting these objects like BingoCache.
        self.persist_to_datastore(identity)

    def persist_to_datastore(self, identity):
        # TODO: add specific queue here
        deferred.defer(persist_gae_bingo_identity, self, identity)

    @staticmethod
    def load_from_datastore():
        return _GAE_Bingo_Identity.load(identity()) or BingoIdentityCache()

    def __init__(self):
        self.dirty = False

        self.participating_tests = [] # List of test names currently participating in
        self.converted_tests = {} # Dict of test names:number of times user has successfully converted

    def participate_in(self, test_name):
        self.participating_tests.append(test_name)
        self.dirty = True

    def convert_in(self, test_name):
        # TODO: multiple participation handling
        self.converted_tests[test_name] = 1
        self.dirty = True

def bingo_and_identity_cache():
    return BingoCache.get(), BingoIdentityCache.get_for_identity(identity())

def store_if_dirty():
    # Only load from request cache here -- if it hasn't been loaded from memcache previously, it's not dirty.
    bingo_cache = REQUEST_CACHE.get(BingoCache.MEMCACHE_KEY)
    bingo_identity_cache = REQUEST_CACHE.get(BingoIdentityCache.key_for_identity(identity()))

    if bingo_cache:
        bingo_cache.store_if_dirty()

    if bingo_identity_cache:
        bingo_identity_cache.store_for_identity_if_dirty(identity())

class PersistToDatastore(RequestHandler):
    def get(self):
        BingoCache.get().persist_to_datastore()
