# Data and evidence status

| Files | Meaning |
| --- | --- |
| `project_brief.json` | Requirements and context confirmed by the owner on 2026-10-11 |
| `sar_design.json`, `sar_mass_budget.csv` | Assumed compact design candidate; not selected hardware |
| `example_design.json`, `example_mass_budget.csv` | Original tutorial; its wing exceeds the project's span limit |

The candidate mass sums to 3 kg including battery, a 0.15 kg unselected payload
allowance, and contingency. The owner specified a 5 kg maximum, not a 3 kg target
or a 0.15 kg payload. Four 0.305 m propellers, a 22.2 V / 5 Ah battery, and all
aerodynamic/efficiency numbers remain assumptions. Cost is not assessed.

Use SI units; battery capacity is Ah, energy Wh, durations seconds. Values ending
in `_fraction` lie in (0, 1]. Hover and transition times are combined mission
allowances for take-off/landing and both transitions respectively. They are not
durations extracted from the dynamics simulation.

## Input checks

Configuration rejects missing/unknown fields, duplicate JSON keys, nonfinite or
nonphysical numbers, and invalid rotor counts. CSV columns must be exactly
`component,quantity,unit_mass_kg,evidence,notes`. Rows require unique nonempty
component names, nonempty evidence, positive integer quantities, and positive
finite masses. Extra/missing cells and duplicate columns are rejected. Notes are
retained in generated snapshots to preserve the reasoning behind allowances.

## Future measurement records

- Instrument, calibration, resolution, uncertainty, and repeated readings.
- Date, component identifiers, configuration, and environmental conditions.
- Column names/units, sample interval, processing steps, and excluded-sample reasons.
- Source URLs and retrieval dates for vendor data; distinguish claims from measurements.

Keep private raw logs in `data/raw/private/`; publish only reviewed, anonymised
copies. Never relabel assumed inputs as measured values.
