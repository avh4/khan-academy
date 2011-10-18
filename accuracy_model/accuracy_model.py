import itertools
import logging
import math
import operator
import unittest

from parameters import log_reg_full_history_tail1m as params

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
        # TODO(david): Allow these seeds to be adjusted or passed in, or at
        #     least use a more accurate seed (one that corresponds to P(first
        #     problem correct)).
        self.ewma_3 = 0.9
        self.ewma_10 = 0.9

        # This is kept here because this is not equivalent to
        # UserExercise.total_done. The latter counts total problems completed
        # (solved), this one counts problems where the user made an attempt at
        # an answer. The distinction is significant when a user incorrectly
        # answers a problem - UserExercise.total_done would not be incremented,
        # whereas this would (which is what we want).
        # TODO(david): Is there a better solution that doesn't require
        #     storing this additional state?
        self.total_attempted = 0

        if keep_all_state:
            self.streak = 0
            self.total_correct = 0

        if user_exercise is not None:
            # Switching the user from streak model to new accuracy model. Use
            # current streak as known history, and simulate streak correct answers.
            for i in xrange(0, user_exercise.streak):
                self.update(True)

    def update(self, correct):
        if self.version != AccuracyModel.CURRENT_VERSION:
            self.update_to_new_version()

        def update_exp_moving_avg(y, prev, weight):
            return float(weight) * y + float(1 - weight) * prev

        self.ewma_3 = update_exp_moving_avg(correct, self.ewma_3, 0.333)
        self.ewma_10 = update_exp_moving_avg(correct, self.ewma_10, 0.1)
        self.total_attempted += 1

        if hasattr(self, 'streak'):
            self.streak = self.streak + 1 if correct else 0

        if hasattr(self, 'total_correct'):
            self.total_correct += correct

    def update_to_new_version(self):
        """
        Updates old AccuracyModel objects to new objects. This function should
        be updated whenever we make a change to the internal state of this
        class.
        """

        # Bump this up when bumping up CURRENT_VERSION. This is here to ensure
        # that this function gets updated along with CURRENT_VERSION.
        UPDATE_TO_VERSION = 1
        assert UPDATE_TO_VERSION == AccuracyModel.CURRENT_VERSION

    def predict(self, user_exercise=None):
        """
        Returns: the probabilty of the next problem correct using logistic regression.
        """

        if self.version != AccuracyModel.CURRENT_VERSION:
            self.update_to_new_version()

        def get_feature_value(feature):
            return getattr(self, feature, getattr(user_exercise, feature, None))

        total_correct = get_feature_value('total_correct')

        # We don't try to predict the first problem (no user-exercise history)
        if self.total_attempted == 0:
            return PROBABILITY_FIRST_PROBLEM_CORRECT

        # Get values for the feature vector X
        ewma_3 = self.ewma_3
        ewma_10 = self.ewma_10
        current_streak = get_feature_value('streak')
        log_num_done = math.log(self.total_attempted)
        log_num_missed = math.log(self.total_attempted - total_correct + 1)  # log (num_missed + 1)
        percent_correct = float(total_correct) / self.total_attempted

        weighted_features = [
            (ewma_3, params.EWMA_3),
            (ewma_10, params.EWMA_10),
            (current_streak, params.CURRENT_STREAK),
            (log_num_done, params.LOG_NUM_DONE),
            (log_num_missed, params.LOG_NUM_MISSED),
            (percent_correct, params.PERCENT_CORRECT),
        ]

        X, weight_vector = zip(*weighted_features)  # unzip the list of pairs

        return AccuracyModel.logistic_regression_predict(params.INTERCEPT, weight_vector, X)

    # See http://en.wikipedia.org/wiki/Logistic_regression
    @staticmethod
    def logistic_regression_predict(intercept, weight_vector, X):
        # TODO(david): Use numpy's dot product fn when we support numpy
        dot_product = sum(itertools.imap(operator.mul, weight_vector, X))
        z = dot_product + intercept

        return 1.0 / (1.0 + math.exp(-z))

    @staticmethod
    def simulate(answer_history):
        model = AccuracyModel(keep_all_state=True)
        for response in answer_history:
            model.update(response)

        return model.predict()

    # The minimum number of problems correct in a row to be greater than the given threshold
    @staticmethod
    def min_streak_till_threshold(threshold):
        model = AccuracyModel(keep_all_state=True)

        for i in itertools.count(1):
            model.update(correct=True)

            if model.predict() >= threshold:
                return i

################################################################################

class TestSequenceFunctions(unittest.TestCase):
    """
    Loose-bounded tests for the accuracy model - sanity tests as well as
    tests for correct behavior expected of an accuracy model. Tries not to be
    flaky.
    """

    @staticmethod
    def to_bool_generator(str_sequence):
        return ((l == '1') for l in str_sequence)

    def setUp(self):
        self.sim = lambda str_sequence: AccuracyModel.simulate(TestSequenceFunctions.to_bool_generator(str_sequence))
        self.lt = lambda seq_smaller, seq_larger: self.assertTrue(self.sim(seq_smaller) < self.sim(seq_larger))

    def test_bounded_in_0_1_interval(self):
        sequences = ['', '1', '0', '000', '111', '1' * 100, '0' * 5000, '1' * 5000, '1101111110111']
        for seq in sequences:
            self.assertTrue(0 <= self.sim(seq) <= 1.0)

    def test_more_is_stronger(self):
        # Longer streaks should give the model greater confidence, manifesting as more extreme predictions
        self.assertTrue(self.sim('') < self.sim('1') < self.sim('11') < self.sim('111') < self.sim('1111'))
        self.assertTrue(self.sim('') > self.sim('0') > self.sim('00') > self.sim('000') > self.sim('0000'))

    def test_weigh_recent_more(self):
        # Should weigh more recent answers greater
        self.lt('0', '1')
        self.lt('10', '01')
        self.lt('110', '101')
        self.lt('010', '001')
        self.lt('1010', '0101')

    def test_sanity(self):
        # Some loose general bounds... if these are violated, something fishy's going on...
        self.assertTrue(self.sim('1' * 20) > 0.95)
        self.assertTrue(self.sim('0' * 20) < 0.8)
        self.assertTrue(0.5 < self.sim('0') < self.sim('') < self.sim('1') < 0.95)

    def test_expected_behavior(self):
        self.lt('11110', '1111')
        self.lt('11110', '111101')
        self.lt('0000', '00001')
        self.lt('0', '01')
        self.lt('10', '1')

if __name__ == '__main__':
    unittest.main()
