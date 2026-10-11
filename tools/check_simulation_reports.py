"""Compare saved and regenerated simulation tables with numerical tolerances."""

import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("generated_dir", type=Path)
    args = parser.parse_args()
    expected = ROOT / "reports/simulation"
    errors = []
    for path in sorted(expected.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as stream:
            original = list(csv.DictReader(stream))
        with (args.generated_dir / path.name).open(encoding="utf-8", newline="") as stream:
            regenerated = list(csv.DictReader(stream))
        if len(original) != len(regenerated):
            errors.append(f"{path.name}: row counts differ")
            continue
        for index, (left, right) in enumerate(zip(original, regenerated), start=2):
            if left.keys() != right.keys():
                errors.append(f"{path.name}: columns differ")
                break
            for key in left:
                if left[key] == right[key]:
                    continue
                try:
                    agrees = math.isclose(float(left[key]), float(right[key]),
                                          rel_tol=1e-5, abs_tol=1e-5)
                except ValueError:
                    agrees = False
                if not agrees:
                    errors.append(f"{path.name} row {index}, {key}: {left[key]} != {right[key]}")
    original_inputs = json.loads((expected / "inputs.json").read_text(encoding="utf-8"))
    generated_inputs = json.loads((args.generated_dir / "inputs.json").read_text(encoding="utf-8"))
    if original_inputs != generated_inputs:
        errors.append("Simulation input snapshots differ.")
    if errors:
        for error in errors[:10]:
            print(error)
        return 1
    print("Simulation inputs and CSV outputs match within numerical tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
