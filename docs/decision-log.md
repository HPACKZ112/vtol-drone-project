# Design decision log

Record a question, alternatives, evidence, and a decision before treating a design
choice as fixed. A provisional choice can be changed when better evidence arrives.

| ID | Date | Question | Current decision | Reason and evidence | Revisit when |
| --- | --- | --- | --- | --- | --- |
| D01 | 2026-10-11 | Which VTOL family? | Tilt-rotor or tilt-wing | Project owner's stated direction | Trade study complete |
| D02 | 2026-10-11 | Which configuration for the first calculation? | Four identical tilting rotors, provisional | Simple equal-load analytical baseline; no hardware evidence | Layout and propulsion shortlist exist |
| D03 | 2026-10-11 | How should calculations be implemented? | Standard Python functions and files; Matplotlib for plots | University-level readability and reproducibility | A new method requires additional tooling |
| D04 | 2026-10-11 | What evidence do initial values represent? | Assumptions only | No measured data provided with the starter | Measurements or sourced selections are added |
| D05 | 2026-10-11 | Which architecture after owner review? | Retain four tilting rotors; supersedes D01/D02's provisional status | Owner explicitly selected tilt-rotor and retained the four-rotor arrangement | Feasibility review identifies a necessary change |
| D06 | 2026-10-11 | Which mission and size targets? | SAR/basic observation, at least 30 minutes, below 1 m wing span, at most 5 kg | Owner's answers, recorded in project_brief.json | Mission profile or packaging is clarified |
| D07 | 2026-10-11 | How to apply the mass ceiling? | Study 3 kg candidate and compare 2.5/5 kg; not design towards 5 kg | Assumed masses; upper case fails energy screen with fixed battery | Sourced parts and mass-CG budget exist |
| D08 | 2026-10-11 | Which compact geometry to investigate? | S=0.18 m^2, AR=5, V=22 m/s; provisional candidate | Derives 0.949 m span; not validated aerodynamics or CAD | Rotor clearance, structure, and aero evidence exist |
| D09 | 2026-10-11 | Budget and payload? | Flexible student prototype near GBP 500; sensor undecided | Owner's clarification; no purchase or part selection | Priced shortlist and payload task exist |
| D10 | 2026-10-11 | Which simulation depth now? | Educational point mass with ideal attitude/trim; SciPy ODE solver | Appropriate incremental model for current Python/calculus background | Geometry/inertia permit attitude model |
| D11 | 2026-10-11 | What does the span guidance mean? | Around 1 m, flexible and wing-only; supersedes D06's below-1-m wording | Owner clarified wing-only scope and that it is a rough guide, not a hard limit | A justified span trade-off or a new owner constraint |
| D12 | 2026-10-11 | What evidence should the next review prioritise? | Mission duty-cycle and span comparisons now; personal mechanical work next | Three simulated review lenses; mission and layout inputs requested | Owner answers and geometry/component evidence exist |
| D13 | 2026-10-11 | How should the owner's rough layout be developed? | Rear pair on horizontal tail; all four rotors tilt forward; dimensioned layout pending | Owner supplied original sketch and confirmed both choices; hand equation sheet also supplied | CG, rotor envelope, tail/boom load path and mechanism calculations identify changes |
| D14 | 2026-10-11 | Which provisional geometry next? | Compare A/B/C/D; AI-assisted shortlist B with C as alternative, not owner selection | Disc sweep and fixed-mass CG screen; B fixes overlap but has front-heavy thrust/forward battery, C has longer loaded supports | Owner preference, battery fit, measured masses and structural/aero/component evidence |

The 0.15 kg payload allowance and 58.86 N simulated thrust ceiling are analysis
assumptions, not owner specifications or measured part ratings. This log preserves
the original provisional choices rather than rewriting their history.

## New decision template

- Date and author:
- Question and affected requirement IDs:
- Alternatives and evaluation criteria:
- Evidence, sources, and uncertainty:
- Decision and reasoning:
- Cost, mass, power, and testing implications:
- Validation required and reason to revisit:
