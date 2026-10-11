"""Input loading, mission accounting, and end-to-end report generation."""

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analysis.run_analysis import ROOT, calculate_case, load_config, load_mass_budget


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "data/example_design.json")
        self.masses = load_mass_budget(ROOT / "data/example_mass_budget.csv")
        self.mass_kg = sum(row["total_mass_kg"] for row in self.masses)

    def test_example_mass_budget_includes_payload_and_battery(self):
        self.assertAlmostEqual(self.mass_kg, 3.0)
        names = [row["component"] for row in self.masses]
        self.assertIn("Battery", names)
        self.assertIn("Payload", names)
        self.assertTrue(all(row["evidence"] == "assumed" for row in self.masses))

    def test_mission_segments_and_energy_balance(self):
        summary, segments = calculate_case(self.config, self.mass_kg)
        self.assertAlmostEqual(summary["usable_battery_energy_wh"], 88.8)
        self.assertAlmostEqual(summary["hover_thrust_per_rotor_n"], 7.3575)
        self.assertAlmostEqual(summary["target_peak_thrust_per_rotor_n"], 14.715)
        self.assertAlmostEqual(summary["mission_energy_wh"],
                               sum(row["energy_wh"] for row in segments))
        self.assertAlmostEqual(summary["remaining_usable_energy_wh"]
                               + summary["mission_energy_wh"], 88.8)

    def test_transition_factor_does_not_multiply_auxiliary_load(self):
        summary, segments = calculate_case(self.config, self.mass_kg)
        expected = ((summary["electrical_hover_power_w"] - 10) * 1.2 + 10)
        self.assertAlmostEqual(segments[1]["power_w"], expected)

    def test_energy_shortfall_remains_negative(self):
        config = self.config.copy()
        config["cruise_time_s"] = 36000
        summary, _ = calculate_case(config, self.mass_kg)
        self.assertFalse(summary["mission_energy_within_budget"])
        self.assertLess(summary["remaining_usable_energy_wh"], 0)

    def test_invalid_or_missing_config_field_is_rejected(self):
        for key, value in (("battery_capacity_ah", -1),
                           ("usable_battery_fraction", 1.2),
                           ("air_density_kg_m3", None),
                           ("thrust_to_weight_target", 0.9),
                           ("rotor_count", 4.5)):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as directory:
                config = self.config.copy()
                config[key] = value
                path = Path(directory) / "config.json"
                path.write_text(json.dumps(config), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_config(path)

    def test_bad_mass_budget_is_rejected(self):
        examples = [
            "component,quantity,unit_mass_kg,evidence,notes\nBattery,1,-1,assumed,test\n",
            "component,quantity,unit_mass_kg,evidence,notes\nBattery,1.5,1,assumed,test\n",
            "component,quantity,unit_mass_kg,evidence,notes\n",
            "component,mass\nBattery,1\n",
        ]
        for content in examples:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "budget.csv"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_mass_budget(path)

    def test_script_runs_from_another_directory_without_plot_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "results"
            result = subprocess.run(
                [sys.executable, "-S", str(ROOT / "analysis/run_analysis.py"),
                 "--no-plots", "--output-dir", str(output)],
                cwd=directory, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["mass_kg"], 3.0)
            self.assertIn("assumed", summary["evidence_status"])
            with (output / "mission_energy.csv").open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 3)
            self.assertTrue((output / "summary.md").is_file())
            self.assertFalse((output / "power_sensitivity.png").exists())


if __name__ == "__main__":
    unittest.main()
