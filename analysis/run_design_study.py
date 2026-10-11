"""Check the compact concept against confirmed targets and inspect sensitivity."""

import argparse
import json
import math
from pathlib import Path

from analysis.run_analysis import (ROOT, calculate_case, load_config,
                                   load_mass_budget, remove_stale_plot, write_csv)
from analysis import calculations as calc


def target_checks(config, mass_kg, brief):
    summary, _ = calculate_case(config, mass_kg)
    return {
        "mass_within_limit": mass_kg <= brief["maximum_mass_kg"],
        "wingspan_m": summary["wingspan_m"],
        "wingspan_guide_m": brief["wingspan_guide_m"],
        "wingspan_difference_from_guide_m": summary["wingspan_m"] - brief["wingspan_guide_m"],
        "wingspan_is_hard_limit": brief["wingspan_is_hard_limit"],
        "duration_meets_target": summary["mission_duration_s"] >= brief["minimum_flight_time_s"],
        "energy_within_assumed_budget": summary["mission_energy_within_budget"],
        "cost_status": "Not assessed: no sourced component selections",
        "payload_status": "Not assessed: camera/sensor is unselected",
    }


def hover_time_cases(config, mass_kg, total_time_s, hover_times_s):
    """Exchange cruise for hover while keeping total mission duration fixed."""
    calc.positive("total_time_s", total_time_s)
    rows = []
    for hover_time_s in hover_times_s:
        calc.non_negative("hover_time_s", hover_time_s)
        cruise_time_s = total_time_s - config["transition_time_s"] - hover_time_s
        calc.non_negative("cruise_time_s", cruise_time_s)
        varied = config.copy()
        varied["hover_time_s"] = hover_time_s
        varied["cruise_time_s"] = cruise_time_s
        result, _ = calculate_case(varied, mass_kg)
        rows.append({
            "total_hover_time_s": hover_time_s,
            "transition_time_s": config["transition_time_s"],
            "cruise_time_s": cruise_time_s,
            "total_mission_time_s": result["mission_duration_s"],
            "mission_energy_wh": result["mission_energy_wh"],
            "remaining_usable_energy_wh": result["remaining_usable_energy_wh"],
            "energy_within_assumed_budget": result["mission_energy_within_budget"],
        })
    return rows


def wing_span_cases(config, mass_kg, spans_m):
    """Compare fixed-area and fixed-mean-chord wings at unchanged assumed mass."""
    mean_chord_m = math.sqrt(config["wing_area_m2"] / config["aspect_ratio"])
    rows = []
    for mode in ("fixed_area", "fixed_mean_chord"):
        for span_m in spans_m:
            calc.positive("span_m", span_m)
            varied = config.copy()
            if mode == "fixed_mean_chord":
                varied["wing_area_m2"] = span_m * mean_chord_m
            varied["aspect_ratio"] = span_m ** 2 / varied["wing_area_m2"]
            result, _ = calculate_case(varied, mass_kg)
            rows.append({
                "comparison": mode, "wingspan_m": span_m,
                "wing_area_m2": varied["wing_area_m2"],
                "aspect_ratio": varied["aspect_ratio"],
                "mean_chord_m": result["mean_chord_m"],
                "stall_speed_m_s": result["stall_speed_m_s"],
                "cruise_power_w": result["electrical_cruise_power_w"],
                "mission_energy_wh": result["mission_energy_wh"],
                "remaining_usable_energy_wh": result["remaining_usable_energy_wh"],
            })
    return rows


def tradeoff_plot_data(mass_kg, baseline, hover_rows, wing_rows):
    record = {
        "mass_kg": round(mass_kg, 6),
        "usable_energy_wh": round(baseline["usable_battery_energy_wh"], 6),
    }
    for name, rows in (("hover_time_cases", hover_rows), ("wing_span_cases", wing_rows)):
        record[name] = [
            {key: round(value, 6) if isinstance(value, float) else value
             for key, value in row.items()} for row in rows
        ]
    return record


