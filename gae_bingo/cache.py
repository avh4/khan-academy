
# Use same trick we use in last_action_cache --> all experiments and alternatives are stored in a single memcache key/value for all users, but only deserialize when necessary
# TODO: once every 5 minutes, persist this to datastore...and add ability to load from datastore

class BingoCache

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

    def add_experiment(self, experiment, alternatives):
        # TODO: handle concurrency issues here during initial creation
        self.experiment_models[experiment.name] = experiment
        self.experiments[experiment.name] = db.model_to_protobuf(experiment).Encode()

        for alternative in alternatives:
            self.update_alternative(alternative)

    def update_alternative(self, alternative):
        if not alternative.experiment_name in self.alternative_models:
            self.alternative_models[experiment.name] = {}

        if not alternative.experiment_name in self.alternatives:
            self.alternatives[experiment.name] = {}

        self.alternative_models[alternative.experiment_name][alternative.uid] = alternative
        self.alternatives[alternative.experiment_name][alternative.uid] = db.model_to_protobuf(alternative).Encode()

class BingoIdentityCache

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

def bingo_and_identity_cache():
    # TODO: make 5 use real identity logic here
    return BingoCache.get(), BingoIdentityCache.get_for_identity(5)
