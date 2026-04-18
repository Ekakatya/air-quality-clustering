import unittest

def get_discount_price(price, discount):
    """
    Calculates price after discount.
    price: float (e.g. 100.0)
    discount: float (e.g. 0.2 for 20%)
    """
    return price * (1 - discount)

class TestingDiscount(unittest.TestCase):
    def test_happy_path(self):
        self.assertEqual(get_discount_price(100, 0.2), 80)

    def test_zero_price(self):
        self.assertEqual(get_discount_price(0, 0.2), 0)

    def test_neg_price(self):
        with self.assertRaises(ValueError):
            get_discount_price(-100, 0)
