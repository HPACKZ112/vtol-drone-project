# Architecture and alternatives

The design direction is **tilt-rotor or tilt-wing**. The worked example assumes
four identical rotors that carry equal load in hover and provide propulsion in
cruise. It does not select rotor placement, tilt linkage, control surfaces, or
transition scheduling. The same aggregate cruise model can support an early
tilt-wing study, but interference and control differences need separate analysis.

## Comparison to complete

| Layout | Potential advantages to investigate | Questions and costs to investigate |
| --- | --- | --- |
| Tilt-rotor | Wing stays fixed; propulsion direction can vary | Tilt mechanism mass, loads, synchronisation, rotor/wing interference |
| Tilt-wing | Wing and propulsion can rotate together | Wing hinge loads, actuator torque, crosswind response, changing aerodynamics |
| Lift-plus-cruise reference | Separate hover and cruise propulsion | Additional motors and cruise drag; useful comparison case |
| Tailsitter reference | May avoid a dedicated tilt mechanism | Landing geometry, attitude transition, and wind sensitivity |

Select criteria before scoring: mass, fabrication difficulty, actuator loading,
transition controllability, maintainability, test facilities, and budget. Record
weights and evidence for scores; leave unsupported scores blank.

## Subsystems

| Subsystem | Interfaces and evidence needed |
| --- | --- |
| Airframe and wing | Geometry, mass, centre of gravity, structural loads, aerodynamic coefficients |
| Propulsion | Rotor diameter, thrust/current curves, voltage, thermal limits, clearance |
| Tilt mechanism | Geometry, torque, rate, position feedback, limits, failure response |
| Power | Battery, distribution, current sensing, protection, connector ratings |
| Flight controller | Sensors, timing, actuator outputs, logging, arming, failsafe behaviour |
| Ground system | Telemetry, operator commands, configuration records, log storage |

```text
Pilot / ground station -> flight controller -> ESCs -> motors
                               |             -> tilt actuators
Sensors -----------------------|             -> control surfaces
                               v
                          recorded logs -> Python analysis
```

The Python code in this repository is offline analysis. Future autopilot
configuration belongs in `firmware/`; dynamics and transition validation belong
in `simulation/`. Configuration files must be tied to a tested hardware version.
