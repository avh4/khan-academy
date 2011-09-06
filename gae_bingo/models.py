import pickle
import logging

from google.appengine.ext import db
from google.appengine.api import memcache

# TODO: add note about deferred entrypoint and startup config here

# If you use a datastore model to uniquely identify each user,
# let it inherit from this class, like so...
#
#       class UserData(GAEBingoIdentityModel, db.Model)
#
# ...this will let gae_bingo automatically take care of persisting ab_test
# identities from unregistered users to logged in users.
class GAEBingoIdentityModel(db.Model):
    gae_bingo_identity = db.StringProperty()

class _GAE_Bingo_Experiment(db.Model):
    name = db.StringProperty()
    conversion_name = db.StringProperty()
    live = db.BooleanProperty(default = False)
    dt_started = db.DateTimeProperty() # TODO: set dt_started appropriately

    @staticmethod
    def key_for_name(name):
        return "_gae_experiment:%s" % name

    @staticmethod
    def exists(name):
        return cache.exists(Experiment.key_for_name(name))

class _GAE_Bingo_Alternative(db.Model):
    number = db.IntegerProperty()
    experiment_name = db.StringProperty()
    content = db.TextProperty()
    conversions = db.IntegerProperty(default = 0)
    participants = db.IntegerProperty(default = 0)
    live = db.BooleanProperty(default = False)

    @staticmethod
    def key_for_experiment_name_and_number(experiment_name, number):
        return "_gae_alternative:%s:%s" % (experiment_name, number)

    def key_for_self(self):
        return _GAE_Bingo_Alternative.key_for_experiment_name_and_number(self.experiment_name, self.number)

    def increment_participants(self):
        # Use a memcache.incr-backed counter to keep track of increments in a scalable fashion.
        # It's possible that the cached _GAE_Bingo_Alternative entities will fall a bit behind
        # due to concurrency issues, but the memcache.incr'd version should stay up-to-date and
        # be persisted.
        self.participants = long(memcache.incr("%s:participants" % self.key_for_self(), initial_value=0))

    def increment_conversions(self):
        # Use a memcache.incr-backed counter to keep track of increments in a scalable fashion.
        # It's possible that the cached _GAE_Bingo_Alternative entities will fall a bit behind
        # due to concurrency issues, but the memcache.incr'd version should stay up-to-date and
        # be persisted.
        self.conversions = long(memcache.incr("%s:conversions" % self.key_for_self(), initial_value=0))

    def load_latest_counts(self):
        # TODO: when memcache is cleared, this erases current max...
        # When persisting to datastore, we want to store the most recent value we've got
        self.participants = long(memcache.get("%s:participants" % self.key_for_self()) or 0)
        self.conversions = long(memcache.get("%s:conversions" % self.key_for_self()) or 0)

class _GAE_Bingo_Identity(db.Model):
    identity = db.StringProperty()
    pickled = db.BlobProperty()

    @staticmethod
    def key_for_identity(identity):
        return "_gae_bingo_identity:%s" % identity

    @staticmethod
    def load(identity):
        gae_bingo_identity = _GAE_Bingo_Identity.all().filter("identity =", identity).get()
        if gae_bingo_identity:
            return pickle.loads(gae_bingo_identity.pickled)

        return None

def persist_gae_bingo_identity(bingo_identity_cache, identity):
    bingo_identity = _GAE_Bingo_Identity(
                key_name = _GAE_Bingo_Identity.key_for_identity(identity),
                identity = identity,
                pickled = pickle.dumps(bingo_identity_cache),
            )
    bingo_identity.put()

def create_experiment_and_alternatives(test_name, alternative_params, conversion_name):

    experiment = _GAE_Bingo_Experiment(
                key_name = _GAE_Bingo_Experiment.key_for_name(test_name),
                name = test_name,
                conversion_name = conversion_name,
                live = False,
            )

    alternatives = []
    i = 0

    for content in alternative_params:
        alternatives.append(
                _GAE_Bingo_Alternative(
                        key_name = _GAE_Bingo_Alternative.key_for_experiment_name_and_number(test_name, i),
                        parent = experiment,
                        experiment_name = experiment.name,
                        number = i,
                        content = str(content),
                        live = False,
                    )
                )
        i += 1

    return experiment, alternatives
