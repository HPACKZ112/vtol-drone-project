# Educational hover and forward-transition model

This is a five-state longitudinal **point-mass** model, not a validated aircraft
simulator. It illustrates Newton's equations and rotor/wing force sharing with
ideal attitude and wing trim. It uses SciPy's established
[solve_ivp ODE solver](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)
instead of implementing a numerical integrator from scratch.

## Run and inspect

```bash
python -m pip install -r requirements.txt
python -m simulation.run_simulation
```

Run from the repository root. [Inputs and results](../reports/simulation/summary.md)
include CSV trajectories, summary metrics, controller assumptions, and two plots.
Use `--output-dir work/my-simulation` for separate output or `--no-plots` for
tables only. Matching plots are retained; plots with mismatched input records are
removed to avoid displaying a chart from another case. Regenerate plots after
changing model code even if the inputs are unchanged.

## Equations and conventions

State is `[x, z, vx, vz, theta]`. `x` is forward, `z` upward, and rotor tilt `theta`
is measured forward from vertical. Positions are metres, speeds m/s, and internal
angles radians. With still air and aggregate rotor thrust `T`:

```text
x_dot = vx
z_dot = vz
vx_dot = (T*sin(theta) + F_aero_x) / m
vz_dot = (T*cos(theta) + F_aero_z - m*g) / m
theta_dot = clip((theta_requested - theta)/tau, -rate_limit, rate_limit)
```

Wing trim is chosen for each mass so lift equals weight at the assumed 22 m/s
cruise speed. The model then holds that lift coefficient constant:

```text
CL_trim = m*g / (0.5*rho*V_cruise^2*S)
q = 0.5*rho*max(vx, 0)^2
L = q*S*CL_trim
CD = CD0 + CL_trim^2/(pi*AR*e)
D = q*S*CD
```

Lift acts normal to the velocity vector and drag opposite it. Using forward speed
for dynamic pressure omits vertical-flow aerodynamic effects; hover has zero wing
lift in this approximation. Lift/drag relations follow the
[NASA lift equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/)
and [induced-drag relation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/).
There is no angle-of-attack state, stall model, or wing moment. Ideal trim is a
strong assumption, not a physical control-surface design.

## Illustrative controller

Altitude uses proportional error and vertical-speed damping. Forward acceleration
uses speed error. Required rotor force subtracts modelled aerodynamic force and
adds weight in the vertical direction. Negative requested force components are
clipped to zero: this is forward-flight force handover, not reverse thrust or a
general-purpose flight controller.

The requested force vector sets thrust magnitude and tilt angle. Total thrust is
limited to an **assumed 58.86 N** for both masses, taken from the 3 kg candidate's
2:1 design target. It is not sourced hardware capability. Tilt follows a first-order
response (`tau=0.4 s`) with an assumed 20 deg/s limit. Neither limit includes servo
torque, motor dynamics, supply voltage, or thermal effects.

Hover begins 0.25 m below a 10 m reference to demonstrate disturbance recovery.
Forward transition holds hover for 5 s, then ramps the speed command to 22 m/s over
25 s using `3*p^2 - 2*p^3`. Both numbers are study inputs, not flight-test commands.
RK45 uses `rtol=1e-7`, `atol=1e-9`, `max_step=0.05 s`; output is sampled at 10 Hz.
Saved CSV values are rounded to six decimal places, not measurement precision.

## Verification versus validation

Tests check hover equilibrium, trimmed cruise equilibrium, thrust/tilt-rate limits,
command endpoints, hover recovery, and solver-step refinement. Automated report
comparison uses `1e-5` relative/absolute tolerance across Python/platforms. These
checks verify implementation consistency, not aerodynamic or aircraft accuracy.

The upper-mass case retrims CL and scales requested forces with mass, so similar
responses are expected while thrust margin differs. It still fails the separate
30-minute energy screen. **Power/endurance is not computed here**; sizing uses
steady power models and an assumed transition-energy allowance.

## Required extensions

Add geometry, inertia, pitch dynamics, rotor locations/allocation, wing coefficients
versus angle of attack, pitching moments, and actuator torque constraints. Then
investigate disturbed hover, transition control authority, wind, return transition,
landing, and failure cases. Validate against independent evidence before claiming
stable aircraft transition. No present result establishes flight readiness.
