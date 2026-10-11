# Verification

Run from the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests use Python's standard `unittest` module. They check independently
evaluable equations, unit conversions, mass/rotor-size scaling, rejected physical
inputs, mission energy accounting, and report generation from a different working
directory without third-party packages.

They establish consistency with the documented equations, not accuracy for a real
aircraft. Compare predictions with calibrated measurements before claiming model
validation. Hardware and flight validation belong in dated test records.
