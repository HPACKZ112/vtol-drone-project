# Verification

Run from the repository root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/check_project.py
```

Tests use standard-library `unittest`. Coverage includes equations and units,
mass/rotor-size scaling, physical input limits, malformed/ambiguous JSON/CSV,
retained mass-budget notes, stale plot handling, report generation from another
working directory, hard mass targets versus flexible span guidance, upper-mass energy failure, force
equilibrium, thrust/rate limits, and solver-step refinement.

Most tests run without third-party packages; the numerical solver test is skipped
when SciPy is absent. Install the requirements for full verification. The sizing
CLI can run with `--no-plots` independently of the scientific packages.

The GitHub workflow runs Python 3.11 and 3.12, checks sizing/design-study reports
against committed inputs, compares regenerated simulation CSVs with numerical
tolerance, and smoke-tests chart generation. It does not compare PNG bytes across
operating systems or establish scientific accuracy from a chart's appearance.

These checks verify consistency with documented assumptions. Physical model
validation requires calibrated, repeatable independent data. No aircraft, flight,
or measured endurance validation is claimed.

New checks cover constant-duration hover exchanges, wing-comparison invariants,
baseline reproduction, invalid geometry/duty cycles, and missing/extra/empty/
malformed/nonfinite simulation tables. Reproducibility now requires all case
files named by the simulation input snapshot, not just whichever CSVs remain.

The personal-work review adds checks that equal-load individual rotor powers
sum to the combined-disc result, and that the labelled 3 kg/5 kg numerical
examples match the scalar equations. The owner's images contain no numerical
results; these tests do not establish independently completed hand calculations.

Layout tests cover projected area by independent integration, sampled analytical
disc bounds, hover/cruise poses, force/moment equilibrium, weighted CG and battery
algebra, mass conservation, invalid schemas, trial screens and complete numerical
reports. These are thin-disc/static checks, not aircraft clearance/stability validation.
