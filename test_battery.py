import unittest


class SolarBattery:
    def __init__(self, capacity_kwh):
        self.capacity = capacity_kwh
        self.current_charge = 0  # Изначально батарея пустая

    def charge(self, amount):
        if amount < 0:
            raise ValueError("Нельзя заряжать отрицательным током!")

        # Если пытаемся зарядить больше емкости — заряжаем до 100% и всё
        if self.current_charge + amount > self.capacity:
            self.current_charge = self.capacity
        else:
            self.current_charge += amount

    def discharge(self, amount):
        if amount < 0:
            raise ValueError("Нельзя разряжать отрицательным током!")

        if amount > self.current_charge:
            raise ValueError("Недостаточно заряда!")

        self.current_charge -= amount
        return self.current_charge

class TestBattery(unittest.TestCase):
    def setUp(self):
        self.battery = SolarBattery(1000)

    def test_charge_logic(self):
        self.battery.charge(10)

        self.assertEqual(self.battery.current_charge, 10)

    def test_overcharge_cap(self):
        self.battery.charge(2000)

        self.assertEqual(self.battery.current_charge, 1000)

    def test_deep_discharge_error(self):
        with self.assertRaises(ValueError):
            self.battery.discharge(100)