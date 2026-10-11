# Provisional swept-clearance and weight-distribution study

Prepared with AI assistance on 2026-10-11 following the owner's request. The
[original sketch](personal-work.md) is unscaled. Rear rotors on the horizontal
tail and all four tilting forward are owner choices; **no trial dimensions below
are owner-selected or a build specification**.

Read the [generated comparison and diagrams](../reports/layout-study/summary.md)
alongside this method. Plain Python functions implement geometry and equilibrium;
Matplotlib makes diagrams. No CAD model or component has been selected.

## Assumed geometry and datums

`x=0` is main-wing leading edge, x positive aft; y lateral; z positive up. Wing
plane is `z=0`. The rectangular drawing retains the assumed 0.18 m^2, AR=5
reference: 0.949 m span and 0.190 m chord. It is not a designed wing/airfoil.
The comparison CG datum is 25% chord, x=47.4 mm. **This is not a verified stable
CG, trim solution, allowable CG band or recommendation for flight.**

Common choices: 305 mm diameter, 40 mm disc-centre offset along the rotor axis
from a lateral hinge, hinges 60 mm above wing/tail planes, 0-90 degree forward
tilt, 20 mm surface thickness. Rear hinges are 80 mm ahead of the tail leading
edge on not-yet-designed supports attached to the tail. Body/boom are reserved
envelopes, not physical parts.

| Trial | Front hinge x (mm) | Rear hinge x (mm) | Front spacing (mm) | Rear spacing (mm) | Tail span (mm) | Purpose |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A Narrow tail | -80 | 380 | 600 | 300 | 360 | Show the risk of copying an undimensioned narrow rear surface |
| B Widened compact | -80 | 380 | 600 | 400 | 480 | Correct rear spacing with short front supports |
| C Longer front supports | -300 | 400 | 700 | 500 | Put hover thrust midpoint near the wing comparison CG datum |
| D Long tail | -100 | 650 | 740 | 600 | 700 | Explore separation at the cost of aft mass moment |

Full assumptions: [provisional_layouts.json](../data/provisional_layouts.json).
Revise for actual hinges, components, structure and rotor size.

## Disc area versus tilt envelope

Each aerodynamic disc is `pi*R^2`, 0.07306 m^2 here; four sum to 0.29225 m^2
regardless of layout. Packaging projection is not extra actuator-disc area.

For axial hinge offset l, forward tilt theta, and disc coordinates u,v:

```text
u^2 + v^2 <= R^2
x_relative = -l*sin(theta) + u*cos(theta)
y_relative = v
z_relative =  l*cos(theta) + u*sin(theta)
0 <= theta <= pi/2
K = sqrt(R^2 + l^2)
```

The continuous envelope fits inside a sphere of radius K about the hinge.
Bounds: x from `-K` to `R`, y from `-R` to `R`, z from `-R` to `K`.
Boxes/spheres contain empty space; neither is the exact swept solid. Here the
extents are 157.7 mm forward, 152.5 mm aft, 152.5 mm each side, 152.5 mm below
and 157.7 mm above the hinge, before allowances.

At fixed y the top-view union runs from `-sqrt(R^2+l^2-y^2)` to
`sqrt(R^2-y^2)`. Integrating the width gives:

```text
A_plan_sweep = pi*R^2/2 + R*l + (R^2+l^2)*asin(R/sqrt(R^2+l^2))
```

This gives 0.07530 m^2 per rotor. With zero offset it reduces to `pi*R^2`,
although the 3D envelope still changes. It covers only an axial offset and
lateral hinge, not an arbitrary linkage.

### Clearance screen

**20 mm is an illustrative planning gap, not a validated safe minimum.** Blade
flex/thickness, balance, manufacture, compliance and control error need evidence.

- Same-row hubs need `d+gap=325 mm` here. A's 300 mm rear spacing gives 5 mm
  actual hover-disc overlap; do not rely on blade timing to accommodate overlap.
- The 25 mm boom's conservative lateral corridor needs
  `d+boom_width+2*gap=370 mm` spacing. B's 400 mm gives 35 mm disc-to-boom
  lateral clearance, stricter than rotor-to-rotor spacing.
- Cross-row hinge distance minus `2*K` is a conservative separation bound,
  including independent tilt. A failed sphere bound needs further analysis;
  it does not prove collision.
- A hinge ahead of its surface LE has u >= 0 for any disc point reaching the
  surface, so z >= hinge height throughout the studied forward tilt. This
  gives at least 50 mm above the 20 mm slab. The proof depends on these datums
  and hinge assumptions.
- Fuselage uses a front lateral corridor and rear hinge-sphere versus box bound.
  Only the specified body/boom envelopes are covered.
