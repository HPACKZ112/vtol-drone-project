# Data

`example_design.json` and `example_mass_budget.csv` are invented inputs for learning
and checking the workflow. They describe a provisional four-rotor tilt-rotor study,
not selected hardware. The mass budget includes battery, payload, and contingency.

Use SI units in calculations. Battery capacity is in Ah and energy is in Wh;
mission durations are in seconds. Values ending in `_fraction` lie in (0, 1].
`hover_time_s` combines the intended take-off and landing hover time;
`transition_time_s` combines both transitions.

When adding measurements, retain the raw data and record:

- Instrument, calibration, resolution, and uncertainty.
- Date, component identifiers, configuration, and environmental conditions.
- Column names and units, sampling interval, and any processing steps.
- Repeated readings and the reason for excluding any samples.

Keep private raw logs in `data/raw/private/`. Publish a reviewed, anonymised copy
when it is suitable to share. Do not label example values as measured.
