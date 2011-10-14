import math
import itertools
import operator

import consts

class AccuracyModel(object):
    """
    Predicts the probabilty of the next problem correct using logistic regression.
    """

    # FIXME(david): versioning
    def __init__(self, user_exercise=None, keep_all_state=False):
        # See http://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average
        # These are seeded on the mean correct of a sample of 1 million problem logs
        self.ewma_3 = 0.9
        self.ewma_10 = 0.9

        if keep_all_state:
            self.streak = 0
            self.total_done = 0
            self.total_correct = 0

        if user_exercise is not None:
            # Switching the user from streak model to new accuracy model. Use
            # current streak as known history, and simulate streak correct answers.
            for i in xrange(0, user_exercise.streak):
                self.update(True)

    def update(self, correct):
        def update_exp_moving_avg(y, prev, weight):
            return float(weight) * y + float(1 - weight) * prev

        self.ewma_3 = update_exp_moving_avg(correct, self.ewma_3, 0.333)
        self.ewma_10 = update_exp_moving_avg(correct, self.ewma_10, 0.1)

        if hasattr(self, 'streak'):  # Keeping all state ourself
            self.streak = self.streak + 1 if correct else 0
            self.total_done += 1
            self.total_correct += correct

    def predict(self, user_exercise=None):
        """
        Returns: the probabilty of the next problem correct using logistic regression.
        """

        total_done = user_exercise.total_done if user_exercise else self.total_done
        total_correct = user_exercise.total_correct if user_exercise else self.total_correct

        # We don't try to predict the first problem (no user-exercise history)
        if total_done == 0:
            return consts.PROBABILITY_FIRST_PROBLEM_CORRECT

        # TODO(david): These values should not be in the raw script itself.
        #     Perhaps import as a dict from a Python file.
        INTERCEPT = -0.6384147

        # Get values for the feature vector X
        ewma_3 = self.ewma_3
        ewma_10 = self.ewma_10
        current_streak = user_exercise.streak if user_exercise else self.streak
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
