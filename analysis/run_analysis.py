"""Run a single assumed design case and save reproducible reports."""

import argparse
import csv
import json
import math
from pathlib import Path

if __package__:
    from . import calculations as calc
else:
    import calculations as calc


ROOT = Path(__file__).resolve().parents[1]


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def load_config(path):
    with Path(path).open(encoding="utf-8") as stream:
        config = json.load(stream, object_pairs_hook=unique_json_object)
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")
    for key in ("case_name", "evidence_status"):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f"{key} must be a non-empty string.")

    positive_keys = [
        "air_density_kg_m3", "gravity_m_s2", "rotor_diameter_m",
        "thrust_to_weight_target", "wing_area_m2", "aspect_ratio",
        "maximum_lift_coefficient", "cruise_speed_m_s", "battery_voltage_v",
        "battery_capacity_ah", "transition_power_factor",
    ]
    fraction_keys = [
        "hover_figure_of_merit", "motor_esc_efficiency", "oswald_efficiency",
        "cruise_propeller_efficiency", "usable_battery_fraction",
    ]
    non_negative_keys = [
        "zero_lift_drag_coefficient", "auxiliary_power_w", "hover_time_s",
        "transition_time_s", "cruise_time_s",
    ]
    expected = set(positive_keys + fraction_keys + non_negative_keys
                   + ["case_name", "evidence_status", "rotor_count"])
    unknown = set(config) - expected
    if unknown:
        raise ValueError(f"Unknown configuration fields: {', '.join(sorted(unknown))}")
    for key in positive_keys:
        calc.positive(key, config.get(key))
    for key in fraction_keys:
        calc.fraction(key, config.get(key))
    for key in non_negative_keys:
        calc.non_negative(key, config.get(key))
    calc.rotor_disk_area_m2(config.get("rotor_count"), config["rotor_diameter_m"])
    if config["thrust_to_weight_target"] < 1:
        raise ValueError("thrust_to_weight_target must be at least one.")
    if config["transition_power_factor"] < 1:
        raise ValueError("transition_power_factor must be at least one.")
    return config


def load_mass_budget(path):
    rows = []
    components = set()
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"component", "quantity", "unit_mass_kg", "evidence", "notes"}
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or set(fields) != required:
            raise ValueError("Mass budget must have one of each required column and no extra columns.")
        for line_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Mass budget row {line_number} has the wrong number of cells.")
            component = row["component"].strip()
            evidence = row["evidence"].strip()
            if not component or not evidence:
                raise ValueError("Each mass item needs a component and evidence label.")
            if component in components:
                raise ValueError(f"Duplicate mass component: {component}")
            components.add(component)
            quantity = int(row["quantity"])
            unit_mass_kg = float(row["unit_mass_kg"])
            calc.positive(f"quantity for {component}", quantity)
            calc.positive(f"unit mass for {component}", unit_mass_kg)
            total_mass_kg = quantity * unit_mass_kg
            calc.positive(f"total mass for {component}", total_mass_kg)
            rows.append({
                "component": component,
                "quantity": quantity,
                "unit_mass_kg": unit_mass_kg,
                "total_mass_kg": total_mass_kg,
                "evidence": evidence,
                "notes": row["notes"].strip(),
            })
    if not rows:
        raise ValueError("Mass budget must contain at least one component.")
    return rows


