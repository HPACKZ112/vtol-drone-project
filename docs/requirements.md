# Requirements and verification

All numerical targets below are **proposed example targets**, not agreed design
requirements or demonstrated capability. Confirm them against the mission and
available resources before selecting components.

| ID | Requirement or proposed target | Verification | Current evidence |
| --- | --- | --- | --- |
| R01 | Vertical take-off, wing-borne cruise, vertical landing | Reviewed dynamics model, then staged testing | Planned |
| R02 | Tilt-rotor or tilt-wing architecture | Weighted trade study and decision review | Tilt-rotor calculation baseline only |
| R03 | All-up mass at or below 3.0 kg, including 0.15 kg payload | Complete mass budget and assembled-aircraft measurement | Assumed mass budget |
| R04 | Combined peak thrust target at least 2.0 times weight | Sourced motor/propeller data and thrust-stand measurement | Calculated target only |
| R05 | Example mission: 60 s total hover, 20 s total transition, 600 s cruise at 18 m/s | Energy calculation, measured loads, validated mission model | Assumed analytical example |
| R06 | Example mission energy at or below 80% of nominal battery energy | Conservative usable-energy estimate, then battery/load tests | Assumed 80% usable fraction |
| R07 | Cruise speed greater than estimated stall speed | Lift calculation, then validated aerodynamic model | Calculation check only; flight margin not selected |
| R08 | Configuration work permits propeller-off arming/disarming checks | Reviewed procedure and ground check | Planned |
| R09 | Every powered test has configuration, conditions, measurements, and abort criteria recorded | Test-record review | Template available; no test records |
| R10 | Python results can be reproduced from committed inputs | Automated numerical tests and report regeneration | Included in repository |

## Unresolved constraints

Budget, span and packaging limits, wind envelope, structural load cases, centre of
gravity, stability margins, controller choice, tilt rate and actuator loading,
maximum current, thermal limits, and local operating requirements remain open.

## Traceability

R03 maps to `data/example_mass_budget.csv`. R04-R07 map to
`analysis/calculations.py` and `reports/example/summary.md`. R08-R09 map to the
safety and test plans. Record changes to targets in the decision log and identify
which reports and checks need to be rerun.
