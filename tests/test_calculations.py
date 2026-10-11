"""Hand-evaluable equations, invalid inputs, and physical trends."""

import math
import unittest

from analysis import calculations as calc


class CalculationTests(unittest.TestCase):
    def test_weight_and_total_rotor_area(self):
        self.assertAlmostEqual(calc.weight_n(2, 10), 20)
        self.assertAlmostEqual(calc.rotor_disk_area_m2(4, 1), math.pi)

    def test_hover_power_hand_calculation(self):
        # sqrt(8 / (2 * 1 * 1)) = 2 m/s, so P = 8 * 2 = 16 W.
        self.assertAlmostEqual(calc.ideal_hover_power_w(8, 1, 1), 16)
        self.assertAlmostEqual(calc.electrical_hover_power_w(16, 0.5, 0.8, 2), 42)

    def test_equal_rotor_powers_sum_to_combined_disc_result(self):
        # Owner's equation sheet uses total weight with total area, not one disc.
        count = 4
        total_thrust = 29.43
        single_area = math.pi * (0.305 / 2) ** 2
        each_power = calc.ideal_hover_power_w(total_thrust / count, 1.225, single_area)
        combined_power = calc.ideal_hover_power_w(
            total_thrust, 1.225, calc.rotor_disk_area_m2(count, 0.305))
        self.assertAlmostEqual(count * each_power, combined_power)

    def test_personal_equation_sheet_numerical_examples(self):
        # AI-assisted examples in docs/personal-work.md, not values in the photo.
        area = calc.rotor_disk_area_m2(4, 0.305)
        self.assertAlmostEqual(area, 0.292246657, places=8)
        cases = [(3.0, 29.43, 7.3575, 188.680742, 351.503605),
                 (5.0, 49.05, 12.2625, 405.976317, 744.798764)]
        for mass, weight, each_thrust, ideal, electrical in cases:
            with self.subTest(mass_kg=mass):
                self.assertAlmostEqual(calc.weight_n(mass, 9.81), weight)
                self.assertAlmostEqual(weight / 4, each_thrust)
                power = calc.ideal_hover_power_w(weight, 1.225, area)
                self.assertAlmostEqual(power, ideal, places=5)
                self.assertAlmostEqual(
                    calc.electrical_hover_power_w(power, 0.65, 0.85, 10),
                    electrical, places=5)

    def test_stall_speed_hand_calculation(self):
        self.assertAlmostEqual(calc.stall_speed_m_s(10, 1, 2, 1), math.sqrt(10))

    def test_cruise_drag_hand_calculation(self):
        # q=50 Pa, CL=0.4, CD=0.02 + 0.16/(4*pi), D=50*CD.
        expected_drag = 1 + 2 / math.pi
        self.assertAlmostEqual(calc.cruise_drag_n(20, 10, 1, 1, 4, 1, 0.02, 1),
                               expected_drag)

    def test_cruise_power_accounts_for_both_efficiencies(self):
        self.assertAlmostEqual(calc.electrical_cruise_power_w(100, 10, 0.5, 0.8, 10),
                               2510)

    def test_battery_and_seconds_to_hours_conversion(self):
        self.assertAlmostEqual(calc.usable_battery_energy_wh(10, 2, 0.8), 16)
        self.assertAlmostEqual(calc.segment_energy_wh(100, 36), 1)
        self.assertEqual(calc.segment_energy_wh(100, 0), 0)

    def test_hover_mass_scaling(self):
        baseline = calc.ideal_hover_power_w(10, 1, 1)
        heavier = calc.ideal_hover_power_w(20, 1, 1)
        self.assertAlmostEqual(heavier / baseline, 2 ** 1.5)

    def test_double_diameter_halves_ideal_hover_power(self):
        small = calc.ideal_hover_power_w(10, 1, calc.rotor_disk_area_m2(4, 1))
        large = calc.ideal_hover_power_w(10, 1, calc.rotor_disk_area_m2(4, 2))
        self.assertAlmostEqual(large / small, 0.5)

    def test_rejects_non_physical_mass(self):
        for value in (0, -1, math.nan, math.inf, True, "3"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calc.weight_n(value, 9.81)

    def test_rotor_count_is_a_positive_integer(self):
        for value in (0, -2, 2.5, 4.0, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calc.rotor_disk_area_m2(value, 0.3)

    def test_efficiencies_must_be_in_range(self):
        for value in (0, -0.1, 1.1, math.nan):
            with self.subTest(value=value), self.assertRaises(ValueError):
                calc.electrical_hover_power_w(10, value, 0.8, 0)

    def test_cruise_at_or_below_stall_is_rejected(self):
        for speed in (1, 2):
            with self.subTest(speed=speed), self.assertRaises(ValueError):
                calc.cruise_drag_n(2, speed, 1, 1, 4, 0.8, 0.02, 1)

    def test_negative_duration_is_rejected(self):
        with self.assertRaises(ValueError):
            calc.segment_energy_wh(10, -1)


if __name__ == "__main__":
    unittest.main()
