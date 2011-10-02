# From http://kovshenin.com/archives/app-engine-python-objects-in-the-google-datastore/

from google.appengine.ext import db
import pickle

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


class TsvProperty(db.UnindexedProperty):
    '''
    An alternative to StringListProperty that serializes lists using a simple
    tab-separated format. This is much faster than StringPropertyList, however
    elements with tabs are not permitted.
    '''
    data_type = list

    def get_value_for_datastore(self, model_instance):
        value = super(TsvProperty, self).get_value_for_datastore(model_instance)
        return db.Text("\t".join(value))

    def make_value_from_datastore(self, value):
        return value.split("\t")

# the following properties are useful for migrating StringListProperty to
# the faster TsvProperty

class TsvCompatStringListProperty(db.StringListProperty):
    'A StringListProperty that can also lists serialized as read tab separated strings'
    def make_value_from_datastore(self, value):
        if isinstance(value, list):
            return value
        else:
            return value.split("\t")

class StringListCompatTsvProperty(TsvProperty):
    'A TsvProperty that can also read lists serialized as native Python lists'
    def make_value_from_datastore(self, value):
        if isinstance(value, list):
            return value
        else:
            return value.split("\t")
