# Verification and staged test plan

Every stage below is **planned**. Define acceptance criteria for the selected
design and have the actual procedures reviewed before testing. Advance only after
the preceding evidence has been reviewed and unresolved faults addressed.

| Stage | Purpose | Evidence and gate |
| --- | --- | --- |
| 0. Analytical review | Check mission, mass, thrust, power, and energy assumptions | Reviewed requirements, equation checks, and sourced component data |
| 1. Mechanical/electrical inspection | Check structure, tilt mechanism, wiring, and limits | Drawings, inspection record, and reviewed failure response |
| 2. Propeller-off configuration | Check sensors, commands, logging, arming, and tilt travel | Versioned configuration and ground checks |
| 3. Controlled propulsion measurement | Measure thrust, voltage, current, and temperature on an appropriate stand | Reviewed procedure, calibration, repeat data, and limits |
| 4. Dynamics simulation | Investigate hover, transition, control authority, and failures | Documented model, scenarios, and acceptance criteria |
| 5. Reviewed initial flight test | Verify limited objectives with approved supervision and site | Readiness review and specific flight procedure |
| 6. Envelope expansion | Extend objectives incrementally | Reviewed logs and updated limits after each test |

Restraining a complete aircraft can change its dynamics; any restraint or tether
arrangement needs its own engineering review. The sizing script cannot validate
this arrangement, a transition controller, or a flight-test envelope.

## Test record template

- Test ID, date, author, supervisor, and objective:
- Requirement IDs and acceptance criteria:
- Hardware configuration, mass, centre of gravity, and battery condition:
- Firmware version and parameter file:
- Instruments, calibration, sampling, and environment:
- Procedure, exclusion area, abort criteria, and emergency response:
- Raw data and processed results:
- Uncertainty, unexpected events, and deviations:
- Pass/fail with evidence and reviewer:
- Corrective actions and next authorised stage:

No hardware or flight test has been recorded in this repository yet.
