import pickle
import logging

# We use a context dict full of pre-pickled values for our cached two_pass_template context,
# so we don't waste time de-pickling entities that aren't used in the second pass.

class PickleContextVal:
    def __init__(self, pickled, val):
        self.pickled = pickled
        self.value = pickle.dumps(val) if self.pickled else val

    def val(self):
        if self.pickled:
            self.value = pickle.loads(self.value)
            self.pickled = False
            return self.value
        else:
            return self.value

# See http://stackoverflow.com/questions/2060972/subclassing-python-dictionary-to-override-setitem
class PickleContextDict(dict):

    def __getitem__(self, key):
        pickle_context_val = super(PickleContextDict, self).__getitem__(key)

        return pickle_context_val.val()

    def __setitem__(self, key, value, pickled=False):
        if isinstance(value, PickleContextVal):
            super(PickleContextDict, self).__setitem__(key, value)
        else:
            super(PickleContextDict, self).__setitem__(key, PickleContextVal(pickled, value))

    def add_pickled(self, dict_to_pickle):
        for key in dict_to_pickle:
            self.__setitem__(key, dict_to_pickle[key], pickled=True)
