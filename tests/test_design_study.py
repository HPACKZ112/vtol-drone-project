"""Geometry guidance and confirmed project target checks."""

import json
import unittest

from analysis.run_analysis import ROOT, calculate_case, load_config
from analysis.run_design_study import hover_time_cases, target_checks, wing_span_cases


class DesignStudyTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "data/sar_design.json")
        self.brief = json.loads((ROOT / "data/project_brief.json").read_text(encoding="utf-8"))

    def test_derived_geometry_and_duration(self):
        summary, _ = calculate_case(self.config, 3)
        self.assertAlmostEqual(summary["wingspan_m"] ** 2, 0.18 * 5)
        self.assertAlmostEqual(summary["mean_chord_m"] * summary["wingspan_m"], 0.18)
        self.assertEqual(summary["mission_duration_s"], 1800)

    def test_geometry_is_reported_and_mass_limit_is_checked(self):
        checks = target_checks(self.config, 3, self.brief)
        self.assertAlmostEqual(checks["wingspan_m"] ** 2, 0.18 * 5)
        self.assertTrue(checks["duration_meets_target"])
        self.assertFalse(target_checks(self.config, 5.1, self.brief)["mass_within_limit"])

    def test_wingspan_guide_is_not_a_hard_limit(self):
        larger_wing = self.config.copy()
        larger_wing["wing_area_m2"] = 0.25
        checks = target_checks(larger_wing, 3, self.brief)
        self.assertGreater(checks["wingspan_m"], 1.0)
        self.assertGreater(checks["wingspan_difference_from_guide_m"], 0)
        self.assertEqual(checks["wingspan_guide_m"], 1.0)
        self.assertFalse(checks["wingspan_is_hard_limit"])
        self.assertNotIn("span_within_limit", checks)

    def test_upper_mass_does_not_inherit_nominal_energy_pass(self):
        self.assertTrue(target_checks(self.config, 3, self.brief)["energy_within_assumed_budget"])
        self.assertFalse(target_checks(self.config, 5, self.brief)["energy_within_assumed_budget"])

    def test_hover_exchange_preserves_duration_and_energy_difference(self):
        cases = hover_time_cases(self.config, 3, 1800, [60, 300])
        baseline, _ = calculate_case(self.config, 3)
        expected_change = (baseline["electrical_hover_power_w"]
                           - baseline["electrical_cruise_power_w"]) * 240 / 3600
        for row in cases:
            self.assertEqual(row["total_mission_time_s"], 1800)
        self.assertAlmostEqual(cases[1]["mission_energy_wh"] - cases[0]["mission_energy_wh"],
                               expected_change)
        self.assertFalse(cases[1]["energy_within_assumed_budget"])

    def test_impossible_hover_allocation_is_rejected(self):
        for duration in (-1, 1800):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                hover_time_cases(self.config, 3, 1800, [duration])

    def test_span_modes_preserve_their_declared_quantity(self):
        rows = wing_span_cases(self.config, 3, [1.1, 1.4])
        baseline, _ = calculate_case(self.config, 3)
        for row in rows:
            self.assertAlmostEqual(row["aspect_ratio"] * row["wing_area_m2"],
                                   row["wingspan_m"] ** 2)
            if row["comparison"] == "fixed_area":
                self.assertAlmostEqual(row["wing_area_m2"], self.config["wing_area_m2"])
                self.assertAlmostEqual(row["stall_speed_m_s"], baseline["stall_speed_m_s"])
            else:
                self.assertAlmostEqual(row["mean_chord_m"], baseline["mean_chord_m"])
        self.assertLess(rows[1]["cruise_power_w"], rows[0]["cruise_power_w"])

    def test_baseline_span_reproduces_baseline_energy_in_both_modes(self):
        baseline, _ = calculate_case(self.config, 3)
        for row in wing_span_cases(self.config, 3, [baseline["wingspan_m"]]):
            self.assertAlmostEqual(row["mission_energy_wh"], baseline["mission_energy_wh"])

    def test_invalid_spans_are_rejected(self):
        for span in (0, -1, float("nan")):
            with self.subTest(span=span), self.assertRaises(ValueError):
                wing_span_cases(self.config, 3, [span])


if __name__ == "__main__":
    unittest.main()
