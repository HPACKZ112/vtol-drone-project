"""Force equilibrium and numerical convergence, not aircraft validation."""

import math
import unittest

from analysis.run_analysis import ROOT, load_config
from simulation.planar import CONTROL, forces_and_derivatives, simulate, speed_reference


class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "data/sar_design.json")
        self.mass = 3.0

    def test_hover_equilibrium(self):
        state = [0, CONTROL["reference_altitude_m"], 0, 0, 0]
        derivatives, values = forces_and_derivatives(0, state, self.config, self.mass, "hover")
        for value in derivatives:
            self.assertAlmostEqual(value, 0)
        self.assertAlmostEqual(values["total_thrust_n"], self.mass * 9.81)

    def test_trimmed_level_cruise_equilibrium(self):
        state = [0, CONTROL["reference_altitude_m"], 22, 0, math.pi / 2]
        derivatives, values = forces_and_derivatives(60, state, self.config, self.mass, "transition")
        self.assertAlmostEqual(derivatives[0], 22)
        for value in derivatives[1:]:
            self.assertAlmostEqual(value, 0)
        self.assertAlmostEqual(values["wing_support_fraction"], 1)

    def test_thrust_and_tilt_rate_are_limited(self):
        state = [0, -100, 0, 0, 0]
        derivatives, values = forces_and_derivatives(60, state, self.config, self.mass, "transition")
        self.assertLessEqual(values["total_thrust_n"], 2 * self.mass * 9.81)
        self.assertTrue(values["thrust_limited"])
        self.assertLessEqual(abs(derivatives[4]), math.radians(20))

    def test_speed_command_starts_and_finishes_smoothly(self):
        self.assertEqual(speed_reference(5, self.config, "transition"), 0)
        self.assertEqual(speed_reference(30, self.config, "transition"), 22)
        self.assertEqual(speed_reference(60, self.config, "hover"), 0)

    def test_upper_mass_keeps_the_same_thrust_ceiling(self):
        state = [0, -100, 0, 0, 0]
        for mass in (3, 5):
            _, values = forces_and_derivatives(60, state, self.config, mass, "transition")
            self.assertAlmostEqual(values["total_thrust_n"], 58.86)

    def test_solver_step_refinement_and_hover_recovery(self):
        try:
            import scipy  # noqa: F401
        except ImportError:
            self.skipTest("Install requirements.txt for solver tests.")
        _, hover = simulate(self.config, self.mass, "hover")
        self.assertLess(abs(hover["final_altitude_error_m"]), 0.001)
        coarse, _ = simulate(self.config, self.mass, "transition", 0.1)
        fine, _ = simulate(self.config, self.mass, "transition", 0.05)
        self.assertEqual(len(coarse), len(fine))
        for left, right in zip(coarse, fine):
            for key in ("x_m", "altitude_m", "forward_speed_m_s", "vertical_speed_m_s", "tilt_deg"):
                self.assertAlmostEqual(left[key], right[key], delta=0.001)


if __name__ == "__main__":
    unittest.main()
