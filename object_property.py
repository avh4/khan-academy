# From http://kovshenin.com/archives/app-engine-python-objects-in-the-google-datastore/

from google.appengine.ext import db
import pickle
import simplejson

# Use this property to store objects.
class ObjectProperty(db.BlobProperty):
    def validate(self, value):
        try:
            result = pickle.dumps(value)
            return value
        except pickle.PicklingError, e:
            return super(ObjectProperty, self).validate(value)

    def get_value_for_datastore(self, model_instance):
        result = super(ObjectProperty, self).get_value_for_datastore(model_instance)
        result = pickle.dumps(result)
        return db.Blob(result)

    def make_value_from_datastore(self, value):
        try:
            value = pickle.loads(str(value))
        except:
            pass
        return super(ObjectProperty, self).make_value_from_datastore(value)

class UnvalidatedObjectProperty(ObjectProperty):
    def validate(self, value):
        # pickle.dumps can be slooooooow,
        # sometimes we just want to trust that the item is pickle'able.
        return value

class JsonProperty(db.TextProperty):
    def validate(self, value):
        try:
            result = simplejson.dumps(value)
            return value
        except:
            return super(JsonProperty, self).validate(value)

    def get_value_for_datastore(self, model_instance):
        result = super(JsonProperty, self).get_value_for_datastore(model_instance)
        return db.Text(simplejson.dumps(result))

    def make_value_from_datastore(self, value):
        try:
            value = simplejson.loads(str(value))
        except:
            pass
        return super(JsonProperty, self).make_value_from_datastore(value)

class UnvalidatedJsonProperty(JsonProperty):
    def validate(self, value):
        return value

