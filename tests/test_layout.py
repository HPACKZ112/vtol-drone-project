"""Independent geometry integrals, moment balance, and provisional screens."""

import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analysis import calculations as calc
from analysis.layout import (battery_position, centre_of_gravity, disc_point,
                             hover_balance, load_layouts, rotor_envelope, screen_layout,
                             unequal_hover_power)
from analysis.run_analysis import ROOT, load_config, load_mass_budget


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "data/sar_design.json")
        self.masses = load_mass_budget(ROOT / "data/sar_mass_budget.csv")
        self.settings = load_layouts(ROOT / "data/provisional_layouts.json")

    def test_zero_hub_offset_plan_projection_is_hover_disc(self):
        result = rotor_envelope(2, 0)
        self.assertAlmostEqual(result["disc_area_m2"], math.pi)
        self.assertAlmostEqual(result["plan_sweep_area_m2"], math.pi)
        self.assertEqual(result["x_min_relative_hinge_m"], -1)
        self.assertEqual(result["z_max_relative_hinge_m"], 1)

    def test_swept_area_matches_independent_midpoint_integration(self):
        radius, offset, steps = 0.1525, 0.04, 10000
        dy = 2 * radius / steps
        widths = []
        for step in range(steps):
            y = -radius + (step + 0.5) * dy
            u = math.sqrt(radius ** 2 - y ** 2)
            widths.append(u + math.hypot(u, offset))
        area = math.fsum(widths) * dy
        self.assertAlmostEqual(rotor_envelope(2 * radius, offset)["plan_sweep_area_m2"], area, places=6)

    def test_sampled_disc_points_are_within_analytical_bounds(self):
        diameter, offset = 0.305, 0.04
        envelope = rotor_envelope(diameter, offset)
        for tilt in range(0, 91, 3):
            for phase in range(0, 360, 6):
                u = diameter / 2 * math.cos(math.radians(phase))
                v = diameter / 2 * math.sin(math.radians(phase))
                x, y, z = disc_point(diameter, offset, math.radians(tilt), u, v)
                self.assertGreaterEqual(x + 1e-12, envelope["x_min_relative_hinge_m"])
                self.assertLessEqual(x, envelope["x_max_relative_hinge_m"] + 1e-12)
                self.assertLessEqual(abs(y), envelope["y_half_extent_m"] + 1e-12)
                self.assertGreaterEqual(z + 1e-12, envelope["z_min_relative_hinge_m"])
                self.assertLessEqual(z, envelope["z_max_relative_hinge_m"] + 1e-12)
                self.assertAlmostEqual(math.sqrt(x*x + y*y + z*z), envelope["bounding_sphere_radius_m"])

    def test_hover_and_cruise_disc_poses(self):
        self.assertEqual(disc_point(2, 0.5, 0, 1, 0), (1, 0, 0.5))
        x, y, z = disc_point(2, 0.5, math.pi / 2, 1, 0)
        self.assertAlmostEqual(x, -0.5)
        self.assertEqual(y, 0)
        self.assertAlmostEqual(z, 1)

    def test_invalid_envelope_and_disc_points_fail(self):
        for diameter, offset in ((0, 0), (-1, 0), (1, -1), (True, 0), (1, math.nan)):
            with self.subTest(inputs=(diameter, offset)), self.assertRaises(ValueError):
                rotor_envelope(diameter, offset)
        for tilt, u, v in ((-1, 0, 0), (math.pi, 0, 0), (0, 2, 0), (0, math.nan, 0)):
            with self.subTest(inputs=(tilt, u, v)), self.assertRaises(ValueError):
                disc_point(2, 0, tilt, u, v)

    def test_mass_weighted_cg_and_battery_solution(self):
        other = [{"mass_kg": 1, "x_m": 0.2}]
        battery_x = battery_position(other, 1, 0.15)
        self.assertAlmostEqual(battery_x, 0.1)
        self.assertAlmostEqual(centre_of_gravity(other + [{"mass_kg": 1, "x_m": battery_x}]), 0.15)
        with self.assertRaises(ValueError):
            centre_of_gravity([])

    def test_hover_balance_preserves_force_and_moment(self):
        balance = hover_balance(20, 0, 1, 0.25)
        self.assertEqual(balance["front_each_n"], 7.5)
        self.assertEqual(balance["rear_each_n"], 2.5)
        self.assertEqual(2 * (balance["front_each_n"] + balance["rear_each_n"]), 20)
        self.assertEqual(balance["front_each_n"] * 0.25, balance["rear_each_n"] * 0.75)
        for cg in (-0.1, 0, 1, 1.1, math.nan):
            with self.subTest(cg=cg), self.assertRaises(ValueError):
                hover_balance(20, 0, 1, cg)

    def test_equal_loading_reproduces_sizing_and_unequal_needs_more_power(self):
        equal = hover_balance(29.43, -1, 1, 0)
        unequal = hover_balance(29.43, -1, 1, 0.5)
        ideal = calc.ideal_hover_power_w(29.43, 1.225, calc.rotor_disk_area_m2(4, 0.305))
        expected = calc.electrical_hover_power_w(ideal, 0.65, 0.85, 10)
        self.assertAlmostEqual(unequal_hover_power(self.config, equal), expected)
        self.assertGreater(unequal_hover_power(self.config, unequal), expected)

    def test_default_trial_clearance_and_mass_conservation(self):
        results = []
        for layout in self.settings["layouts"]:
            result, clearances, other, battery_mass = screen_layout(self.config, self.masses, layout, self.settings)
            results.append(result)
            self.assertAlmostEqual(math.fsum(row["mass_kg"] for row in other) + battery_mass, 3)
            self.assertAlmostEqual(centre_of_gravity(other + [{"mass_kg": battery_mass, "x_m": result["required_battery_x_m"]}]), result["reference_cg_x_m"])
            if layout["id"] == "A":
                self.assertAlmostEqual(clearances["rear_pair_gap_m"], -0.005)
        self.assertEqual([row["disc_sweep_screen_met"] for row in results], [False, True, True, True])
        self.assertEqual([row["battery_reference_reachable"] for row in results], [True, True, True, False])
        self.assertGreater(results[2]["front_support_thrust_moment_nm"], results[1]["front_support_thrust_moment_nm"])

    def test_battery_cg_shift_has_expected_mass_ratio(self):
        result, _, _, battery_mass = screen_layout(self.config, self.masses, self.settings["layouts"][1], self.settings)
        expected_shift = battery_mass / result["mass_kg"] * (self.settings["battery_max_x_m"] - self.settings["battery_min_x_m"])
        self.assertAlmostEqual(result["cg_max_x_m"] - result["cg_min_x_m"], expected_shift)

    def test_four_rotor_requirement_and_changed_mass_rules_fail(self):
        config = self.config.copy()
        config["rotor_count"] = 3
        with self.assertRaises(ValueError):
            screen_layout(config, self.masses, self.settings["layouts"][0], self.settings)
        with self.assertRaises(ValueError):
            screen_layout(self.config, self.masses[:-1], self.settings["layouts"][0], self.settings)

    def test_rear_mass_increase_can_exceed_compact_battery_travel(self):
        layout = self.settings["layouts"][1]
        result, _, other, battery_mass = screen_layout(self.config, self.masses, layout, self.settings)
        extra_mass = 0.1
        position = battery_position(other + [{"mass_kg": extra_mass, "x_m": layout["rear_x_m"]}],
                                    battery_mass, result["reference_cg_x_m"])
        expected = result["required_battery_x_m"] + extra_mass * (result["reference_cg_x_m"] - layout["rear_x_m"]) / battery_mass
        self.assertAlmostEqual(position, expected)
        self.assertLess(position, self.settings["battery_min_x_m"])

    def test_malformed_settings_fail(self):
        variations = []
        for key, value in (("unexpected", 1), ("hub_axial_offset_m", -1), ("battery_min_x_m", 1), ("layouts", [])):
            settings = copy.deepcopy(self.settings)
            settings[key] = value
            variations.append(settings)
        settings = copy.deepcopy(self.settings)
        settings["layouts"][1]["id"] = "A"
        variations.append(settings)
        settings = copy.deepcopy(self.settings)
        settings["layouts"][0]["front_x_m"] = math.nan
        variations.append(settings)
        settings = copy.deepcopy(self.settings)
        del settings["planning_clearance_m"]
        variations.append(settings)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            for index, settings in enumerate(variations):
                path.write_text(json.dumps(settings), encoding="utf-8")
                with self.subTest(case=index), self.assertRaises(ValueError):
                    load_layouts(path)

    def test_cli_generates_complete_numerical_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-m", "analysis.run_layout_study", "--no-plots", "--output-dir", directory],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            required = {"summary.md", "comparison.csv", "clearances.csv", "mass_positions.csv", "battery_sweep.csv", "inputs.json", "rotor_envelope.json"}
            self.assertEqual({path.name for path in Path(directory).iterdir()}, required)


if __name__ == "__main__":
    unittest.main()
