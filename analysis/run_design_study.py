"""Check the compact concept against confirmed targets and inspect sensitivity."""

import json
import math

from analysis.run_analysis import (ROOT, calculate_case, load_config,
                                   load_mass_budget, write_csv)


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


def main():
    config = load_config(ROOT / "data/sar_design.json")
    masses = load_mass_budget(ROOT / "data/sar_mass_budget.csv")
    mass_kg = math.fsum(row["total_mass_kg"] for row in masses)
    brief = json.loads((ROOT / "data/project_brief.json").read_text(encoding="utf-8"))
    output = ROOT / "reports/design-study"
    output.mkdir(parents=True, exist_ok=True)
    baseline, _ = calculate_case(config, mass_kg)
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
        "The GBP 500 parts budget is a",
        "flexible student-project target. The observation payload is unselected.", "",
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
    print(f"Design study saved to {output}")


if __name__ == "__main__":
    main()
