"""Geometry guidance and confirmed project target checks."""

import json
import unittest

from analysis.run_analysis import ROOT, calculate_case, load_config
from analysis.run_design_study import target_checks


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


if __name__ == "__main__":
    unittest.main()
