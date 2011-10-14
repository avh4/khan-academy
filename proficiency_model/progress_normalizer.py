import itertools

class InvFnLinInterpNormalizer(object):
    """
    This is basically a function that takes an accuracy prediction (probability
    of next problem correct) and attempts to "evenly" distribute it in [0, 1]
    such that progress bar appears to fill up linearly.

    The current algorithm is as follows:
    Let
        f(n) = probabilty of next problem correct after doing n problems,
        all of which are correct.
    Let
        g(x) = f^(-1)(x)
    that is, the inverse function of f. Since f is discrete but we want g to be
    continuous, unknown values in the domain of g will be approximated by
    linear interpolation, with the additional artificial ordered pair (0, 0).
    Intuitively, g(x) is a function that takes your accuracy and returns how
    many problems correct in a row it would've taken to get to that, as a real
    number. Thus, our progress display function is just
        h(x) = g(x) / g(consts.PROFICIENCY_ACCURACY_THRESHOLD)
    clamped between [0, 1].

    The rationale behind this is that if you don't get any problems wrong, your
    progress bar will increment by the same amount each time and be full
    right when you're proficient (i.e. reach the required accuracy threshold).

    (Sorry if the explanation is not very clear... best to draw a graph of f(n)
    and g(x) to see for yourself.)

    This is a class because of static initialization of state.
    """

    def __init__(self, accuracy_model, proficiency_threshold):
        self.ordered_pairs = [(0.0, 0.0)]
        self.proficiency_threshold = proficiency_threshold

        for i in itertools.count(1):
            accuracy_model.update(correct=True)
            probability = accuracy_model.predict()
            self.ordered_pairs.append((probability, i))

            if probability >= proficiency_threshold:
                self.ordered_pairs.append((1.0, i + 1))  # sentinel for interpolation
                break

        self.normalized_threshold = self.linear_interpolate(proficiency_threshold)

    def linear_interpolate(self, x):
        # TODO: Use numpy when we get it. This is a brain-dead quick-and-dirty
        #     O(n) implementation.

        # pre: ordered_pairs is ordered on its first element

        prev_x, prev_y = self.ordered_pairs[0]

        for cur_x, cur_y in self.ordered_pairs[1:]:
            if prev_x <= x < cur_x:
                return prev_y + float(x - prev_x) * (cur_y - prev_y) / (cur_x - prev_x)

            prev_x, prev_y = cur_x, cur_y

        raise NotImplementedError('Does not support extrapolation.')

    def normalize(self, p_val):
        def clamp(value, minval, maxval):
            return sorted((minval, value, maxval))[1]

        # TODO: Should fit an exponential curve to the data points so that we
        #     get meaningful values for when p_val is between 0 and x-value of
        #     the first data point.
        return clamp(self.linear_interpolate(p_val) / self.normalized_threshold,
            0.0, 1.0)
