# Evidence map

A navigation aid, not a maturity score or aircraft approval.

| Claim / question | Evidence now | Level | Still required |
| --- | --- | --- | --- |
| Four tilts, at most 5 kg, at least 30 minutes | [Confirmed brief](../data/project_brief.json) | Owner targets | Feasibility/compliance evidence |
| Around 1 m wing-only guide is flexible | Brief, [D11](decision-log.md) | Owner guidance | Dimensions and justified span choice |
| Candidate span 0.949 m | [Sizing](../reports/sar/summary.md) | Derived from assumed S/AR | CAD/clearance |
| Nominal energy about 80.5 Wh | [Mission table](../reports/sar/mission_energy.csv) | First-order estimate | Operating data, mission definition, validation |
| More hover increases this case's energy | [Hover cases](../reports/design-study/hover_time_cases.csv) | Fixed-duration comparison | Owner input and realistic loads |
| Span changes have different consequences | [Wing cases](../reports/design-study/wing_span_cases.csv) | Fixed-mass/coefficients comparison | Structural mass/stiffness and aero evidence |
| Hover/forward transition simulated | [Simulation](../reports/simulation/summary.md) | Point mass, ideal attitude/trim | Moments, inertia, allocation, actuator/aero data |
| Numerical checks pass | Tests and GitHub workflow | Software verification | Not aircraft validation |
| Personal hover equation sheet and rough layout exist | [Originals and review](personal-work.md), [contributions](contributions.md) | Owner-identified work | Numerical hand substitutions, dimensions and load diagrams |
| Rear pair on horizontal tail; all four tilt forward | [Architecture](architecture.md), [D13](decision-log.md) | Owner design intent | CG, clearance, tail/boom strength and tilt mechanism evidence |
| Hardware/cost/sensor meet targets | [BOM](../hardware/bom.md) | Not assessed | Sourced selections, budget scope, measurements |

Use confirmed requirement, assumed, modelled, verified implementation, and measured
accurately. Tests cannot turn an assumed coefficient or ideal control force into
measured capability.
