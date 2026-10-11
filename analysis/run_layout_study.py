"""Compare assumed rotor tilt envelopes and longitudinal mass distribution."""

import argparse
import json
import math
from pathlib import Path

from analysis.layout import (disc_point, hover_balance, load_layouts, rotor_envelope,
                             screen_layout, unequal_hover_power, centre_of_gravity)
from analysis.run_analysis import ROOT, load_config, load_mass_budget, remove_stale_plot, write_csv


def rounded(rows):
    return [{key: round(value, 6) if isinstance(value, float) else value
             for key, value in row.items()} for row in rows]


def write_summary(output, results, envelope, settings, config):
    radius = config["rotor_diameter_m"] / 2
    clearance = settings["planning_clearance_m"]
    reference = results[0]["reference_cg_x_m"]
    lines = [
        "# Provisional rotor-layout comparison", "",
        "AI-assisted geometric and static-balance screen, not an aircraft design approval.",
        "All four rotors tilt forward; rear rotors attach to the horizontal tail.",
        "Dimensions are explicit trial choices, not measurements of the owner's sketch.",
        f"All cases retain the existing assumed {results[0]['mass_kg']:.1f} kg mass budget; longer/wider structure",
        "does not get a mass penalty here. Actual structure sizing can change the ranking.", "",
        "[Methods, assumptions and interpretation](../../docs/layout-comparison.md).", "",
        "## Space required per rotor", "",
        f"Assumed diameter {2 * radius * 1000:.0f} mm; hub {settings['hub_axial_offset_m'] * 1000:.0f} mm",
        "along the thrust axis from a lateral hinge. Tilt range studied: 0 to 90 degrees.",
        f"Aerodynamic disc area: **{envelope['disc_area_m2']:.5f} m^2** per rotor;",
        f"continuous top-view swept projection: **{envelope['plan_sweep_area_m2']:.5f} m^2**.",
        "The latter is packaging area, not extra lifting-disc area.",
        f"Relative to a hinge, forward extent is {envelope['bounding_sphere_radius_m'] * 1000:.1f} mm;",
        f"aft extent {radius * 1000:.1f} mm; lateral half-width {radius * 1000:.1f} mm;",
        f"vertical range {-radius * 1000:.1f} to {envelope['bounding_sphere_radius_m'] * 1000:.1f} mm.",
        f"The assumed {clearance * 1000:.0f} mm planning gap is not a validated safety minimum.",
        f"Same-row hubs need at least **{(2 * radius + clearance) * 1000:.0f} mm** lateral spacing in this screen.",
        f"With hinges {settings['hinge_height_m'] * 1000:.0f} mm above the wing plane, keeping disc tips",
        f"{clearance * 1000:.0f} mm above flat ground through full tilt needs the wing plane at least",
        f"{max(0, radius - settings['hinge_height_m'] + clearance) * 1000:.1f} mm above ground.",
        "Blade thickness/flex, motor bodies, servo/linkage, attitude and gear deflection are omitted.", "",
        "![One rotor's plan and side sweep](rotor_sweep.png)", "",
        "## Comparison at a common CG reference", "",
        f"Reference x = **{reference * 1000:.1f} mm aft of the main-wing leading edge**",
        f"({100 * settings['cg_reference_chord_fraction']:.0f}% of the assumed reference chord). It is only a comparison datum,",
        "not an established cruise trim point, stable CG range or flight limit.",
        "Battery figures are centre positions with x positive aft. Negative is forward.", "",
        "| Trial | Row separation (mm) | Rear hub spacing (mm) | Rear disc gap (mm) | Disc-envelope screen | Battery x (mm) | Within assumed travel? | Front/rear thrust (%) | Hover estimate (W) |",
        "| --- | ---: | ---: | ---: | --- | ---: | --- | ---: | ---: |",
    ]
    for row in results:
        layout = next(item for item in settings["layouts"] if item["id"] == row["layout"])
        lines.append(
            f"| {row['layout']} {row['name']} | {row['row_separation_m'] * 1000:.0f} | "
            f"{row['rear_spacing_m'] * 1000:.0f} | {(layout['rear_spacing_m'] - 2 * radius) * 1000:.0f} | "
            f"{'Met' if row['disc_sweep_screen_met'] else 'Not met'} | {row['required_battery_x_m'] * 1000:.1f} | "
            f"{'Yes' if row['battery_reference_reachable'] else 'No'} | "
            f"{100 * row['front_thrust_fraction']:.1f}/{100 * (1 - row['front_thrust_fraction']):.1f} | "
            f"{row['electrical_hover_power_w']:.1f} |")
    lines.extend([
        "", "Power is diagnostic at the reference CG even where a layout fails clearance or",
        "the required battery centre lies outside its travel. Such a row is not feasible.",
        "Estimates omit download/interactions and keep efficiencies fixed. No mission",
        "energy or transition simulation has been updated from these trial geometries.", "",
        "![Four layouts on common-scale axes](layouts.png)", "",
        "## Weight distribution", "",
        f"Assumed battery-centre travel: {settings['battery_min_x_m'] * 1000:.0f} to",
        f"{settings['battery_max_x_m'] * 1000:.0f} mm. Pack dimensions and mounting are unselected.",
        "The existing airframe allowance is split 2/3 main structure and 1/3 tail/boom,",
        "not structural predictions. Motor, propeller and tilt allowances",
        "are split equally between rows. Other assumed stations are saved in the input file.", "",
        "| Trial | CG reachable by battery travel (mm aft of LE) | Equal-load hover CG (mm) | Front thrust each (N) | Rear thrust each (N) | Extra hover power vs equal loading (W) |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in results:
        lines.append(f"| {row['layout']} | {row['cg_min_x_m'] * 1000:.1f} to {row['cg_max_x_m'] * 1000:.1f} | "
                     f"{row['equal_load_cg_x_m'] * 1000:.1f} | {row['front_each_n']:.2f} | "
                     f"{row['rear_each_n']:.2f} | {row['extra_hover_power_w']:.1f} |")
    lines.extend([
        "", "![CG and front thrust share versus battery position](weight_distribution.png)", "",
        "## Rotor-thrust-only load indicators", "",
        "These are moments, not stresses, servo ratings or complete load cases.",
        "Front support is referenced to main-wing LE; tail half to centreline;",
        "boom to main-wing trailing edge. Own weights, aero, torque and dynamics are omitted.", "",
        "| Trial | Front support each (N*m) | Tail half each (N*m) | Boom from rear pair (N*m) |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in results:
        lines.append(f"| {row['layout']} | {row['front_support_thrust_moment_nm']:.2f} | "
                     f"{row['tail_half_thrust_moment_nm']:.2f} | {row['boom_rear_thrust_moment_nm']:.2f} |")
    lines.extend([
        "", "## Next mechanical study", "",
        "The initial B/C shortlist and trade-offs are explained in the methods document.",
        "Re-evaluate that interpretation after changing trial dimensions or mass stations;",
        "the generated table does not automatically select a build configuration.",
        "Do not move CG aft just to make hover thrust equal; assess wing/tail trim and",
        "stability separately. Keep heavy items near the centreline; lateral imbalance,",
        "vertical CG/inertia and moving component CG through tilt remain unmodelled.", "",
        "## Evidence and reproduction", "",
        "[Inputs](inputs.json), [comparison CSV](comparison.csv), [clearance CSV](clearances.csv),",
        "[trial mass positions](mass_positions.csv), [battery sweep](battery_sweep.csv).",
        "Mass positions include the algebraically required battery even if outside travel.",
        "Run `python -m analysis.run_layout_study`; add `--no-plots` for numerical outputs only.",
        "Verification checks the equations and reproducibility, not physical adequacy.", "",
    ])
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def make_plots(output, settings, config, results, sweep_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Rectangle
    import numpy as np

    radius = config["rotor_diameter_m"] / 2
    offset = settings["hub_axial_offset_m"]
    bound = math.hypot(radius, offset)
    span = math.sqrt(config["wing_area_m2"] * config["aspect_ratio"])
    chord = math.sqrt(config["wing_area_m2"] / config["aspect_ratio"])
    v = np.linspace(-radius, radius, 301)
    aft = np.sqrt(np.maximum(0, radius ** 2 - v ** 2))
    forward = -np.sqrt(np.maximum(0, bound ** 2 - v ** 2))
    colours = {"A": "#bd3e36", "B": "#087e8b", "C": "#397842", "D": "#846138"}
    count = len(results)
    fig, axes = plt.subplots(math.ceil(count / 2), 2, figsize=(11, 5 * math.ceil(count / 2)),
                             constrained_layout=True, squeeze=False)
    x_min = min(settings["battery_min_x_m"], min(row["front_x_m"] for row in settings["layouts"])) - bound - 0.04
    x_max = max(row["rear_x_m"] for row in settings["layouts"]) + settings["tail_leading_edge_offset_m"] + settings["tail_chord_m"] + 0.05
    half_width = max(max(row["wing_and_prop_width_m"] for row in results), span) / 2 + 0.05
    for axis, result, layout in zip(axes.flat, results, settings["layouts"]):
        colour = colours.get(layout["id"], "#087e8b")
        axis.add_patch(Rectangle((-span / 2, 0), span, chord, color="#d6dde0"))
        axis.add_patch(Rectangle((-settings["boom_half_width_m"], chord),
                                 2 * settings["boom_half_width_m"], layout["rear_x_m"] - chord
                                 + settings["tail_leading_edge_offset_m"], color="#a9b3b8"))
        tail_le = layout["rear_x_m"] + settings["tail_leading_edge_offset_m"]
        axis.add_patch(Rectangle((-layout["tail_span_m"] / 2, tail_le), layout["tail_span_m"],
                                 settings["tail_chord_m"], color="#d6dde0"))
        axis.add_patch(Rectangle((-settings["fuselage_half_width_m"], settings["fuselage_forward_x_m"]),
                                 2 * settings["fuselage_half_width_m"],
                                 settings["fuselage_aft_x_m"] - settings["fuselage_forward_x_m"],
                                 facecolor="#f5f5f5", edgecolor="#555555"))
        for row_name in ("front", "rear"):
            x = layout[f"{row_name}_x_m"]
            for y in (-layout[f"{row_name}_spacing_m"] / 2, layout[f"{row_name}_spacing_m"] / 2):
                axis.fill(np.r_[y + v, (y + v)[::-1]],
                          np.r_[x + forward, (x + aft)[::-1]], color=colour, alpha=0.2)
                axis.add_patch(Circle((y, x), radius, fill=False, edgecolor=colour, linewidth=1.3))
                axis.plot([y], [x], "o", color="#333333", markersize=3)
                surface_x = 0 if row_name == "front" else tail_le
                axis.plot([y, y], [x, surface_x], color="#555555", linewidth=1)
        axis.axhline(result["reference_cg_x_m"], color="#bd3e36", linestyle="--", linewidth=1)
        axis.plot([0, 0], [result["cg_min_x_m"], result["cg_max_x_m"]], color="#333333", linewidth=3)
        axis.plot([0], [result["required_battery_x_m"]], "D", color=colour, markersize=5)
        axis.set(xlim=(-half_width, half_width), ylim=(x_max, x_min), aspect="equal",
                 xlabel="Lateral position y (m)", ylabel="Aft position x (m)",
                 title=f"{layout['id']}  {layout['name']}\nDisc screen: {'met' if result['disc_sweep_screen_met'] else 'not met'}")
        axis.grid(alpha=0.15)
    for axis in list(axes.flat)[count:]:
        axis.set_visible(False)
    fig.suptitle("Provisional layouts | common scale, nose up\nTint: tilt projection; circle: hover disc; diamond: trial battery; dashed: CG reference", fontsize=12)
    fig.savefig(output / "layouts.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    axes[0].fill(np.r_[forward, aft[::-1]], np.r_[v, v[::-1]], color="#087e8b", alpha=0.2,
                 label="Full 0-90 deg projection")
    axes[0].add_patch(Circle((0, 0), radius, fill=False, edgecolor="#087e8b", label="Hover disc"))
    axes[0].plot([0], [0], "o", color="#333333", label="Hinge")
    axes[0].set(title="One rotor: top view", xlabel="x relative to hinge (m), forward negative",
                ylabel="y relative to hinge (m)", aspect="equal")
    height, front_x = settings["hinge_height_m"], settings["layouts"][0]["front_x_m"]
    for angle in range(0, 91, 5):
        points = [disc_point(2 * radius, offset, math.radians(angle), u, 0) for u in (-radius, radius)]
        axes[1].plot([front_x + p[0] for p in points], [height + p[2] for p in points],
                     color="#087e8b", alpha=0.22, linewidth=1)
    for angle, colour, label in ((0, "#397842", "Hover"), (90, "#bd3e36", "Forward thrust")):
        points = [disc_point(2 * radius, offset, math.radians(angle), u, 0) for u in (-radius, radius)]
        axes[1].plot([front_x + p[0] for p in points], [height + p[2] for p in points], color=colour,
                     linewidth=2, label=label)
    axes[1].add_patch(Rectangle((0, -settings["surface_thickness_m"] / 2), chord,
                               settings["surface_thickness_m"], color="#a9b3b8", label="Wing section"))
    axes[1].plot([front_x], [height], "o", color="#333333", label="Hinge")
    axes[1].add_patch(Rectangle((front_x - bound, height - radius), bound + radius,
                               bound + radius, fill=False, linestyle="--", edgecolor="#777777"))
    ground = min(0, height - radius - settings["planning_clearance_m"])
    axes[1].axhline(ground, color="#846138", linestyle=":", label="Illustrative ground")
    axes[1].set(title="First trial front rotor: side projection", xlabel="x aft of wing LE (m)",
                ylabel="z above wing plane (m)", aspect="equal")
    for axis in axes:
        axis.grid(alpha=0.15)
        axis.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2)
    fig.suptitle(f"Assumed disc sweep | {2 * radius * 1000:.0f} mm propeller, {offset * 1000:.0f} mm axial hinge offset", fontsize=12)
    fig.savefig(output / "rotor_sweep.png", dpi=150)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    for result in results:
        rows = [row for row in sweep_rows if row["layout"] == result["layout"]]
        label = f"{result['layout']} {result['name']}"
        style = "--" if result["layout"] == "A" else "-"
        for axis, key, scale in ((axes[0], "cg_x_m", 1000), (axes[1], "front_thrust_fraction", 100)):
            axis.plot([row["battery_x_m"] * 1000 for row in rows], [row[key] * scale for row in rows],
                      color=colours.get(result["layout"], "#087e8b"), linestyle=style, label=label)
    axes[0].axhline(results[0]["reference_cg_x_m"] * 1000, color="#555555", linestyle=":", label="Comparison CG reference")
    axes[1].axhline(50, color="#555555", linestyle=":", label="Equal front/rear loading")
    axes[0].set(ylabel="CG aft of wing LE (mm)", title="CG reachable by battery travel")
    axes[1].set(ylabel="Front pair share of total hover thrust (%)", title="Static loading at each reachable CG")
    for axis in axes:
        axis.set_xlabel("Battery centre x (mm), negative forward")
        axis.grid(alpha=0.2)
        axis.legend(frameon=False, fontsize=8)
    fig.suptitle(f"Same assumed {results[0]['mass_kg']:.1f} kg budget | centreline items, symmetric rotor pairs", fontsize=12)
    fig.savefig(output / "weight_distribution.png", dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layouts", type=Path, default=ROOT / "data/provisional_layouts.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/layout-study")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    try:
        settings = load_layouts(args.layouts)
        config = load_config(ROOT / "data/sar_design.json")
        masses = load_mass_budget(ROOT / "data/sar_mass_budget.csv")
        output = args.output_dir
        output.mkdir(parents=True, exist_ok=True)
        results, clear_rows, mass_rows, sweep_rows = [], [], [], []
        for layout in settings["layouts"]:
            result, clearances, other, battery_mass = screen_layout(config, masses, layout, settings)
            results.append(result)
            clear_rows.extend({"layout": layout["id"], "check": key, "gap_m": value,
                               "planning_gap_m": settings["planning_clearance_m"],
                               "meets_planning_gap": value >= settings["planning_clearance_m"]}
                              for key, value in clearances.items())
            mass_rows.extend({"layout": layout["id"], **row} for row in other)
            mass_rows.append({"layout": layout["id"], "component": "Battery", "group": "reference-CG trial",
                              "mass_kg": battery_mass, "x_m": result["required_battery_x_m"]})
            for step in range(35):
                battery_x = settings["battery_min_x_m"] + step * (settings["battery_max_x_m"] - settings["battery_min_x_m"]) / 34
                cg = centre_of_gravity(other + [{"mass_kg": battery_mass, "x_m": battery_x}])
                balance = hover_balance(result["mass_kg"] * config["gravity_m_s2"], layout["front_x_m"], layout["rear_x_m"], cg)
                sweep_rows.append({"layout": layout["id"], "battery_x_m": battery_x, "cg_x_m": cg,
                                   "front_thrust_fraction": balance["front_fraction"],
                                   "electrical_hover_power_w": unequal_hover_power(config, balance)})
        results, clear_rows, mass_rows, sweep_rows = map(rounded, (results, clear_rows, mass_rows, sweep_rows))
        envelope = rounded([rotor_envelope(config["rotor_diameter_m"], settings["hub_axial_offset_m"])])[0]
        inputs = {"design": config, "mass_budget": masses, "layout_settings": settings,
                  "mass_split_assumption": "2/3 airframe main structure, 1/3 tail/boom; equal motor/prop/tilt row masses; positions refer to hover",
                  "tilt_range_deg": [0, 90], "lateral_mass_assumption": "Centreline items and symmetric pairs; no roll or moving-CG model"}
        record = {"inputs": inputs, "comparison": results, "envelope": envelope}
        charts = ("layouts.png", "rotor_sweep.png", "weight_distribution.png")
        removed = remove_stale_plot(output, record, charts, "plot_inputs.json")
        for name, rows in (("comparison", results), ("clearances", clear_rows),
                           ("mass_positions", mass_rows), ("battery_sweep", sweep_rows)):
            write_csv(output / f"{name}.csv", rows)
        (output / "inputs.json").write_text(json.dumps(inputs, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (output / "rotor_envelope.json").write_text(json.dumps(envelope, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        write_summary(output, results, envelope, settings, config)
        if not args.no_plots:
            make_plots(output, settings, config, results, sweep_rows)
            (output / "plot_inputs.json").write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        if removed and args.no_plots:
            print("Stale layout charts removed; rerun without --no-plots to regenerate.")
    except (ValueError, KeyError, TypeError, OSError, ModuleNotFoundError) as error:
        parser.exit(1, f"Layout study failed: {error}\n")
    print(f"Provisional layout comparison saved to {output}")


if __name__ == "__main__":
    main()
