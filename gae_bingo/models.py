
def Experiment(db.Model):
    name = db.StringProperty()
    live = db.BooleanProperty(default = False)
    dt_started = db.DateTimeProperty()

    @staticmethod
    def key_for_name(name):
        return "_gae_experiment:%s" % name

    @staticmethod
    def exists(name):
        return cache.exists(Experiment.key_for_name(name))

def Alternative(db.Model):
    uid = db.IntegerProperty()
    experiment_name = db.StringProperty()
    content = db.TextProperty()
    weight = db.FloatProperty()
    conversions = db.IntegerProperty(default = 0)
    participants = db.IntegerProperty(default = 0)

    def key_for_self(self):
        return "_gae_alternative:%s:%s" % (self.parent.name, self.alternative_id)

