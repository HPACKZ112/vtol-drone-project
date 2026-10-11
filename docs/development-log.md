# Development log

Keep short dated entries that explain the engineering work. Link the relevant
commit, drawing, measurement, plot, or test record. Record failed ideas and what
they taught you as well as successful results.

## 2026-10-11 - Repository foundation

- Work completed: starter documentation and an illustrative Python sizing workflow.
- Design direction supplied by the project owner: tilt-rotor or tilt-wing.
- Baseline assumption: four identical tilting rotors with equal hover loads.
- Assistance: initial scaffold, calculations, and checks prepared with AI assistance.
- Evidence: example input files, generated reports, and automated numerical tests.
- Limit: no component selection, hardware measurements, or flight evidence added.
- Next task: confirm requirements and compare tilt-rotor with tilt-wing.

### Verification correction

The first GitHub run passed all equation tests but exposed a 0.01 N difference in
the displayed peak thrust target between Python 3.11 and 3.12. Improved summation
and consistent report rounding remove the formatting difference. A regression
test covers values immediately either side of the rounding boundary.

## 2026-10-11 - Owner requirements and repository review

- Owner supplied course/year, existing Python/maths background, aerospace-placement
  audience, tools, and design-study/simulation scope. Applications are already underway.
- Confirmed four-tilt layout, 5 kg maximum, sub-1-m wing, 30-minute target, SAR/basic
  surveillance mission, flexible student budget, and no selected camera/sensor.
- Review of commit `92dd57e52973da44e41b3958eb5378516d7699c8` identified a tutorial
  geometry mismatch and missing mechanical/dynamics evidence. It did not establish
  that the concept is physically feasible.
- Reproduced and corrected unknown/duplicate JSON keys, malformed CSV handling,
  lost mass-budget notes, and stale sizing charts; added regression tests.
- Added an explicitly assumed compact candidate and sensitivity/target checks.
  Nominal 3 kg estimates 80.5 Wh demand against 88.8 Wh usable; 5 kg estimates
  133.5 Wh with the same battery. This is a conditional screen, not flight evidence.
- Added a documented point-mass hover/forward-transition model using SciPy, plus
  equilibrium, thrust/rate-limit, recovery, and solver-refinement checks.
- Both masses use a shared assumed thrust ceiling, rather than silently upgrading
  available hardware thrust for the heavier case. Ideal wing trim is still a limitation.
- Expanded automated checks to regenerate candidate/study/simulation reports and
  exercise plotting, with numerical tolerance for solver outputs.
- Assistance: review, code, documentation, and generated studies prepared with AI
  assistance. Owner decisions are distinguished from suggested numerical assumptions.
- Next personal work: dimensioned rotor/tilt layout, CG and load calculations,
  component evidence, and a short explanation of the assumptions driving endurance.

See [the prioritised review](repository-review.md) for outstanding additions.

## 2026-10-11 - Wingspan clarification

- Owner clarified that the size guidance applies only to wingspan, not the
  propeller envelope, and that approximately 1 m is flexible rather than a hard cap.
- Updated the brief, requirements, architecture, and study output. Span is reported
  relative to the guide rather than assigned a hard requirement pass/fail.
- Added a regression check that a wing above 1 m is reported without hard rejection.
- Kept the assumed 0.949 m geometry and all performance inputs unchanged; this
  clarification alone does not improve predicted endurance or validate rotor clearance.
- Next design work can compare larger spans while accounting for mass, structure,
  lift/drag, rotor interference, and fabrication. Assistance: AI-assisted updates.

## 2026-10-11 - Recruitment, leadership and engineering review

- Reviewed the published state at `cffea99be6fc6249e7490cc2b40e027253ce91c4`.
  Simulated three role lenses with Airbus/Rolls-Royce/BAE discussion angles;
  no company representatives reviewed or endorsed the project.
- Added a short generated decision brief, evidence map, contribution record
  and small design gates. Personal name/work, observation hover time and
  rotor-layout/CAD/printer inputs were requested, not invented.
- Added fixed-duration hover duty-cycle cases: five minutes total hover estimates
  94.1 Wh for a 30-minute mission, above 88.8 Wh assumed usable.
- Added span comparisons holding area or reference mean chord fixed, with mass
  and coefficients unchanged. These are not structural/aerodynamic optimisations.
- Reproduced false-success simulation comparison with no expected CSV tables.
  Fixed required filenames, missing/extra/empty/malformed tables, finite numerical
  comparison and colliding mass-case filenames; added regression tests.
- AI assistance prepared the review, changes, tests and generated outputs.
  No physical measurements, selected hardware or completed personal CAD were added.

## Entry template

- Date, author, and time period:
- Question or requirement addressed:
- Personal work completed:
- Inputs, configuration, and sources:
- Result and link to evidence:
- Uncertainty, error, or unexpected behaviour:
- What changed and why:
- External assistance or reused work:
- Next step:
