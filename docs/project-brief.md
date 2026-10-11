# Project brief

## Problem

A VTOL aircraft must support its weight using rotors during hover, then use its
wing during cruise. Tilting rotors or a tilting wing introduce extra mechanical
and control requirements. This project asks how a student can turn that problem
into a traceable preliminary design and testable engineering work.

## Objective

Develop a documented concept for a small electric tilt-rotor or tilt-wing aircraft.
Begin with reproducible sizing calculations, then replace assumptions with
component evidence and validate the design in stages.

## Current deliverables

- A provisional mission and requirements with verification methods.
- A mass budget and Python estimates of hover thrust/power, stall speed, cruise
  drag/power, and mission energy.
- Sensitivity plots and a written explanation of model limitations.
- A decision log, BOM template, and staged validation plan.

## Future deliverables

An architecture trade study, CAD and drawings, centre-of-gravity calculation,
structural checks, propulsion measurements, and a validated dynamics model.
Hardware or flight results should be added only after they exist and are reviewed.

## Scope boundary

The current code performs preliminary scalar calculations. It does not implement
an autopilot, attitude controller, tilt controller, or flight simulator. The
transition power allowance is an energy estimate; it cannot establish transition
stability. A future controller must have its own model, review, and validation.

## Success criteria for this phase

Another student can run the same inputs and obtain the same numerical outputs,
trace each equation to a source or derivation, identify the largest uncertainties,
and explain which measurements would improve the design.

## Items to confirm

Mission duration and payload; project budget and schedule; university supervision
and facilities; available fabrication tools; operating location; selected VTOL
layout; and the contribution of each team member.