def make_tradeoff_plot(output, data):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    fig.suptitle(f"Assumed trade-offs | {data['mass_kg']:.1f} kg, fixed mass and battery",
                 fontsize=14)
    hover = data["hover_time_cases"]
    axes[0].plot([row["total_hover_time_s"] / 60 for row in hover],
                 [row["mission_energy_wh"] for row in hover],
                 marker="o", color="#087e8b")
    duration = hover[0]["total_mission_time_s"] / 60
    axes[0].set(title=f"Hover versus cruise in {duration:.0f}-minute mission",
                xlabel="Total hover time (min)", ylabel="Mission energy (Wh)")
    for mode, label, color in (
            ("fixed_area", "Fixed area", "#087e8b"),
            ("fixed_mean_chord", "Fixed mean chord", "#bd3e36")):
        rows = [row for row in data["wing_span_cases"] if row["comparison"] == mode]
        axes[1].plot([row["wingspan_m"] for row in rows],
                     [row["mission_energy_wh"] for row in rows],
                     marker="o", label=label, color=color)
    axes[1].set(title="Flexible span comparison", xlabel="Wing span (m)",
                ylabel="Mission energy (Wh)")
    for axis in axes:
        axis.axhline(data["usable_energy_wh"], linestyle="--", color="#555555",
                     label="Assumed usable battery")
        axis.grid(alpha=0.2)
        axis.legend(frameon=False, fontsize=9)
        axis.spines[["top", "right"]].set_visible(False)
    fig.savefig(output / "decision_tradeoffs.png", dpi=150)
    plt.close(fig)
    (output / "tradeoff_plot_data.json").write_text(
        json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/design-study")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    config = load_config(ROOT / "data/sar_design.json")
    masses = load_mass_budget(ROOT / "data/sar_mass_budget.csv")
    mass_kg = math.fsum(row["total_mass_kg"] for row in masses)
    brief = json.loads((ROOT / "data/project_brief.json").read_text(encoding="utf-8"))
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    baseline, _ = calculate_case(config, mass_kg)
    hover_times = sorted(set([config["hover_time_s"], 60.0, 180.0, 300.0, 600.0]))
    hover_rows = hover_time_cases(config, mass_kg, brief["minimum_flight_time_s"], hover_times)
    spans = [baseline["wingspan_m"], 1.1, 1.25, 1.4]
    wing_rows = wing_span_cases(config, mass_kg, spans)
    plot_record = tradeoff_plot_data(mass_kg, baseline, hover_rows, wing_rows)
    removed_plot = remove_stale_plot(output, plot_record,
                                    ("decision_tradeoffs.png",), "tradeoff_plot_data.json")
    write_csv(output / "hover_time_cases.csv", hover_rows)
    write_csv(output / "wing_span_cases.csv", wing_rows)
    (output / "inputs.json").write_text(json.dumps({
        "design": config, "mass_budget": masses, "project_brief": brief,
        "hover_times_s": hover_times, "comparison_spans_m": spans,
        "comparison_assumptions": "Fixed mass, battery, coefficients and efficiencies; no structural resizing",
    }, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    rows = []
    for study_mass in (2.5, mass_kg, brief["maximum_mass_kg"]):
        result, _ = calculate_case(config, study_mass)
        rows.append({
            "study_mass_kg": study_mass,
            "stall_speed_m_s": result["stall_speed_m_s"],
            "cruise_to_stall_ratio": result["cruise_to_stall_speed_ratio"],
            "hover_power_w": result["electrical_hover_power_w"],
            "mission_energy_wh": result["mission_energy_wh"],
            "usable_energy_wh": result["usable_battery_energy_wh"],
            "remaining_usable_energy_wh": result["remaining_usable_energy_wh"],
            "nominal_energy_needed_wh": result["mission_energy_wh"] / config["usable_battery_fraction"],
            "energy_within_budget": result["mission_energy_within_budget"],
        })
    write_csv(output / "mass_cases.csv", rows)

    sensitivity = []
    for parameter in ("mass_kg", "zero_lift_drag_coefficient", "hover_figure_of_merit",
                      "cruise_propeller_efficiency", "auxiliary_power_w"):
        for factor in (0.8, 1.2):
            varied = config.copy()
            study_mass = mass_kg
            if parameter == "mass_kg":
                study_mass *= factor
            else:
                varied[parameter] *= factor
            result, _ = calculate_case(varied, study_mass)
            sensitivity.append({
                "parameter": parameter, "factor": factor,
                "mission_energy_wh": result["mission_energy_wh"],
                "change_from_baseline_wh": result["mission_energy_wh"] - baseline["mission_energy_wh"],
            })
    write_csv(output / "sensitivity.csv", sensitivity)
    checks = target_checks(config, mass_kg, brief)
    (output / "target_checks.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Compact tilt-rotor design study", "",
        "Confirmed targets: four tilting rotors; mass at most 5 kg; at least",
        "30 minutes total flight time. Around 1 m wingspan is a flexible guide,",
        "not a hard limit, and applies to the wing only, not the rotor envelope.",
        "The GBP 500 parts budget is a flexible student-project target.",
        "The observation payload is unselected.", "",
        "All numerical design inputs and component masses remain assumptions.",
        "These results screen a concept; they do not demonstrate aircraft performance.", "",
        f"The candidate geometry implies a **{baseline['wingspan_m']:.3f} m span** and",
        f"a **{baseline['mean_chord_m']:.3f} m mean chord**. Area is 0.18 m^2 and AR is 5.",
        "This is a geometry candidate, not a completed CAD design. A larger span",
        "may be considered through a documented mass, lift/drag, structure, and",
        "packaging trade-off; exceeding the guide is not a requirement failure.", "",
        "## Mass cases", "",
        "The 5 kg row is an upper-mass stress case, not the intended all-up mass.",
        "Battery energy, wing, rotor size, and all other inputs stay fixed.", "",
        "| Mass (kg) | Stall estimate (m/s) | Cruise/stall ratio | Hover power (W) | Mission energy (Wh) | Remaining usable energy (Wh) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(f"| {row['study_mass_kg']:.1f} | {row['stall_speed_m_s']:.2f} | "
                     f"{row['cruise_to_stall_ratio']:.2f} | {row['hover_power_w']:.1f} | "
                     f"{row['mission_energy_wh']:.1f} | {row['remaining_usable_energy_wh']:.1f} |")
    lines.extend([
        "", "## Interpretation", "",
        "A lighter concept can fit the assumed energy budget while the upper-mass",
        "case consumes more energy and has less cruise-to-stall margin. A maximum",
        "mass requirement should therefore not be treated as a mass to design towards.",
        "A larger battery adds mass; the energy-needed column in mass_cases.csv is",
        "a fixed-mass estimate, not a completed battery sizing solution.", "",
        "Sensitivity.csv varies one input at a time by +/-20%. These perturbations",
        "are illustrative comparisons, not measured uncertainty intervals or",
        "probability distributions. They identify assumptions worth investigating.", "",
        "For the nominal case, 20% higher CD0 raises demand to 88.8 Wh, just over",
        "the 88.8 Wh usable allowance (88.819 Wh in sensitivity.csv).",
        "20% lower cruise propeller efficiency raises demand to 96.5 Wh.",
        "A positive nominal screen is therefore not a robust endurance conclusion.", "",
        "## Observation hover versus cruise", "",
        "These cases exchange cruise time for total hover time within a fixed",
        "30-minute mission, retaining the transition allowance. Total hover includes",
        "take-off/landing time, not just time available for observation.", "",
        "| Total hover (min) | Cruise (min) | Mission energy (Wh) | Usable-energy headroom (Wh) |",
        "| ---: | ---: | ---: | ---: |",
    ])
    for row in hover_rows:
        lines.append(f"| {row['total_hover_time_s'] / 60:.1f} | "
                     f"{row['cruise_time_s'] / 60:.1f} | {row['mission_energy_wh']:.1f} | "
                     f"{row['remaining_usable_energy_wh']:.1f} |")
    lines.extend([
        "", "This is a mission trade-off, not a demonstrated hover capability.",
        "The observation task needs owner input before selecting the mission profile.", "",
        "## Flexible wingspan comparison", "",
        "wing_span_cases.csv compares the starting span with 1.10, 1.25, and 1.40 m.",
        "One sweep holds area fixed; the other holds reference mean chord fixed.",
        "The former changes aspect ratio without changing the stall estimate; the",
        "latter changes area, stall estimate, and both induced and zero-lift drag.",
        "All hold mass and coefficients fixed: heavier structure, stiffness,",
        "rotor interference, Reynolds-number effects, and manufacturing are omitted.",
        "Do not select a wing solely by the lowest estimated energy.", "",
        "## Outstanding feasibility checks", "",
        "- Source motor/propeller thrust and current curves and battery discharge data.",
        "- Justify drag, lift, and efficiency inputs for the selected configuration.",
        "- Lay out all four rotor discs and tilt envelopes with verified clearance.",
        "- Design the tilt mechanism, wing structure, attachments, and centre of gravity.",
        "- Check attitude/control authority and transition/landing behaviour.",
        "- Select the observation payload and price a complete component BOM.",
        "", "## Target screen", "",
    ])
    for key, value in checks.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    five_minute_hover = next(row for row in hover_rows if row["total_hover_time_s"] == 300)
    brief_lines = [
        "# Design decision brief", "",
        "## Purpose and present decision", "",
        "Second-year Mechanical Engineering design study: investigate four tilting",
        "rotors for a compact observation concept. Continue analytical/mechanical",
        "design, not hardware purchases or operational search-and-rescue deployment.",
        "Around 1 m is flexible wing-only guidance; maximum mass is 5 kg.",
        "The camera/sensor and complete parts cost are unselected.", "",
        "## Assumption-based result", "",
        f"At {mass_kg:.1f} kg, the candidate span is {baseline['wingspan_m']:.3f} m.",
        f"The assumed {baseline['mission_duration_s'] / 60:.0f}-minute mission needs",
        f"{baseline['mission_energy_wh']:.1f} Wh against",
        f"{baseline['usable_battery_energy_wh']:.1f} Wh usable energy.",
        f"Only {baseline['remaining_usable_energy_wh']:.1f} Wh headroom remains.",
        "This is not demonstrated endurance; drag, efficiencies, component masses,",
        "battery usability, and observation payload remain assumptions.", "",
        "## Decision-relevant trade-offs", "",
        f"Exchanging cruise for five minutes of total hover in a 30-minute mission",
        f"raises demand to {five_minute_hover['mission_energy_wh']:.1f} Wh, with",
        f"{five_minute_hover['remaining_usable_energy_wh']:.1f} Wh usable-energy headroom.",
        "Total hover includes take-off/landing, not just observation.",
        "Larger spans reduce induced drag at fixed area in this model; increasing",
        "area at fixed mean chord also increases assumed zero-lift drag. Neither",
        "comparison includes extra structure mass or altered aerodynamic coefficients.", "",
        "## What remains unproven", "",
        "Rotor packaging/tilt clearance, CG, wing/root loads, mechanism torque,",
        "current/thermal capability, aerodynamic data, cost, and sensor suitability.",
        "The point-mass simulation assumes ideal attitude and trim, omits moments,",
        "and cannot validate real transition stability or calculate endurance.", "",
        "## Next evidence", "",
        "Confirm the observation/hover task; sketch rotor placement; calculate CG",
        "and mechanism loads; connect a component shortlist to measured/sourced data.",
        "Record the student's personal work and assistance without inventing results.", "",
        "## Reproduce and inspect", "",
        "[Full study](summary.md), [input snapshot](inputs.json),",
        "[hover cases](hover_time_cases.csv), [wing cases](wing_span_cases.csv),",
        "[assumption-based sizing](../sar/summary.md), and",
        "[simulation boundaries](../../simulation/README.md).", "",
        "Generated by `python -m analysis.run_design_study`; verification checks",
        "implementation consistency, not measured aircraft performance.", "",
    ]
    (output / "decision-brief.md").write_text("\n".join(brief_lines), encoding="utf-8")
    if not args.no_plots:
        make_tradeoff_plot(output, plot_record)
    if removed_plot and args.no_plots:
        print("Stale trade-off chart removed; rerun without --no-plots to regenerate it.")
    print(f"Design study saved to {output}")


if __name__ == "__main__":
    main()
