import unittest


class WindTurbine:
    def __init__(self):
        self.is_running = False  # Сначала выключена
        self.error_log = []  # Журнал ошибок пуст
        self.current_power = 0

    def start_up(self):
        self.is_running = True

    def stop(self):
        self.is_running = False
        self.current_power = 0

    def log_critical_error(self, error_code):
        # Записываем ошибку в журнал
        self.error_log.append(error_code)
        # При критической ошибке турбина останавливается
        self.stop()

    def generate_energy(self, wind_speed):
        if wind_speed < 0:
            raise ValueError("Ветер не может быть отрицательным")

        if not self.is_running:
            self.current_power = 0
            return 0

        # Формула: энергия = куб скорости ветра
        self.current_power = wind_speed ** 3
        return self.current_power


class TestWindTurbine(unittest.TestCase):

    def setUp(self):
        self.turbine = WindTurbine()

    def test_startup_status(self):
        self.turbine.start_up()
        self.assertTrue(self.turbine.is_running)

    def test_error_logging(self):
        self.turbine.log_critical_error("ERROR_505")
        self.assertIn("ERROR_505", self.turbine.error_log)

    def test_security_stop(self):
        self.turbine.stop()
        self.turbine.log_critical_error('OVERHEAT')
        self.assertFalse(self.turbine.is_running)

    def test_positive_generation(self):
        self.turbine.start_up()
        self.turbine.generate_energy(10)
        self.assertGreater(self.turbine.current_power, 0)

if __name__ == '__main__':
    unittest.main()
