"""
Loose-bounded tests for the accuracy model - sanity tests as well as
tests for correct behavior expected of an accuracy model. Tries not to be
flaky.
"""

import unittest

from accuracy_model import AccuracyModel

class TestSequenceFunctions(unittest.TestCase):

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
        # Some loose general bounds (very unscientific)... at least if these
        # are violated, we know something fishy's going on.
        self.assertTrue(self.sim('1' * 20) > 0.95)
        self.assertTrue(self.sim('0' * 20) < 0.8)
        self.assertTrue(0.3 < self.sim('0') < 0.8)
        self.assertTrue(0.4 < self.sim('') < 0.9)
        self.assertTrue(0.5 < self.sim('1') < 1.0)

    def test_expected_behavior(self):
        self.lt('11110', '1111')
        self.lt('11110', '111101')
        self.lt('0000', '00001')
        self.lt('0', '01')
        self.lt('10', '1')

if __name__ == '__main__':
    unittest.main()
