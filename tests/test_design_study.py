"""Geometry constraints and confirmed project target checks."""

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

    def test_geometry_and_mass_limits_are_checked(self):
        checks = target_checks(self.config, 3, self.brief)
        self.assertTrue(checks["span_within_limit"])
        self.assertTrue(checks["duration_meets_target"])
        self.assertFalse(target_checks(self.config, 5.1, self.brief)["mass_within_limit"])
        oversized = self.config.copy()
        oversized["wing_area_m2"] = 0.2
        self.assertFalse(target_checks(oversized, 3, self.brief)["span_within_limit"])

    def test_upper_mass_does_not_inherit_nominal_energy_pass(self):
        self.assertTrue(target_checks(self.config, 3, self.brief)["energy_within_assumed_budget"])
        self.assertFalse(target_checks(self.config, 5, self.brief)["energy_within_assumed_budget"])


if __name__ == "__main__":
    unittest.main()
