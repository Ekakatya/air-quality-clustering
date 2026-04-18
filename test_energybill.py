import unittest


class EnergyBill:
    def __init__(self, peak_rate, off_peak_rate):
        self.peak_rate = peak_rate  # Цена за кВт*ч днем
        self.off_peak_rate = off_peak_rate  # Цена за кВт*ч ночью
        self.total_cost = 0  # Изначально счет пустой

    def add_consumption(self, kwh, is_peak=False):
        if kwh < 0:
            raise ValueError("Consumption cannot be negative")

        # Выбираем тариф
        rate = self.peak_rate if is_peak else self.off_peak_rate

        # Добавляем к общей сумме
        self.total_cost += kwh * rate

    def apply_discount(self, percent):
        if percent < 0 or percent > 100:
            raise ValueError("Discount must be between 0 and 100")

        # Уменьшаем сумму на процент
        discount_amount = self.total_cost * (percent / 100)
        self.total_cost -= discount_amount

class TestEnergyBill(unittest.TestCase):
    def setUp(self):
        self.bill = EnergyBill(10, 5)

    def test_peak_calculation(self):
        self.bill.add_consumption(10, is_peak=True)
        self.assertEqual(self.bill.total_cost, 100)

    def test_discount_logic(self):
        self.bill.add_consumption(20, is_peak=False)
        self.bill.apply_discount(20)
        self.assertEqual(self.bill.total_cost, 80)

    def test_invalid_discount_error(self):
        with self.assertRaises(ValueError):
            self.bill.apply_discount(150)

