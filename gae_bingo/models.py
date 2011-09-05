import logging

from google.appengine.ext import db
from google.appengine.api import memcache

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

    @staticmethod
    def key_for_experiment_name_and_number(experiment_name, number):
        return "_gae_alternative:%s:%s" % (experiment_name, number)

    def increment_participants(self):
        # Use a memcache.incr-backed counter to keep track of increments in a scalable fashion.
        # It's possible that the cached _GAE_Bingo_Alternative entities will fall a bit behind
        # due to concurrency issues, but the memcache.incr'd version should stay up-to-date and
        # be persisted.
        self.participants = long(memcache.incr("%s:participants" % self.key_for_experiment_name_and_number(self.experiment_name, self.number), initial_value=0))

    def increment_conversions(self):
        # Use a memcache.incr-backed counter to keep track of increments in a scalable fashion.
        # It's possible that the cached _GAE_Bingo_Alternative entities will fall a bit behind
        # due to concurrency issues, but the memcache.incr'd version should stay up-to-date and
        # be persisted.
        self.conversions = long(memcache.incr("%s:conversions" % self.key_for_experiment_name_and_number(self.experiment_name, self.number), initial_value=0))

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
                    )
                )
        i += 1

    return experiment, alternatives
