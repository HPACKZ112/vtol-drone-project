# Calculation methods and assumptions

These models provide preliminary estimates for design comparisons. Every numeric
input in both the tutorial and compact candidate is assumed. `analysis/calculations.py` contains scalar
equations; `analysis/run_analysis.py` loads inputs, combines them, and writes
reports. Names include units where practical.

## Symbols and inputs

| Symbol | Meaning | Unit | Example input |
| --- | --- | --- | ---: |
| m | All-up mass from component budget | kg | 3.0 |
| g | Gravitational acceleration | m/s^2 | 9.81 |
| rho | Air density | kg/m^3 | 1.225 |
| N | Number of identical rotors | - | 4 |
| d | Rotor diameter | m | 0.305 |
| S | Wing reference area | m^2 | 0.55 |
| AR | Wing aspect ratio | - | 6.0 |
| e | Oswald efficiency factor | - | 0.8 |
| CD0 | Whole-aircraft zero-lift drag coefficient, referenced to S | - | 0.045 |
| CLmax | Maximum lift coefficient | - | 1.2 |
| V | Cruise airspeed | m/s | 18.0 |
| FM | Hover figure of merit: ideal induced power / shaft power | - | 0.65 |
| eta_m | Combined motor and ESC efficiency | - | 0.85 |
| eta_p | Cruise propeller efficiency: thrust power / shaft power | - | 0.70 |
| P_aux | Auxiliary electrical load | W | 10.0 |

The values illustrate the workflow; they are not literature-derived performance
values for a selected aircraft. Keep `CD0` and lift coefficients referenced to
the same wing area. Equal rotor loads and non-overlapping rotor discs are assumed.

## 1. Mass, weight, and thrust target

### Wing geometry screen

From the definition `AR = b^2/S`, span `b = sqrt(AR*S)` and reference mean
chord `c = S/b`. Wing loading is `W/S`. This does not establish planform,
thickness, rotor clearance, stiffness, or aerodynamic validity.

The original tutorial's S=0.55 m^2 and AR=6 imply 1.817 m span; that case does
not meet the owner's later below-1-m requirement. The separate compact candidate
uses S=0.18 m^2 and AR=5, giving 0.949 m span and 0.190 m mean chord.
Values in the symbol table above belong to the tutorial, not the compact case.

```text
m = sum(quantity * unit_mass)
W = m * g
T_hover_per_rotor = W / N
T_peak_target_per_rotor = thrust_to_weight_target * W / N
```

For the example, W = 3.0 * 9.81 = 29.43 N; each rotor needs 7.3575 N in
ideal balanced hover. A thrust-to-weight target of 2 gives a peak target of
14.715 N per rotor. It does not demonstrate that a selected propulsion unit can
produce that thrust, and it does not predict peak electrical power.

## 2. Hover power

```text
A = N * pi * (d / 2)^2
v_i = sqrt(W / (2 * rho * A))
P_ideal = W * v_i
P_hover_electrical = P_ideal / (FM * eta_m) + P_aux
```

