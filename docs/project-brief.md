# Project brief

## Purpose and audience

Investigate a compact electric four-tilting-rotor aircraft for search-and-rescue
observation and basic surveillance. This is an educational engineering concept,
not an operational rescue system or a market-ready product. The owner is a
second-year Mechanical Engineering student at the University of Exeter, already
applying for aerospace mechanical-engineering summer placements.

## Confirmed scope

- Design study plus simulated hover and forward transition.
- Four tilting rotors, maximum all-up mass 5 kg.
- Around 1 m wingspan as a flexible guide, not a hard limit; wing only.
- At least 30 minutes total flight time as a design target.
- Approximately GBP 500 parts target, flexible for an achievable student prototype.
- Camera/sensor unselected; basic 3D printer, soldering, and DIY tools available.

These owner-confirmed facts are stored in [project_brief.json](../data/project_brief.json).
No exact costs, selected parts, supervision, workshop access, or hardware results
have been supplied. Budget inclusions remain open. Propellers may extend beyond
the wing; no total-aircraft width limit has been specified. Rotor clearance and
the complete tilt envelope still need to be documented.

## Current deliverables

Readable Python sizing calculations, a candidate mass budget, a target screen,
mass/efficiency sensitivity, and a five-state point-mass dynamics model. Supporting
documents distinguish requirements from assumptions and verification from
physical validation. The candidate 3 kg mass is a study assumption, not an owner
requirement; the 5 kg case tests the upper limit with otherwise unchanged inputs.

The 0.949 m wing is a starting candidate, not an optimised span. A wider wing can
be investigated where a documented aerodynamic, structural, mass, or packaging
trade-off justifies it. The target screen reports span relative to the guide
without marking a larger wing as a failed requirement.

Programming stays close to university material: functions, dictionaries, arrays,
files, and tests. Calculus supplies Newton's differential equations; SciPy solves
them with a documented, established method. There is no need to introduce a complex
software architecture to demonstrate sound engineering reasoning.

## Success criteria

Another student can reproduce outputs, explain units and equations, identify which
assumptions drive the result, and propose measurements that would improve it.
Mechanical evidence should next show geometry, loads, materials, assembly, and
centre of gravity. A simulated smooth transition alone is not a success criterion
for the physical aircraft: attitude/control authority and model validity are still
unresolved.

## Boundaries

No aircraft autopilot, validated transition controller, flight-ready design, rescue
deployment capability, thermal sensor performance, or measured endurance is claimed.
Hardware testing depends on appropriate supervision, risk assessment, facilities,
and applicable operating requirements. Return transition and landing are future
simulation work, not covered by the present forward-transition model.
