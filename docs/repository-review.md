# Professional repository review and necessary additions

Reviewed on 2026-10-11 against commit
`92dd57e52973da44e41b3958eb5378516d7699c8`, then developed using the owner's answers.
Priorities describe engineering/portfolio impact, not proof of aircraft safety.

## Overall judgement

The original repository was a well-organised starter: units, equations, assumptions,
tests, and safety boundaries were visible. It was not yet a mission-specific
mechanical design study. The main weakness was lack of geometry, mechanism/load
evidence, component data, and dynamics, not a need for more complicated Python.

For a second-year aerospace mechanical-placement application, the strongest next
evidence is explainable design reasoning: dimensions, free-body diagrams, torque
and CG calculations, material choices, sensitivity, and traceable decisions.
The project should not imply a built drone or a validated 30-minute rescue capability.

## Findings at the reviewed revision

| Priority | Finding and original location | Consequence | Development status |
| --- | --- | --- | --- |
| P1 | `data/example_design.json`: S=0.55 m^2, AR=6 imply 1.817 m span | Tutorial cannot represent the owner's later sub-1-m aircraft | Separate 0.949 m compact candidate added; tutorial clearly labelled |
| P1 | `hardware/cad/README.md` and `hardware/bom.md`: placeholders only | Rotor packaging, CG, mechanism loads, materials, cost and propulsion feasibility unestablished | Remains essential work; no fabricated CAD or part choices |
| P1 | `simulation/README.md`: no dynamics model | No evidence of hover/transition behaviour | Educational point-mass model added; attitude/transition validation still open |
| P1 | `data/example_design.json` and example report: assumed efficiencies/aerodynamics | A positive energy balance cannot establish the requested endurance | Mission-specific mass/energy and sensitivity studies added; measurements still needed |
| P2 | `analysis/run_analysis.py::load_config`: unknown and duplicate keys accepted | Typos/ambiguous inputs could silently change the intended case | Fixed; regression tests added |
| P2 | `analysis/run_analysis.py::load_mass_budget`: malformed rows/headers and weak identifiers | Incomplete or ambiguous budgets could be reported without error | Fixed; exact columns, row validation, and duplicate-name checks |
| P2 | `load_mass_budget` / report snapshot: notes dropped | Assumption/evidence reasoning lost in published outputs | Fixed; notes retained in snapshots and CSV |
| P2 | `main` with `--no-plots`: old PNG could survive changed inputs | A reader could see a chart belonging to an earlier case | Fixed for recorded data; regenerate after code changes |
| P2 | `docs/requirements.md`, `README.md`: provisional scope | Interviewer could not distinguish owner requirements from tutorial assumptions | Rewritten with confirmed brief, open items, and evidence status |
| P2 | Workflow tested equations but not plotting/dynamics | New outputs could fail independently of scalar tests | Scientific dependencies, solver checks, report comparisons, plotting smoke tests added |

No incorrect scalar equation was identified within the original documented
first-order assumptions. Passing tests cannot compensate for unsupported physical
inputs or omitted mechanisms. Finding locations refer to the reviewed revision;
the updated files now contain the corrections.

## Necessary remaining work, in order

1. **Packaging and mechanical concept.** Dimension all four rotor discs and tilt
   envelopes, wing, fuselage, and landing clearance. Add CG from component positions.
   Close when drawings and a mass-CG table show a physically consistent layout.
2. **Wing and tilt mechanism.** Draw free-body diagrams; calculate wing/root and
   attachment loads, hinge/actuator torque, linkage ratios, travel, backlash, and
   material/print-direction implications. State load cases and justify margins.
   Close with calculations linked to CAD and an assembly/manufacturing plan.
3. **Propulsion, battery, and cost evidence.** Source compatible motor/prop/ESC data
   at the proposed voltage, battery discharge/energy data, and a complete priced BOM.
   Include wiring, servos, payload and agreed budget scope. Recalculate mass/energy
   when choices change; adding battery mass is not a free endurance improvement.
4. **Mission and aerodynamic evidence.** Define observation versus cruise/hover
   time, sensor task, reserve and conditions. Justify CLmax, CD0 and efficiencies
   for geometry and operating point; investigate sensitivity before asserting
   endurance. The 3 kg screen has only 8.3 Wh headroom; 5 kg is 44.7 Wh short.
5. **Geometry-based dynamics.** Add pitch/inertia, rotor moment arms/allocation,
   wing moments and angle-of-attack behaviour, then actuator constraints and
   disturbed cases. Extend to return transition/landing. Ideal trim in the current
   model makes force handover possible by assumption, not by demonstrated control.
6. **Independent evidence and personal ownership.** Obtain appropriate supervision
   before powered work. Record repeatable measurements, model comparisons,
   discrepancies, and your own revisions. Add one concise design report and actual
   CAD images; keep AI/reused work and personal contributions transparent.

Do not rush to hardware purchases to fill repository folders. A sound student
study can be useful in applications now while the physical concept remains open.
Select a licence before intending unrestricted public reuse.

## Owner input applied

The owner confirmed Year 2 Mechanical Engineering at Exeter, university-level
Python/NumPy and calculus, applications already underway, design study plus
simulation, four tilting rotors, maximum 5 kg, below-1-m wing, at least 30 minutes,
SAR/basic observation, basic fabrication tools, and a flexible student budget near
GBP 500. No camera/sensor has been selected. These are recorded in
[the brief](../data/project_brief.json), not replaced with invented decisions.

## Questions for the next design step

- Does the below-1-m limit apply only to the wing, or also the full rotor envelope?
- What observation task matters: visible camera, live feed, recording, or thermal?
  Sensor performance, mass, power, and cost should follow that task.
- Which costs belong in the student budget, and what equipment is already owned?
- Can a university supervisor/workshop support mechanical review and safe testing?

These questions do not block the current preliminary study. Payload, costs,
facilities, and full-envelope limits remain explicitly open until answered.

## Evidence added in this pass

[Candidate sizing](../reports/sar/summary.md),
[mass/energy sensitivity](../reports/design-study/summary.md),
[hover/transition outputs](../reports/simulation/summary.md), and
[verification scope](../tests/README.md) now accompany the confirmed requirements.
All performance numbers remain model estimates from assumed inputs.
