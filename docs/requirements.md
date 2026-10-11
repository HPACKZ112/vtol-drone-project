# Requirements and verification

Owner-confirmed targets are separate from engineering assumptions. A successful
numerical screen is not demonstrated aircraft compliance.

| ID | Requirement / status | Verification | Current evidence |
| --- | --- | --- | --- |
| R01 | Four tilting rotors; confirmed | Geometry and interface review | Aggregate model; placement open |
| R02 | All-up mass at most 5 kg; confirmed | Complete mass budget, then weighing | 3 kg assumed candidate; 5 kg stress case |
| R03 | Around 1 m wingspan; confirmed flexible guide, wing only | Compare candidate dimensions and trade-offs, then measure | 0.949 m starting candidate; no hard span pass/fail; rotor envelope separate |
| R04 | Total flight time at least 1800 s; confirmed target | Energy/load model, then validated mission evidence | Nominal energy screen conditional; upper-mass screen fails |
| R05 | Search-and-rescue observation/basic surveillance concept; confirmed | Define sensor task and observation criteria | Camera/sensor and payload capability open |
| R06 | Around GBP 500 parts; flexible owner target | Dated, complete BOM with inclusions | No parts priced; not assessed |
| R07 | Design study plus hover/forward-transition simulation; confirmed scope | Reproducible results and documented model | Included; ideal attitude/trim, not aircraft validation |
| R08 | Combined peak thrust target 2 times nominal weight; assumed | Sourced thrust/current curves, then measurement | 58.86 N target at 3 kg; hardware capability unknown |
| R09 | Mission fits 80% usable nominal battery energy; assumed allowance | Battery discharge/load measurements and mission model | 88.8 Wh assumed usable; no measured energy |
| R10 | Cruise above estimated stall; margin still to select | Aerodynamic evidence and validated model | Ratios 1.48 at 3 kg, 1.14 at 5 kg; not a safe-speed finding |
| R11 | Results reproducible from committed inputs | Automated tests, report regeneration | Python 3.11/3.12 checks configured |
| R12 | Powered work has reviewed procedures and abort criteria | Safety/configuration/test-record review | Plans only; no powered tests |

## Traceability

R01-R07 map to [the confirmed brief](../data/project_brief.json). R02-R04 and
R08-R10 map to [candidate inputs](../data/sar_design.json),
[mass allowances](../data/sar_mass_budget.csv), and
[the design study](../reports/design-study/summary.md). R07 maps to the
[simulation](../simulation/README.md). R11 maps to the tests and automated workflow.
R12 maps to the [safety plan](safety.md) and [test plan](flight-test-plan.md).

The 30-minute allocation is assumed: 60 s total hover, 50 s total transition, and
1690 s cruise at 22 m/s. The energy model allows for both transitions, but only
forward transition is dynamically simulated. This allocation is not yet a rescue
mission profile with defined observation time, turns, wind, or reserve policy.

## Open engineering requirements

Document full-envelope dimensions and clearance; no overall width limit is set.
Define sensor task/mass/power, wind and weather conditions,
structural load factors, CG range, actuator loads/rates, control authority,
current/thermal limits, budget inclusions, and supervision before hardware work.
Do not fill these with arbitrary pass criteria merely to obtain a green result.