In steady hover, ideal actuator-disc momentum theory relates thrust, disc area,
and induced velocity. The electrical estimate then applies assumed aerodynamic
and motor losses. The combined-disc equation requires identical, equally loaded
rotors without significant wake interaction. See
[Johnson, NASA Ames, rotor inflow and ideal hover power, pp. 2-3](https://rotorcraft.arc.nasa.gov/Publications/files/Johnson_AHS-SF2004.pdf).

This estimate omits wing download, rotor interactions, ground effect, changing
efficiency, and airframe attitude. At fixed disc area and efficiencies, propulsion
power scales with mass^(3/2). Auxiliary power is added once for the whole aircraft.

## 3. Wing lift and stall estimate

```text
q = 0.5 * rho * V^2
L = q * S * CL
V_stall = sqrt(2 * W / (rho * S * CLmax))
CL_cruise = W / (q * S)
```

Set L = W for steady level flight, then use the assumed maximum lift coefficient
to estimate stall speed. This rearranges the
[NASA Glenn lift equation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/).
`CLmax` needs evidence for the chosen airfoil, Reynolds number, and configuration.
The script rejects cruise at or below this estimate; it does not select an
operational flight margin or establish transition airspeed.

## 4. Cruise drag and electrical power

```text
CD_induced = CL_cruise^2 / (pi * AR * e)
CD = CD0 + CD_induced
D = q * S * CD
P_cruise_electrical = D * V / (eta_p * eta_m) + P_aux
```

The parabolic drag model follows
[NASA Glenn's induced drag relation](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/induced-drag-coefficient/).
Thrust equals drag in this level-flight model. The thrust power D*V is divided by
propeller and motor efficiencies to estimate electrical input; see
[MIT Unified Engineering, propeller performance](https://ocw.mit.edu/ans7870/16/16.unified/propulsionS04/UnifiedPropulsion7/UnifiedPropulsion7.htm).

The assumed whole-aircraft drag coefficient must eventually include fuselage,
nacelles, mechanisms, and other components. Efficiency varies with operating
point. Rotor tilt, wing interference, climbing, turns, and transient dynamics are
not represented.

## 5. Battery and mission energy

```text
E_nominal_Wh = nominal_voltage_V * capacity_Ah
E_usable_Wh = E_nominal_Wh * usable_fraction
P_transition = (P_hover_electrical - P_aux) * transition_factor + P_aux
E_segment_Wh = P_segment_W * duration_s / 3600
E_mission_Wh = sum(E_segment_Wh)
E_remaining_Wh = E_usable_Wh - E_mission_Wh
```

The transition factor is an explicit budgeting allowance applied to propulsion
power. It is not a model of tilt motion or rotor/wing force sharing. A positive
energy balance says only that the assumed loads fit the assumed usable energy.
The fraction already excludes reserve; remaining usable energy is additional
headroom, not total energy left in the pack. Battery sag, discharge-rate limits,
temperature, ageing, and climb energy are not explicitly modelled.

The compact candidate allocates 60 s hover, 50 s transition, and 1690 s cruise
for 1800 s total. At 3 kg, estimated demand is 80.5 Wh against 88.8 Wh assumed
usable. At 5 kg with the same battery/wing, demand rises to 133.5 Wh. Neither
result demonstrates endurance. Increasing capacity adds mass: a fixed-mass
energy-needed calculation is not a converged battery-sizing solution.

The separate point-mass simulation does not calculate energy and does not replace
the transition-power allowance. See [its derivation](../simulation/README.md).

## Verification and sensitivity

Unit tests use independently evaluable numbers: thrust 8 N, density 1 kg/m^3,
and disc area 1 m^2 give induced velocity 2 m/s and ideal power 16 W. Energy
conversion is checked with 100 W for 36 s = 1 Wh. Further checks cover input
limits, physical trends, and report generation.

`math.fsum` reduces floating-point accumulation error in the mass and energy totals.
Saved numeric outputs are rounded to six decimal places before report formatting;
the displayed digits do not represent measurement accuracy. A regression check
ensures tiny floating-point differences cannot change the displayed thrust target.

The mass sweep varies mass from 70% to 130% of baseline with rotor size fixed.
The speed sweep samples above 1.1 times the estimated stall speed and holds all
other inputs fixed. That lower bound is for plotting only. The model does not
establish a safe speed range or an optimal flight speed.

`python -m analysis.run_design_study` checks confirmed mass/span/duration targets,
compares mass cases, and varies individual assumptions by +/-20%. These are
illustrative perturbations, not measured uncertainty intervals. Component cost
and payload suitability explicitly remain unassessed.

Generated mass snapshots retain evidence notes. Plot-data records identify the
case, curves, and markers behind each sizing image. When `--no-plots` changes
the recorded data, a mismatched chart is removed instead of left beside a new
report. Matching records retain existing charts. After editing plotting/model
code, regenerate plots even if inputs did not change.

## Next measurements

Weigh components and record uncertainty; obtain thrust, current, and voltage data
for candidate propulsion units; justify aerodynamic coefficients; measure battery
usable energy under relevant loads; then compare predictions with repeatable
measurements. Retain both predicted and measured values and discuss residuals.