def calculate_case(config, mass_kg):
    weight = calc.weight_n(mass_kg, config["gravity_m_s2"])
    area = calc.rotor_disk_area_m2(config["rotor_count"], config["rotor_diameter_m"])
    ideal_hover = calc.ideal_hover_power_w(weight, config["air_density_kg_m3"], area)
    hover_power = calc.electrical_hover_power_w(
        ideal_hover, config["hover_figure_of_merit"], config["motor_esc_efficiency"],
        config["auxiliary_power_w"])
    stall_speed = calc.stall_speed_m_s(
        weight, config["air_density_kg_m3"], config["wing_area_m2"],
        config["maximum_lift_coefficient"])
    drag = calc.cruise_drag_n(
        weight, config["cruise_speed_m_s"], config["air_density_kg_m3"],
        config["wing_area_m2"], config["aspect_ratio"], config["oswald_efficiency"],
        config["zero_lift_drag_coefficient"], config["maximum_lift_coefficient"])
    cruise_power = calc.electrical_cruise_power_w(
        drag, config["cruise_speed_m_s"], config["cruise_propeller_efficiency"],
        config["motor_esc_efficiency"], config["auxiliary_power_w"])
    battery_energy = calc.usable_battery_energy_wh(
        config["battery_voltage_v"], config["battery_capacity_ah"],
        config["usable_battery_fraction"])

    # Budget transition at an assumed multiple of hover propulsion power.
    transition_power = ((hover_power - config["auxiliary_power_w"])
                        * config["transition_power_factor"] + config["auxiliary_power_w"])
    segments = [
        {"segment": "hover", "power_w": hover_power, "duration_s": config["hover_time_s"]},
        {"segment": "transition allowance", "power_w": transition_power,
         "duration_s": config["transition_time_s"]},
        {"segment": "cruise", "power_w": cruise_power, "duration_s": config["cruise_time_s"]},
    ]
    for segment in segments:
        segment["energy_wh"] = calc.segment_energy_wh(segment["power_w"], segment["duration_s"])
    mission_energy = math.fsum(segment["energy_wh"] for segment in segments)
    summary = {
        "case_name": config["case_name"],
        "evidence_status": config["evidence_status"],
        "mass_kg": mass_kg,
        "weight_n": weight,
        "wingspan_m": math.sqrt(config["aspect_ratio"] * config["wing_area_m2"]),
        "mean_chord_m": math.sqrt(config["wing_area_m2"] / config["aspect_ratio"]),
        "wing_loading_n_m2": weight / config["wing_area_m2"],
        "rotor_disk_area_m2": area,
        "hover_thrust_per_rotor_n": weight / config["rotor_count"],
        "target_peak_thrust_per_rotor_n": (weight * config["thrust_to_weight_target"]
                                            / config["rotor_count"]),
        "disk_loading_n_m2": weight / area,
        "ideal_hover_power_w": ideal_hover,
        "electrical_hover_power_w": hover_power,
        "stall_speed_m_s": stall_speed,
        "cruise_to_stall_speed_ratio": config["cruise_speed_m_s"] / stall_speed,
        "cruise_drag_n": drag,
        "electrical_cruise_power_w": cruise_power,
        "nominal_battery_energy_wh": config["battery_voltage_v"] * config["battery_capacity_ah"],
        "usable_battery_energy_wh": battery_energy,
        "mission_energy_wh": mission_energy,
        "mission_duration_s": math.fsum(segment["duration_s"] for segment in segments),
        "remaining_usable_energy_wh": battery_energy - mission_energy,
        "mission_energy_within_budget": mission_energy <= battery_energy,
    }
    return summary, segments


def sensitivity_tables(config, mass_kg):
    mass_rows = []
    for step in range(7):
        varied_mass = mass_kg * (0.7 + 0.1 * step)
        area = calc.rotor_disk_area_m2(config["rotor_count"], config["rotor_diameter_m"])
        power = calc.ideal_hover_power_w(
            calc.weight_n(varied_mass, config["gravity_m_s2"]),
            config["air_density_kg_m3"], area)
        electrical_power = calc.electrical_hover_power_w(
            power, config["hover_figure_of_merit"], config["motor_esc_efficiency"],
            config["auxiliary_power_w"])
        mass_rows.append({"mass_kg": varied_mass, "hover_power_w": electrical_power})

    speed_rows = []
    weight = calc.weight_n(mass_kg, config["gravity_m_s2"])
    stall_speed = calc.stall_speed_m_s(
        weight, config["air_density_kg_m3"], config["wing_area_m2"],
        config["maximum_lift_coefficient"])
    # Sample only above stall. The factor is a plotting bound, not a flight limit.
    lower_speed = 1.1 * stall_speed
    upper_speed = max(2 * config["cruise_speed_m_s"], 2 * lower_speed)
    for step in range(31):
        speed = lower_speed + step * (upper_speed - lower_speed) / 30
        drag = calc.cruise_drag_n(
            weight, speed, config["air_density_kg_m3"], config["wing_area_m2"],
            config["aspect_ratio"], config["oswald_efficiency"],
            config["zero_lift_drag_coefficient"], config["maximum_lift_coefficient"])
        power = calc.electrical_cruise_power_w(
            drag, speed, config["cruise_propeller_efficiency"],
            config["motor_esc_efficiency"], config["auxiliary_power_w"])
        speed_rows.append({"speed_m_s": speed, "cruise_power_w": power})
    return mass_rows, speed_rows


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            formatted = {}
            for key, value in row.items():
                formatted[key] = round(value, 6) if isinstance(value, float) else value
            writer.writerow(formatted)


