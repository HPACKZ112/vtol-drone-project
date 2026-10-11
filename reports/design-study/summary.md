# Compact tilt-rotor design study

Confirmed targets: four tilting rotors; mass at most 5 kg; at least
30 minutes total flight time. Around 1 m wingspan is a flexible guide,
not a hard limit, and applies to the wing only, not the rotor envelope.
The GBP 500 parts budget is a
flexible student-project target. The observation payload is unselected.

All numerical design inputs and component masses remain assumptions.
These results screen a concept; they do not demonstrate aircraft performance.

The candidate geometry implies a **0.949 m span** and
a **0.190 m mean chord**. Area is 0.18 m^2 and AR is 5.
This is a geometry candidate, not a completed CAD design. A larger span
may be considered through a documented mass, lift/drag, structure, and
packaging trade-off; exceeding the guide is not a requirement failure.

## Mass cases

The 5 kg row is an upper-mass stress case, not the intended all-up mass.
Battery energy, wing, rotor size, and all other inputs stay fixed.

| Mass (kg) | Stall estimate (m/s) | Cruise/stall ratio | Hover power (W) | Mission energy (Wh) | Remaining usable energy (Wh) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2.5 | 13.62 | 1.62 | 269.8 | 70.9 | 17.9 |
| 3.0 | 14.91 | 1.48 | 351.5 | 80.5 | 8.3 |
| 5.0 | 19.25 | 1.14 | 744.8 | 133.5 | -44.7 |

## Interpretation

A lighter concept can fit the assumed energy budget while the upper-mass
case consumes more energy and has less cruise-to-stall margin. A maximum
mass requirement should therefore not be treated as a mass to design towards.
A larger battery adds mass; the energy-needed column in mass_cases.csv is
a fixed-mass estimate, not a completed battery sizing solution.

Sensitivity.csv varies one input at a time by +/-20%. These perturbations
are illustrative comparisons, not measured uncertainty intervals or
probability distributions. They identify assumptions worth investigating.

For the nominal case, 20% higher CD0 raises demand to 88.8 Wh, just over
the 88.8 Wh usable allowance (88.819 Wh in sensitivity.csv).
20% lower cruise propeller efficiency raises demand to 96.5 Wh.
A positive nominal screen is therefore not a robust endurance conclusion.

## Outstanding feasibility checks

- Source motor/propeller thrust and current curves and battery discharge data.
- Justify drag, lift, and efficiency inputs for the selected configuration.
- Lay out all four rotor discs and tilt envelopes with verified clearance.
- Design the tilt mechanism, wing structure, attachments, and centre of gravity.
- Check attitude/control authority and transition/landing behaviour.
- Select the observation payload and price a complete component BOM.

## Target screen

- mass_within_limit: True
- wingspan_m: 0.9486832980505138
- wingspan_guide_m: 1.0
- wingspan_difference_from_guide_m: -0.05131670194948623
- wingspan_is_hard_limit: False
- duration_meets_target: True
- energy_within_assumed_budget: True
- cost_status: Not assessed: no sourced component selections
- payload_status: Not assessed: camera/sensor is unselected
