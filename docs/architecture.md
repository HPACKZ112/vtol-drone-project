# Architecture and interfaces

The owner has selected **four tilting rotors with a fixed wing**. The model assumes
four identical rotors with equal hover loading and combines their thrust into one
longitudinal force. It does not select exact placement, linkage, actuator count,
control surfaces, rotor direction, or thrust allocation.

## Candidate and unresolved geometry

The preliminary candidate has 0.18 m^2 wing area, aspect ratio 5, and four assumed
0.305 m rotor diameters. The resulting 0.949 m wing span is not proof that four
rotor discs, their rotating tilt envelopes, wing, and ground clearance fit. A
dimensioned layout must show disc separation, rotor/wing interference, landing
clearance, tilt travel, and access for assembly. Keep the wing-span constraint
distinct from total vehicle width until the owner defines the latter.

## Architecture trade-offs to document

| Layout | Potential advantage | Main question |
| --- | --- | --- |
| Selected four-rotor tilt-rotor | Fixed wing; variable thrust direction | Tilt mechanism loads, synchronisation, interference, control authority |
| Tilt-wing comparison | Wing and propulsion rotate together | Wing hinge loads, actuator sizing, changing aerodynamics |
| Lift-plus-cruise reference | Separate lift and cruise systems | Extra propulsion mass and cruise drag |

Selection is an owner decision, not the outcome of a completed scored study. A
short comparison can explain that decision for interviews; unsupported numerical
scores should remain blank. Prioritise the selected concept's feasibility.

## Subsystem evidence

| Subsystem | Interfaces and evidence needed |
| --- | --- |
| Wing / airframe | Geometry, mass, CG, bending/attachment loads, materials, aerodynamic coefficients |
| Propulsion | Thrust/current versus operating point, voltage, heat, rotor clearance |
| Tilt mechanism | Free-body diagram, hinge moment, servo/linkage torque, rate, backlash, stops |
| Power | Battery energy/discharge, distribution, connectors, total current, monitoring |
| Flight control | Sensor/actuator interfaces, moments/inertia, allocation, logging, failsafes |
| Observation payload | Task, mass, power, mounting, vibration, privacy and data handling |

```text
Pilot / ground station -> flight controller -> ESCs -> motors
                               |             -> tilt actuators
Sensors -----------------------|             -> control surfaces
                               v
                          recorded logs -> Python analysis
```

The current Python work is offline sizing and an educational dynamics model.
Future autopilot configuration belongs in `firmware/` and must be tied to a
reviewed hardware version. A controlled aggregate force in the model does not
establish that real actuator geometry can produce the required forces and moments.
