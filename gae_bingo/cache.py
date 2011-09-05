
# Use same trick we use in last_action_cache --> all experiments and alternatives are stored in a single memcache key/value for all users, but only deserialize when necessary
# TODO: once every 5 minutes, persist both of these to datastore...and add ability to load from datastore

class BingoCache(object):

    MEMCACHE_KEY = "_gae_bingo_cache"

    @staticmethod
    def get():
        # TODO: implement request caching for this
        return memcache.get(BingoCache.MEMCACHE_KEY) or BingoCache()

    def __init__(self):
        self.experiments = {} # Protobuf version of experiments for extremely fast (de)serialization
        self.experiment_models = {} # Deserialized experiment models

        self.alternatives = {} # Protobuf version of alternatives for extremely fast (de)serialization
        self.alternative_models = {} # Deserialized alternative models

        self.experiment_names_by_conversion_names = {} # Mapping of conversion names to experiment names

    def add_experiment(self, experiment, alternatives):
        # TODO: handle concurrency issues here during initial creation
        self.experiment_models[experiment.name] = experiment
        self.experiments[experiment.name] = db.model_to_protobuf(experiment).Encode()

        if not experiment.conversion_name in self.experiment_names_by_conversion_name:
            self.experiment_names_by_conversion_names[experiment.conversion_name] = []
        self.experiment_names_by_conversion_names[experiment.conversion_name].append(experiment.name)

        for alternative in alternatives:
            self.update_alternative(alternative)

    def update_alternative(self, alternative):
        if not alternative.experiment_name in self.alternative_models:
            self.alternative_models[experiment.name] = {}

        if not alternative.experiment_name in self.alternatives:
            self.alternatives[experiment.name] = {}

        self.alternative_models[alternative.experiment_name][alternative.number] = alternative
        self.alternatives[alternative.experiment_name][alternative.number] = db.model_to_protobuf(alternative).Encode()

    def experiment_and_alternatives(self, test_name):
        return self.get_experiment(test_name), self.get_alternatives(test_name)

    def get_experiment(test_name):
        # TODO: Handle deserialization appropriately here
        return self.experiment_models.get(test_name)

    def get_alternatives(test_name):
        # TODO: deserialization
        return self.alternative_models.get(test_name) or []

    def get_experiment_names_by_conversion_name(conversion_name):
        # TODO: Handle deserialization and lookups
        return self.experiment_names_by_conversion_names.get(conversion_name)

class BingoIdentityCache(object):

    MEMCACHE_KEY = "_gae_identity_cache:%s"

    @staticmethod
    def key_for_identity(identity):
        return BingoIdentityCache.MEMCACHE_KEY % identity

    @staticmethod
    def get_for_identity(identity):
        # TODO: implement request caching here, too, maybe collapse both memcached requests into a single bulk get
        return memcache.get(BingoIdentityCache.key_for_identity(identity)) or BingoIdentityCache()

    def __init__(self):
        self.participating_tests = [] # List of test names currently participating in
        self.converted_tests = {} # Dict of test names:number of times user has successfully converted

def bingo_and_identity_cache():
    # TODO: make 5 use real identity logic here
    return BingoCache.get(), BingoIdentityCache.get_for_identity(5)
