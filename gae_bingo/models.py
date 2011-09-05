from google.appengine.ext import db

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
    weight = db.FloatProperty()
    conversions = db.IntegerProperty(default = 0)
    participants = db.IntegerProperty(default = 0)

    def key_for_self(self):
        return "_gae_alternative:%s:%s" % (self.parent.name, self.alternative_id)

def create_experiment_and_alternatives(test_name, unparsed_alternatives, conversion):
    experiment = Experiment()
    experiment.name = test_name

    i = 0
    alternatives = []

    for unparsed_alternative in unparsed_alternatives:

        alternative = Alternative()
        alternative.number = i
        alternative.content = unparsed_alternative

        i += 1

    # TODO: set weights appropriately

    return experiment, alternatives
