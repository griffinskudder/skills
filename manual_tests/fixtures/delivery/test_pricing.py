import unittest

from pricing import total


class PricingTests(unittest.TestCase):
    def test_multiple_units(self):
        self.assertEqual(total(7, 3), 21)
