import logging
import math
import itertools
import operator

# TODO(david): Find out what this actually is
PROBABILITY_FIRST_PROBLEM_CORRECT = 0.8

class AccuracyModel(object):
    """
    Predicts the probabilty of the next problem correct using logistic regression.
    """

    # Bump this whenever you change the state we keep around so we can
    # reconstitute existing old AccuracyModel objects. Also remember to update
    # the function update_to_new_version accordingly.
    CURRENT_VERSION = 1

    def __init__(self, user_exercise=None, keep_all_state=False):
        self.version = AccuracyModel.CURRENT_VERSION

        # See http://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
        # These are seeded on the mean correct of a sample of 1 million problem logs
        self.ewma_3 = 0.9
        self.ewma_10 = 0.9

        if keep_all_state:
            self.keep_all_state = True
            self.streak = 0
            self.total_done = 0
            self.total_correct = 0

        if user_exercise is not None:
            # Switching the user from streak model to new accuracy model. Use
            # current streak as known history, and simulate streak correct answers.
            for i in xrange(0, user_exercise.streak):
                self.update(True)

    def update(self, correct, **kwargs):
        if self.version != AccuracyModel.CURRENT_VERSION:
            self.update_to_new_version()

        def update_exp_moving_avg(y, prev, weight):
            return float(weight) * y + float(1 - weight) * prev

        self.ewma_3 = update_exp_moving_avg(correct, self.ewma_3, 0.333)
        self.ewma_10 = update_exp_moving_avg(correct, self.ewma_10, 0.1)

        if hasattr(self, 'keep_all_state'):
            self.streak = self.streak + 1 if correct else 0
            self.total_done += 1
            self.total_correct += correct

        if kwargs:
            self.__dict__.update(kwargs)

        # TODO(david): Delete any unused features as optimization

    def update_to_new_version(self):
        """
        Updates old AccuracyModel objects to new objects. This function should
        be updated whenever we make a change to the internal state of this
        class.
        """

        # Bump this up when bumping up CURRENT_VERSION. This is here to ensure
        # that this function gets updated along with CURRENT_VERSION.
        UPDATE_TO_VERSION = 1
        assert(UPDATE_TO_VERSION == AccuracyModel.CURRENT_VERSION)

    def predict(self, user_exercise=None):
        """
        Returns: the probabilty of the next problem correct using logistic regression.
        """

        if self.version != AccuracyModel.CURRENT_VERSION:
            self.update_to_new_version()

        def get_feature_max_value(feature):
            return max(getattr(self, feature, 0.0), getattr(user_exercise, feature, 0.0))

        total_done = get_feature_max_value('total_done')
        total_correct = get_feature_max_value('total_correct')

        # We don't try to predict the first problem (no user-exercise history)
        if total_done == 0:
            return consts.PROBABILITY_FIRST_PROBLEM_CORRECT

        # TODO(david): These values should not be in the raw script itself.
        #     Perhaps import as a dict from a Python file.
        INTERCEPT = -0.6384147

        # Get values for the feature vector X
        ewma_3 = self.ewma_3
        ewma_10 = self.ewma_10
        current_streak = get_feature_max_value('streak')
        log_num_done = math.log(total_done)
        log_num_missed = math.log(total_done - total_correct + 1)  # log (num_missed + 1)
        percent_correct = float(total_correct) / total_done

        weighted_features = [
            (ewma_3, 0.9595278),
            (ewma_10, 1.3383701),
            (current_streak, 0.0070444),
            (log_num_done, 0.4862635),
            (log_num_missed, -0.7135976),
            (percent_correct, 0.6336906),
        ]

        X, weight_vector = zip(*weighted_features)  # unzip the list of pairs

        return AccuracyModel.logistic_regression_predict(INTERCEPT, weight_vector, X)

    # See http://en.wikipedia.org/wiki/Logistic_regression
    @staticmethod
    def logistic_regression_predict(intercept, weight_vector, X):
        # TODO: Use numpy's dot product fn when we support numpy
        dot_product = sum(itertools.imap(operator.mul, weight_vector, X))
        z = dot_product + intercept

        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def simulate(answer_history):
        model = AccuracyModel(keep_all_state=True)
        for response in answer_history:
            model.update(response)

        return model.predict()