def write_reports(output_dir, config, mass_rows, summary, segments,
                  mass_sensitivity, cruise_sensitivity):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rounded = {}
    for key, value in summary.items():
        rounded[key] = round(value, 6) if isinstance(value, float) else value
    (output_dir / "summary.json").write_text(
        json.dumps(rounded, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (output_dir / "inputs.json").write_text(
        json.dumps(config, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_csv(output_dir / "mass_budget.csv", mass_rows)
    write_csv(output_dir / "mission_energy.csv", segments)
    write_csv(output_dir / "mass_sensitivity.csv", mass_sensitivity)
    write_csv(output_dir / "cruise_sensitivity.csv", cruise_sensitivity)

    # Format the report from the same rounded values stored in summary.json.
    summary = rounded
    status = "Within the assumed energy budget" if summary["mission_energy_within_budget"] else "Exceeds the assumed energy budget"
    lines = [
        "# Preliminary sizing results", "", f"Case: {config['case_name']}", "",
        f"Evidence status: **{config['evidence_status']}**.", "",
        "Generated by `python analysis/run_analysis.py`. Input snapshots are in",
        "[inputs.json](inputs.json) and [mass_budget.csv](mass_budget.csv).", "",
        "## Baseline estimates", "", "| Quantity | Estimate |", "| --- | ---: |",
        f"| All-up study mass | {summary['mass_kg']:.2f} kg |",
        f"| Implied wingspan | {summary['wingspan_m']:.3f} m |",
        f"| Mean chord | {summary['mean_chord_m']:.3f} m |",
        f"| Wing loading | {summary['wing_loading_n_m2']:.1f} N/m^2 |",
        f"| Total rotor disc area | {summary['rotor_disk_area_m2']:.3f} m^2 |",
        f"| Hover thrust per rotor | {summary['hover_thrust_per_rotor_n']:.2f} N |",
        f"| Peak thrust target per rotor | {summary['target_peak_thrust_per_rotor_n']:.2f} N |",
        f"| Ideal hover power | {summary['ideal_hover_power_w']:.1f} W |",
        f"| Estimated electrical hover power | {summary['electrical_hover_power_w']:.1f} W |",
        f"| Estimated stall speed | {summary['stall_speed_m_s']:.2f} m/s |",
        f"| Cruise speed / stall speed | {summary['cruise_to_stall_speed_ratio']:.2f} |",
        f"| Drag at {config['cruise_speed_m_s']:.1f} m/s | {summary['cruise_drag_n']:.2f} N |",
        f"| Estimated electrical cruise power | {summary['electrical_cruise_power_w']:.1f} W |",
        f"| Nominal battery energy | {summary['nominal_battery_energy_wh']:.1f} Wh |",
        f"| Usable battery energy | {summary['usable_battery_energy_wh']:.1f} Wh |",
        "", "## Assumed mission", "",
        "| Segment | Duration (s) | Electrical power (W) | Energy (Wh) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for segment in segments:
        lines.append(f"| {segment['segment']} | {segment['duration_s']:.0f} | "
                     f"{segment['power_w']:.1f} | {segment['energy_wh']:.2f} |")
    lines.extend([
        "", f"Total estimated mission energy: **{summary['mission_energy_wh']:.2f} Wh**.",
        f"Total assumed mission time: **{summary['mission_duration_s'] / 60:.1f} minutes**.",
        f"Remaining usable energy: **{summary['remaining_usable_energy_wh']:.2f} Wh**.",
        f"Budget comparison: **{status}**.", "",
        "The usable fraction already excludes an assumed battery reserve. Remaining",
        "usable energy is additional to that reserve; negative values indicate a shortfall.",
        "This comparison does not prove an aircraft can complete the mission.", "",
        "## Interpretation", "",
        "Hover power increases with mass to the power 1.5 at fixed disc area and",
        "efficiency (excluding the constant auxiliary load). Cruise power combines",
        "induced and zero-lift drag. The curves hold all other inputs fixed.", "",
        "## Limitations and next evidence", "",
        "- Efficiencies, drag coefficients, and maximum lift coefficient are assumed.",
        "- Rotor/wing interference, tilt mechanics, and transition dynamics are omitted.",
        "- Transition energy is an allowance, not a physics simulation.",
        "- Battery sag, temperature, ageing, and component current limits are omitted.",
        "- Peak thrust is a target; a motor/propeller has not been shown to meet it.",
        "- Structural integrity, centre of gravity, and control authority are unverified.",
        "", "Compare the model with sourced component data and controlled measurements",
        "before using it to select hardware. Record differences and uncertainty.", "",
    ])
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def plot_data(config, summary, mass_rows, speed_rows):
    data = {
        "case_name": config["case_name"],
        "mass_kg": round(summary["mass_kg"], 6),
        "hover_power_w": round(summary["electrical_hover_power_w"], 6),
        "cruise_speed_m_s": round(config["cruise_speed_m_s"], 6),
        "cruise_power_w": round(summary["electrical_cruise_power_w"], 6),
    }
    for name, rows in (("mass_sensitivity", mass_rows), ("cruise_sensitivity", speed_rows)):
        data[name] = []
        for row in rows:
            data[name].append({key: round(value, 6) for key, value in row.items()})
    return data


def remove_stale_plot(output_dir, expected_data, chart_names=("power_sensitivity.png",),
                      record_name="plot_data.json"):
    charts = [Path(output_dir) / name for name in chart_names]
    record = Path(output_dir) / record_name
    if not any(chart.exists() for chart in charts):
        return False
    try:
        saved_data = json.loads(record.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        saved_data = None
    if saved_data == expected_data and all(chart.exists() for chart in charts):
        return False
    for chart in charts:
        if chart.exists():
            chart.unlink()
    if record.exists():
        record.unlink()
    return True


def make_plots(output_dir, config, summary, mass_rows, speed_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    fig.suptitle("VTOL preliminary sizing | assumed inputs", fontsize=15)
    axes[0].plot([row["mass_kg"] for row in mass_rows],
                 [row["hover_power_w"] for row in mass_rows], color="#087e8b", linewidth=2)
    axes[0].scatter([summary["mass_kg"]], [summary["electrical_hover_power_w"]],
                    color="#bd3e36", zorder=3, label="Baseline")
    axes[0].set(title="Hover: mass sensitivity", xlabel="All-up mass (kg)",
                ylabel="Electrical hover power (W)")
    axes[1].plot([row["speed_m_s"] for row in speed_rows],
                 [row["cruise_power_w"] for row in speed_rows], color="#087e8b", linewidth=2)
    axes[1].scatter([config["cruise_speed_m_s"]], [summary["electrical_cruise_power_w"]],
                    color="#bd3e36", zorder=3, label="Baseline")
    axes[1].set(title="Cruise: airspeed sensitivity", xlabel="Airspeed (m/s)",
                ylabel="Electrical cruise power (W)")
    for axis in axes:
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
        axis.spines[["top", "right"]].set_visible(False)
    fig.savefig(Path(output_dir) / "power_sensitivity.png", dpi=160)
    plt.close(fig)
    (Path(output_dir) / "plot_data.json").write_text(
        json.dumps(plot_data(config, summary, mass_rows, speed_rows), indent=2) + "\n",
        encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "data/example_design.json")
    parser.add_argument("--mass-budget", type=Path, default=ROOT / "data/example_mass_budget.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/example")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        masses = load_mass_budget(args.mass_budget)
        mass_kg = math.fsum(row["total_mass_kg"] for row in masses)
        summary, segments = calculate_case(config, mass_kg)
        mass_rows, speed_rows = sensitivity_tables(config, mass_kg)
        removed_plot = remove_stale_plot(args.output_dir, plot_data(config, summary, mass_rows, speed_rows))
        write_reports(args.output_dir, config, masses, summary, segments, mass_rows, speed_rows)
        if not args.no_plots:
            make_plots(args.output_dir, config, summary, mass_rows, speed_rows)
    except ModuleNotFoundError as error:
        parser.exit(1, f"Plotting package missing: {error}. Install requirements.txt or use --no-plots.\n")
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f"Analysis failed: {error}\n")
    print(f"Case: {config['case_name']} ({config['evidence_status']})")
    print(f"Mass: {mass_kg:.2f} kg; hover power: {summary['electrical_hover_power_w']:.1f} W")
    print(f"Estimated mission energy: {summary['mission_energy_wh']:.2f} Wh")
    print(f"Remaining usable energy: {summary['remaining_usable_energy_wh']:.2f} Wh")
    if not summary["mission_energy_within_budget"]:
        print("WARNING: the assumed mission exceeds the usable battery energy budget.")
    if removed_plot and args.no_plots:
        print("Previous chart removed because its inputs changed. Rerun without --no-plots to plot this case.")
    print(f"Reports saved to {args.output_dir}")


if __name__ == "__main__":
    main()
