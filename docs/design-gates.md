# Small design gates and next work

Gates are evidence questions, not a corporate certification process or permission
for powered tests.

| Gate | Next decision | Evidence to close it | Status |
| --- | --- | --- | --- |
| G1 Mission | How much observation hover is needed? | Owner transit/hover/observation profile, sensor task, energy comparison | Asked; baseline assumed |
| G2 Mechanical | Can four tilts form a plausible layout? | Dimensions, swept clearance, mass-CG, wing/root and tilt-torque free-body calculations | Geometry open |
| G3 Parts | Which affordable combination supports loads? | Compatible propulsion/battery/servo data, current/energy/load checks, complete cost/mass allowances | No selections/quotes |
| G4 Model | Which prediction can be independently checked first? | Hand checks, geometry/moments, justified aero/actuation and repeatable comparison plan | Software verification, no aircraft validation |

## Risks and small next actions

| Risk | Why it matters | Action |
| --- | --- | --- |
| Hover task differs from baseline | Five minutes total hover fails the current energy screen | Confirm duty cycle before battery resizing |
| Larger span appears to offer free performance | Sweeps hold structure mass/coefficients fixed | Recalculate mass/CG, loads and aero before choosing span |
| Ideal control hides authority limits | Aggregate forces have no moments/allocation | Define rotor centres, hinges and actuator limits |
| Parts exceed student resources | Allowances are not sourced selections | Record budget inclusions and compatible shortlists |
| Presentation outruns personal evidence | Scaffold is AI-assisted; personal technical work unconfirmed | Complete and explain one derivation/drawing |

## Mechanical inputs

Start with a sketch: axes/origin, wing, fuselage, rotor centres, hinges, battery
and sensor allowance. Compare hover/cruise and the swept geometry. Use component
positions for mass-weighted CG and stated loads for moments. Distinguish thrust,
mechanism weight, inertial and aerodynamic loads; a mass allowance does not rate
a servo. CAD software and printer model are requested before assuming process
capability, print fit, materials or tolerances.

[CAD guidance](../hardware/cad/README.md) is the home for actual models and revisions.
Powered work still needs the [safety plan](safety.md), [staged tests](flight-test-plan.md),
appropriate facilities and supervision.
