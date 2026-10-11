# Educational hover and forward-transition simulation

This five-state longitudinal point-mass model illustrates force sharing
between tilted rotor thrust and wing lift. Attitude control and a constant
trimmed lift coefficient are ideal assumptions. It does not simulate
pitch/roll/yaw dynamics, moments, rotor allocation, structural loads,
return transition, or landing. These are not validated aircraft results.

The hover case starts 0.25 m below the reference altitude. The transition
case ramps the speed command from zero to 22 m/s over 25 seconds after
5 seconds of hover. Height is an illustrative airborne reference, not a
proposed flight-test instruction. Inputs and controller gains are assumed.

| Case | Mass (kg) | Final speed (m/s) | Maximum height error (m) | Final wing support fraction |
| --- | ---: | ---: | ---: | ---: |
| hover | 3.0 | 0.000 | 0.250 | 0.000 |
| transition | 3.0 | 22.000 | 0.128 | 1.000 |
| hover | 5.0 | 0.000 | 0.250 | 0.000 |
| transition | 5.0 | 22.000 | 0.126 | 1.000 |

Hover.png and transition.png show the nominal and upper-mass runs when generated.
Both use the same assumed 58.86 N total thrust ceiling, corresponding to
the 3 kg candidate's 2:1 thrust target. This is not a measured hardware limit.
The upper-mass run has a lower thrust-to-weight margin. Ideal wing trim and
mass-scaled control forces also explain the similar response curves.
The successful force handover depends on the assumed perfect attitude
and trim control. The 5 kg simulation does not override the failed 30-minute
energy screen for that mass. Simulation power/endurance is not calculated:
the separate sizing study uses steady power models and a transition allowance.

Next: add aircraft geometry, moments/inertia, actuator torque limits,
aerodynamic coefficients versus angle of attack, and attitude dynamics
before treating this as a transition-control validation model.
