# Small design gates and next work

Gates are evidence questions, not a corporate certification process or permission
for powered tests.

| Gate | Next decision | Evidence to close it | Status |
| --- | --- | --- | --- |
| G1 Mission | How much observation hover is needed? | Owner transit/hover/observation profile, sensor task, energy comparison | Asked; baseline assumed |
| G2 Mechanical | Can the tail-mounted rear pair and front pair form a plausible layout? | Dimensions, swept clearance, mass-CG, wing/tail/boom and tilt-torque free-body calculations | Owner sketch and tilt intent supplied; dimensions/loads open |
| G3 Parts | Which affordable combination supports loads? | Compatible propulsion/battery/servo data, current/energy/load checks, complete cost/mass allowances | No selections/quotes |
| G4 Model | Which prediction can be independently checked first? | Numerical hand checks, geometry/moments, justified aero/actuation and repeatable comparison plan | Owner equation sheet supplied; software verification, no aircraft validation |

## Risks and small next actions

| Risk | Why it matters | Action |
| --- | --- | --- |
| Hover task differs from baseline | Five minutes total hover fails the current energy screen | Confirm duty cycle before battery resizing |
| Larger span appears to offer free performance | Sweeps hold structure mass/coefficients fixed | Recalculate mass/CG, loads and aero before choosing span |
| Ideal control hides authority limits | Aggregate forces have no moments/allocation | Define rotor centres, hinges and actuator limits |
| Tail mounting adds propulsion loads | Rear rotor thrust/tilt loads act through horizontal tail and boom | Draw the load path; calculate bending/twist and attachment loads |
| Parts exceed student resources | Allowances are not sourced selections | Record budget inclusions and compatible shortlists |
| Presentation outruns personal evidence | Equation sheet and rough sketch exist; numerical workings/CAD still open | Extend the owner's sheet with numbers/units and dimension the sketch |

## Mechanical inputs

Extend the [owner's sketch](personal-work.md): axes/origin, wing, fuselage, rotor centres, hinges, battery
and sensor allowance. Compare hover/cruise and the swept geometry. Use component
positions for mass-weighted CG and stated loads for moments. Distinguish thrust,
mechanism weight, inertial and aerodynamic loads; a mass allowance does not rate
a servo. CAD software and printer model are requested before assuming process
capability, print fit, materials or tolerances.

[CAD guidance](../hardware/cad/README.md) is the home for actual models and revisions.
Powered work still needs the [safety plan](safety.md), [staged tests](flight-test-plan.md),
appropriate facilities and supervision.
