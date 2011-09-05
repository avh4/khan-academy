import logging

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.datastore import entity_pb

# Use same trick we use in last_action_cache --> all experiments and alternatives are stored in a single memcache key/value for all users, but only deserialize when necessary
# TODO: once every 5 minutes, persist both of these to datastore...and add ability to load from datastore

class BingoCache(object):

    MEMCACHE_KEY = "_gae_bingo_cache"

    @staticmethod
    def get():
        # TODO: implement request caching for this
        return memcache.get(BingoCache.MEMCACHE_KEY) or BingoCache()

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

    def __init__(self):
        self.dirty = False

        self.experiments = {} # Protobuf version of experiments for extremely fast (de)serialization
        self.experiment_models = {} # Deserialized experiment models

        self.alternatives = {} # Protobuf version of alternatives for extremely fast (de)serialization
        self.alternative_models = {} # Deserialized alternative models

        self.experiment_names_by_conversion_name = {} # Mapping of conversion names to experiment names

    def add_experiment(self, experiment, alternatives):
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
                for serialized_alternative in self.alternatives[test_name]:
                    self.alternative_models[test_name].append(db.model_from_protobuf(entity_pb.EntityProto(serialized_alternative)))

        return self.alternative_models.get(test_name) or []

    def get_experiment_names_by_conversion_name(conversion_name):
        return self.experiment_names_by_conversion_name.get(conversion_name) or []

class BingoIdentityCache(object):

    MEMCACHE_KEY = "_gae_identity_cache:%s"

    @staticmethod
    def key_for_identity(identity):
        return BingoIdentityCache.MEMCACHE_KEY % identity

    @staticmethod
    def get_for_identity(identity):
        # TODO: implement request caching here, too, maybe collapse both memcached requests into a single bulk get
        return memcache.get(BingoIdentityCache.key_for_identity(identity)) or BingoIdentityCache()

    def store_for_identity_if_dirty(self, identity):
        if not self.dirty:
            return

        # No longer dirty
        self.dirty = False

        # TODO: maybe collapse both memcached sets into a single bulk set
        memcache.set(BingoIdentityCache.key_for_identity(identity), self)

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
    # TODO: make 5 use real identity logic here
    return BingoCache.get(), BingoIdentityCache.get_for_identity(5)

def store_if_dirty():
    # TODO: only load here if loading from request cache, don't load from memcache
    bingo_cache, bingo_identity_cache = bingo_and_identity_cache()
    
    bingo_cache.store_if_dirty()
    bingo_identity_cache.store_if_dirty()