- Longitudinal projection gaps also separate the rear discs from the main wing
  and front discs from the tail, beyond the respective leading-edge proof.
- Disc-only full tilt requires wing-plane height >=112.5 mm for 20 mm flat-ground
  tip allowance. This is not landing-gear sizing; attitude, terrain and gear
  deflection are omitted.

Motor bodies, support members, servo/linkage, wiring, blade thickness and moving
rear control surfaces are **not** cleared. A disc-screen result is not assembly,
aerodynamic or structural clearance.

## Mass positions and hover thrust

```text
x_CG = sum(m_i*x_i) / sum(m_i)
x_battery = (m_total*x_CG_reference - sum(other_m_i*other_x_i)) / m_battery
```

This uses the mass-weighted relation explained by
[NASA Glenn](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/center-of-gravity/).
Keep the assumed 3 kg budget; split 0.9 kg airframe into 0.6 kg main structure
at x=60 mm and 0.3 kg tail/boom at `0.55*x_rear`. Motor/prop/tilt masses split
equally between rows; electronics are central; 0.15 kg unselected sensor is at
x=-20 mm. Battery mass is 0.7 kg. These are assumed, not measured mass centres.

Battery-centre travel is assumed -180 to +160 mm. Pack dimensions, restraint,
access and bay fit are unverified. The [mass-position CSV](../reports/layout-study/mass_positions.csv)
includes the algebraic trial even where D's battery is outside travel.

A/B share longitudinal mass stations, so their CG/thrust-share curves coincide.
Widening A's tail is given no structural mass penalty in this initial comparison.

For vertical hover with symmetric pairs and no other moments:

```text
F_front + F_rear = W
F_front*(x_CG-x_front) = F_rear*(x_rear-x_CG)
F_front/W = (x_rear-x_CG)/(x_rear-x_front)
T_front_each = F_front/2
T_rear_each = F_rear/2
```

Percentages describe **thrust sharing**, not where that percentage of component
mass must go. Equal loading needs CG at the thrust-row midpoint; that is not
automatically an acceptable cruise CG.

At the reference B needs battery centre 154.4 mm ahead of wing LE and roughly
72.3/27.7 thrust sharing: 10.64 N each front, 4.08 N each rear. C needs 60.6 mm
ahead and is nearly equal-load. D needs 341.3 mm ahead, outside assumed travel.

B has just 25.6 mm adjustment left forward. A hypothetical additional 0.1 kg
at its rear hinge would require battery centre 201.9 mm ahead, beyond that travel.
Weigh tail/propulsion parts and revise stations before fixing geometry.

Keep pairs symmetric and heavy central items on the centreline. A movable,
restrained battery helps adjustment but does not replace measured CG. Lateral
and vertical CG, inertia and moving mass centres through tilt remain unmodelled.
Longitudinal hover balance does not establish transition control.

### Power and mechanical trade-off

Sum `T_i*sqrt(T_i/(2*rho*A_i))` over separate discs, apply the same assumed
figure of merit/motor efficiency and add auxiliary power once. The isolated-disc
hover relation follows [NASA Ames, Johnson, pp. 2-3](https://rotorcraft.arc.nasa.gov/Publications/files/Johnson_AHS-SF2004.pdf).
B estimates 377.3 W, 25.8 W above equal-load 351.5 W. Download, interactions
and operating-point changes are omitted. A's power is only diagnostic because
overlapping rotors violate that model.

C reduces imbalance but its rotor-thrust-only front support moment is 2.22 N*m
per side versus B's 0.85 N*m; tail/boom indicators also rise. These `force*distance`
values are not allowable stresses or servo torque. Add weight, rotor torque,
aero and dynamic loads plus actual support geometry.

## Recommendation and next inputs

**Develop B as the first compact mechanical study; retain C as the comparison.**
This is conditional judgement, not optimal/flight-ready selection. B improves
rear spacing and keeps short front supports but needs forward battery space and
higher front loading. C trades lower isolated hover power for longer front
supports and greater tail/boom moment indicators. Structural mass and drag may
change the choice. Do not build A as drawn or adopt D without revising mass positions.

Choose a trial to dimension, confirm battery-centre travel and fuselage size,
then develop one tilt hinge/load path using actual component dimensions. Check
cruise trim/stability, 3D component clearance, structure and control authority
before any hardware/readiness claim.

Run `python -m analysis.run_layout_study`; `--no-plots` uses standard Python.
Reports retain inputs, mass stations, clearance metrics, battery sweeps and chart
records. Tests check integration, analytical bounds, force/moment balance,
mass conservation and invalid inputs, not aircraft adequacy. SAR sizing inputs
and the transition simulator are unchanged.
