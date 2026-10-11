"""Missing simulation evidence must not produce a successful comparison."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import check_simulation_reports as checker


class ReportCheckTests(unittest.TestCase):
    def run_check(self, root, generated):
        with patch.object(checker, "ROOT", root):
            with patch("sys.argv", ["check_simulation_reports.py", str(generated)]):
                with redirect_stdout(io.StringIO()):
                    return checker.main()

    def make_directories(self, root):
        expected = root / "reports/simulation"
        generated = root / "regenerated"
        for directory in (expected, generated):
            directory.mkdir(parents=True)
            (directory / "inputs.json").write_text(
                json.dumps({"masses_kg": [3.0]}), encoding="utf-8")
        return expected, generated

    def test_missing_expected_tables_cannot_report_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, generated = self.make_directories(root)
            self.assertNotEqual(self.run_check(root, generated), 0)

    def make_tables(self, directories):
        for directory in directories:
            for name in ("summary.csv", "hover_3.0kg.csv", "transition_3.0kg.csv"):
                (directory / name).write_text("time_s,value\n0,1\n", encoding="utf-8")

    def test_complete_matching_tables_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            self.assertEqual(self.run_check(root, generated), 0)

    def test_missing_regenerated_trajectory_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            (generated / "transition_3.0kg.csv").unlink()
            self.assertNotEqual(self.run_check(root, generated), 0)

    def test_empty_tables_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            for directory in (expected, generated):
                (directory / "summary.csv").write_text("time_s,value\n", encoding="utf-8")
            self.assertNotEqual(self.run_check(root, generated), 0)

    def test_extra_table_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            (generated / "unexpected.csv").write_text("a\n1\n", encoding="utf-8")
            self.assertNotEqual(self.run_check(root, generated), 0)

    def test_numeric_tolerance_is_used_but_large_changes_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            table = generated / "summary.csv"
            table.write_text("time_s,value\n0,1.000001\n", encoding="utf-8")
            self.assertEqual(self.run_check(root, generated), 0)
            table.write_text("time_s,value\n0,2\n", encoding="utf-8")
            self.assertNotEqual(self.run_check(root, generated), 0)

    def test_matching_nonfinite_values_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, generated = self.make_directories(root)
            self.make_tables((expected, generated))
            for directory in (expected, generated):
                (directory / "summary.csv").write_text("time_s,value\n0,nan\n", encoding="utf-8")
            self.assertNotEqual(self.run_check(root, generated), 0)

    def test_ambiguous_mass_case_filenames_fail(self):
        with self.assertRaises(ValueError):
            checker.required_tables({"masses_kg": [3.01, 3.02]})

    def test_malformed_table_cells_and_headers_fail(self):
        contents = ("time_s,value\n0,1,extra\n", "time_s,value\n0\n",
                    "time_s,value\n,\n", "time_s,time_s\n0,1\n")
        for content in contents:
            with self.subTest(content=content), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                expected, generated = self.make_directories(root)
                self.make_tables((expected, generated))
                (generated / "summary.csv").write_text(content, encoding="utf-8")
                self.assertNotEqual(self.run_check(root, generated), 0)


if __name__ == "__main__":
    unittest.main()
