# Three-lens review: recruitment, leadership, engineering

Reviewed on 2026-10-11 at commit
`cffea99be6fc6249e7490cc2b40e027253ce91c4`.
This is a simulated three-person review with company-specific discussion angles,
not feedback from Airbus, Rolls-Royce, BAE Systems, their CEOs, or hiring teams.
There was no external panel and no access to private selection criteria.

## Combined judgement

Readable Python, explicit assumptions, tests and honest boundaries make this a
credible analytical starting point for a second-year student. It does not yet
show enough personal mechanical-design evidence to distinguish the student from
the AI-assisted scaffold. Explainable geometry/load/component work is more
valuable next than more folders, complex controls, or a claim of a completed drone.

The 30-minute result depends on a cruise-heavy mission and assumed performance.
Use the study in applications with those boundaries visible; do not claim measured
endurance, stable aircraft transition, or an operational rescue product.

## 1. Talent acquisition scout

| Company lens | Positive evidence | Concern | Best next addition |
| --- | --- | --- | --- |
| Airbus | Academic equations connected to an aircraft question; requirements and reproducibility visible | What did the student personally derive, code, design or review? | Short design brief and a personally explained wing/mechanism decision with drawings |
| Rolls-Royce | Power, efficiency and energy reasoning support relevant analytical discussion | Can the student explain losses, uncertainty and units independently? | Hand calculation, sourced propulsion comparison, predicted-versus-measured plan |
| BAE Systems | Traceability, tests, limits and safety awareness show disciplined habits | Are claims defensible and contributions transparent? | Contribution record, a corrected error, and concise evidence map |

These are our inferences, not hiring predictions. Airbus describes internships
as connecting academic knowledge with practical experience and advises matching
applications to actual skills and experience.
[Airbus internship guidance](https://www.airbus.com/en/careers/students-and-graduates/interns).
Rolls-Royce's emerging-talent information emphasises skills, behaviours and experience.
[Rolls-Royce student opportunities](https://careers.rolls-royce.com/en/students-and-graduates).
BAE Systems describes recruitment behaviours including reliability, curiosity,
learning and action.
[BAE Systems joining guidance](https://www.baesystems.com/careers/join-us).
None of these sources provides a score for this repository.

## 2. CEO / business leadership

| Company lens | Leadership question | Student-project assessment | Proportionate improvement |
| --- | --- | --- | --- |
| Airbus | Does mission connect to integration and delivery? | Useful educational scope; observation needs and integration unclear | Define observation versus transit time and the next decision, not more features |
| Rolls-Royce | Is performance credible enough to guide effort? | Losses and small margins matter more than nominal green checks | Compare mission duty cycle and geometry; identify the first assumption needing evidence |
| BAE Systems | Are purpose, accountable decisions and risk visible? | Labelled modelling is appropriate; operational claims premature | Keep responsible observation scope, evidence gates, and cost/safety boundaries explicit |

These hypothetical leadership judgements are not corporate strategy or quotations.
Investment here means student time and modest parts spending, not a commercial
business case. A corporate certification programme or market forecast is not
required for a good Year 2 study. Prioritise one small, finishable engineering question.

## 3. Senior engineer

| Company lens | Strongest feature | Concern | Next evidence |
| --- | --- | --- | --- |
| Airbus | Aircraft-level force/energy calculations | Rotor clearance, CG, wing/root loads and control authority unknown | Dimensioned layout, mass-CG calculation, wing/attachment load cases |
| Rolls-Royce | Separate shaft/electrical efficiency assumptions | Thrust ceiling and propulsion/battery performance are not hardware data | Compatible operating-point data and electrical/current/load assessment |
| BAE Systems | Automated comparisons and documented limits | Checks must reject missing evidence; ideal trim cannot establish stability | Complete-table checks, independent checks, geometry-based moments and actuator constraints |

Scalar equations appear consistent with their first-order assumptions. The
point-mass simulator teaches force sharing but assumes attitude and trim control.
More controller states without geometry/inertia/actuator evidence would not
resolve that weakness.

## Prioritised findings and response

1. **High: personal technical ownership unconfirmed.** README and portfolio
   guidance disclose AI help but do not establish personal technical work. Added
   a factual [contribution record](contributions.md); asked the owner for completed
   work and a preferred public name, rather than inventing achievements.
2. **High: observation mission unspecified.** Candidate inputs allocate only
   60 s total hover. New [hover cases](../reports/design-study/hover_time_cases.csv)
   exchange cruise for hover at fixed total duration. Five minutes total hover
   estimates 94.1 Wh versus 88.8 Wh usable. Asked how much hover is intended.
3. **High: mechanical integration absent.** The [CAD folder](../hardware/cad/README.md)
   contains guidance, not an aircraft. Rotor envelope, CG, loads and tilt torque
   cannot be inferred from span. Added [small gates](design-gates.md); requested
   rotor-layout, CAD and fabrication inputs. No invented CAD or ratings were added.
4. **Medium: flexible span not yet explored.** Added fixed-area and fixed-mean-chord
   comparisons up to 1.4 m. A larger wing does not automatically improve energy.
   All retain assumed mass/coefficients; stiffness, extra structure, interference
   and aerodynamic changes remain excluded.
5. **Medium: simulation verification could falsely succeed.** At the
   [reviewed checker, line 19](https://github.com/HPACKZ112/vtol-drone-project/blob/cffea99be6fc6249e7490cc2b40e027253ce91c4/tools/check_simulation_reports.py#L19),
   only existing expected CSVs are compared. With none present, equal input
   snapshots can produce success without trajectories. Empty matching tables
   and matching nonfinite text could also bypass meaningful checks. Reproduced
   missing-table success in a failing test; fixed completeness, schema, nonempty
   and finite-number checks. This does not imply previous actual tables were missing.
6. **Medium: first review path too long.** Added a generated
   [decision brief](../reports/design-study/decision-brief.md) and
   [evidence map](evidence-map.md), without fabricated achievements or measurements.

## Combined next decision

Confirm observation hover time and layout inputs, then develop one personally
explainable mechanical study. Do not freeze the assumed wing, rotors, battery or
payload allowance merely because they appear in the current case. Revise from
evidence and record why. The [original review](repository-review.md) remains as history.
