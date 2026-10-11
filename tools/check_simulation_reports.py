"""Compare saved and regenerated simulation tables with numerical tolerances."""

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def required_tables(inputs):
    if not isinstance(inputs, dict):
        raise ValueError("Simulation input snapshot must be an object.")
    masses = inputs.get("masses_kg")
    if not isinstance(masses, list) or not masses:
        raise ValueError("Simulation input snapshot needs a nonempty mass list.")
    for mass in masses:
        if (isinstance(mass, bool) or not isinstance(mass, (int, float))
                or not math.isfinite(mass) or mass <= 0):
            raise ValueError("Simulation masses must be finite and positive.")
    names = {"summary.csv"}
    for mass in masses:
        for scenario in ("hover", "transition"):
            names.add(f"{scenario}_{mass:.1f}kg.csv")
    if len(names) != 1 + 2 * len(masses):
        raise ValueError("Mass cases would produce duplicate trajectory filenames.")
    return names


def read_table(path):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        rows = list(reader)
    if (not fields or any(not field.strip() for field in fields)
            or len(fields) != len(set(fields)) or not rows
            or any(None in row or any(value is None or not value.strip()
                                     for value in row.values()) for row in rows)):
        raise ValueError(f"{path.name}: empty or malformed table")
    return fields, rows


def compare_reports(expected, generated):
    errors = []
    try:
        original_inputs = json.loads((expected / "inputs.json").read_text(encoding="utf-8"))
        generated_inputs = json.loads((generated / "inputs.json").read_text(encoding="utf-8"))
        names = required_tables(original_inputs)
    except (OSError, ValueError) as error:
        return [f"Cannot check simulation evidence: {error}"]
    if original_inputs != generated_inputs:
        errors.append("Simulation input snapshots differ.")
    for directory, label in ((expected, "Committed"), (generated, "Regenerated")):
        actual = {path.name for path in directory.glob("*.csv")}
        for name in sorted(names - actual):
            errors.append(f"{label} table missing: {name}")
        for name in sorted(actual - names):
            errors.append(f"{label} unexpected table: {name}")
    if errors:
        return errors
    for name in sorted(names):
        try:
            fields, original = read_table(expected / name)
            new_fields, regenerated = read_table(generated / name)
        except (OSError, ValueError) as error:
            errors.append(str(error))
            continue
        if fields != new_fields:
            errors.append(f"{name}: columns differ")
            continue
        if len(original) != len(regenerated):
            errors.append(f"{name}: row counts differ")
            continue
        for index, (left, right) in enumerate(zip(original, regenerated), start=2):
            for key in left:
                try:
                    a, b = float(left[key]), float(right[key])
                    agrees = (math.isfinite(a) and math.isfinite(b)
                              and math.isclose(a, b, rel_tol=1e-5, abs_tol=1e-5))
                except ValueError:
                    agrees = left[key] == right[key]
                if not agrees:
                    errors.append(f"{name} row {index}, {key}: {left[key]} != {right[key]}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated_dir", type=Path)
    args = parser.parse_args()
    errors = compare_reports(ROOT / "reports/simulation", args.generated_dir)
    if errors:
        for error in errors[:10]:
            print(error)
        return 1
    print("Simulation inputs and CSV outputs match within numerical tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
