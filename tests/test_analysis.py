"""Input loading, mission accounting, and end-to-end report generation."""

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from analysis.run_analysis import (ROOT, calculate_case, load_config,
                                   load_mass_budget, plot_data, remove_stale_plot,
                                   sensitivity_tables, write_reports)


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

    def test_unknown_config_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            config = self.config.copy()
            config["cruise_speeed_m_s"] = 25
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cruise_speeed_m_s"):
                load_config(path)

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            content = json.dumps(self.config)
            content = content.replace('"rotor_count": 4',
                                      '"rotor_count": 2, "rotor_count": 4')
            path = Path(directory) / "config.json"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                load_config(path)

    def test_mass_budget_notes_survive_loading(self):
        battery = next(row for row in self.masses if row["component"] == "Battery")
        self.assertIn("no product selected", battery["notes"])

    def test_ambiguous_mass_budget_rows_are_rejected(self):
        header = "component,quantity,unit_mass_kg,evidence,notes\n"
        examples = [
            header + "Battery,1,1,assumed,test,unexpected cell\n",
            header + "Battery,1,1,   ,test\n",
            header + "Battery,1,1,assumed\n",
            header + "Battery,1,1,assumed,test\nBattery,1,1,assumed,test\n",
            "component,quantity,unit_mass_kg,evidence,notes,quantity\n"
            "Battery,1,1,assumed,test,2\n",
        ]
        for content in examples:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "mass.csv"
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_mass_budget(path)

    def test_no_plots_removes_a_chart_from_a_different_case(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / "power_sensitivity.png").write_bytes(b"previous chart")
            (output / "plot_data.json").write_text('{"case": "previous"}', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-S", str(ROOT / "analysis/run_analysis.py"),
                 "--no-plots", "--output-dir", str(output)],
                capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((output / "power_sensitivity.png").exists())
            self.assertFalse((output / "plot_data.json").exists())

    def test_matching_chart_is_preserved(self):
        summary, _ = calculate_case(self.config, self.mass_kg)
        mass_rows, speed_rows = sensitivity_tables(self.config, self.mass_kg)
        record = plot_data(self.config, summary, mass_rows, speed_rows)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            chart = output / "power_sensitivity.png"
            chart.write_bytes(b"matching chart")
            (output / "plot_data.json").write_text(json.dumps(record), encoding="utf-8")
            self.assertFalse(remove_stale_plot(output, record))
            self.assertEqual(chart.read_bytes(), b"matching chart")

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

    def test_report_formatting_ignores_insignificant_float_differences(self):
        summary, segments = calculate_case(self.config, self.mass_kg)
        mass_rows, speed_rows = sensitivity_tables(self.config, self.mass_kg)
        reports = []
        for target in (14.715 - 1e-12, 14.715 + 1e-12):
            with tempfile.TemporaryDirectory() as directory:
                varied_summary = summary.copy()
                varied_summary["target_peak_thrust_per_rotor_n"] = target
                write_reports(directory, self.config, self.masses, varied_summary,
                              segments, mass_rows, speed_rows)
                reports.append((Path(directory) / "summary.md").read_text(encoding="utf-8"))
        self.assertEqual(reports[0], reports[1])


if __name__ == "__main__":
    unittest.main()
