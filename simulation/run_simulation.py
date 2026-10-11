"""Generate nominal and upper-mass educational hover/transition results."""

import argparse
import json
import math
from pathlib import Path

from analysis.run_analysis import (ROOT, load_config, load_mass_budget,
                                   remove_stale_plot, write_csv)
from simulation.planar import CONTROL, simulate


def plot_results(output, all_rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for scenario in ("hover", "transition"):
        shape = (1, 2) if scenario == "hover" else (2, 2)
        size = (10, 3.8) if scenario == "hover" else (10, 7)
        fig, axes = plt.subplots(*shape, figsize=size, constrained_layout=True)
        fig.suptitle(f"{scenario.title()} | point-mass model, ideal attitude", fontsize=14)
        quantities = [("forward_speed_m_s", "Forward speed (m/s)"),
                      ("altitude_m", "Altitude (m)"),
                      ("tilt_deg", "Rotor tilt from vertical (deg)"),
                      ("wing_support_fraction", "Wing vertical force / weight")]
        if scenario == "hover":
            quantities = [("altitude_m", "Altitude (m)"),
                          ("vertical_speed_m_s", "Vertical speed (m/s)")]
        for key, rows in all_rows.items():
            if key[0] != scenario:
                continue
            times = [row["time_s"] for row in rows]
            for axis, (quantity, label) in zip(axes.flat, quantities):
                axis.plot(times, [row[quantity] for row in rows], label=f"{key[1]:.1f} kg")
                axis.set(xlabel="Time (s)", ylabel=label)
                axis.grid(alpha=0.2)
                axis.spines[["top", "right"]].set_visible(False)
        altitude_axis = axes.flat[0] if scenario == "hover" else axes.flat[1]
        altitude_axis.axhline(CONTROL["reference_altitude_m"], color="black", linestyle="--", alpha=0.5)
        axes.flat[0].legend(frameon=False)
        fig.savefig(output / f"{scenario}.png", dpi=150)
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/simulation")
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args()
    config = load_config(ROOT / "data/sar_design.json")
    mass_rows = load_mass_budget(ROOT / "data/sar_mass_budget.csv")
    nominal_mass = math.fsum(row["total_mass_kg"] for row in mass_rows)
    brief = json.loads((ROOT / "data/project_brief.json").read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    input_record = {
        "design": config, "controls": CONTROL,
        "masses_kg": [round(nominal_mass, 6), brief["maximum_mass_kg"]],
        "model": "Point mass; attitude and fixed CL trim are ideal assumptions",
        "solver": "SciPy solve_ivp RK45; rtol=1e-7; atol=1e-9; max_step=0.05 s",
    }
    removed_plot = remove_stale_plot(args.output_dir, input_record,
                                    ("hover.png", "transition.png"), "plot_inputs.json")
    all_rows = {}
    summaries = []
    for mass in (nominal_mass, brief["maximum_mass_kg"]):
        for scenario in ("hover", "transition"):
            rows, summary = simulate(config, mass, scenario)
            all_rows[(scenario, mass)] = rows
            summaries.append(summary)
            write_csv(args.output_dir / f"{scenario}_{mass:.1f}kg.csv", rows)
    write_csv(args.output_dir / "summary.csv", summaries)
    (args.output_dir / "inputs.json").write_text(
        json.dumps(input_record, indent=2) + "\n", encoding="utf-8")
    if not args.no_plots:
        plot_results(args.output_dir, all_rows)
        (args.output_dir / "plot_inputs.json").write_text(
            json.dumps(input_record, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Educational hover and forward-transition simulation", "",
        "This five-state longitudinal point-mass model illustrates force sharing",
        "between tilted rotor thrust and wing lift. Attitude control and a constant",
        "trimmed lift coefficient are ideal assumptions. It does not simulate",
        "pitch/roll/yaw dynamics, moments, rotor allocation, structural loads,",
        "return transition, or landing. These are not validated aircraft results.", "",
        "The hover case starts 0.25 m below the reference altitude. The transition",
        "case ramps the speed command from zero to 22 m/s over 25 seconds after",
        "5 seconds of hover. Height is an illustrative airborne reference, not a",
        "proposed flight-test instruction. Inputs and controller gains are assumed.", "",
        "| Case | Mass (kg) | Final speed (m/s) | Maximum height error (m) | Final wing support fraction |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        lines.append(f"| {row['scenario']} | {row['mass_kg']:.1f} | "
                     f"{row['final_speed_m_s']:.3f} | {row['maximum_altitude_error_m']:.3f} | "
                     f"{row['final_wing_support_fraction']:.3f} |")
    lines.extend([
        "", "Hover.png and transition.png show the nominal and upper-mass runs when generated.",
        "Both use the same assumed 58.86 N total thrust ceiling, corresponding to",
        "the 3 kg candidate's 2:1 thrust target. This is not a measured hardware limit.",
        "The upper-mass run has a lower thrust-to-weight margin. Ideal wing trim and",
        "mass-scaled control forces also explain the similar response curves.",
        "The successful force handover depends on the assumed perfect attitude",
        "and trim control. The 5 kg simulation does not override the failed 30-minute",
        "energy screen for that mass. Simulation power/endurance is not calculated:",
        "the separate sizing study uses steady power models and a transition allowance.", "",
        "Next: add aircraft geometry, moments/inertia, actuator torque limits,",
        "aerodynamic coefficients versus angle of attack, and attitude dynamics",
        "before treating this as a transition-control validation model.", "",
    ])
    (args.output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    if removed_plot and args.no_plots:
        print("Stale charts removed; rerun without --no-plots to generate matching charts.")
    print(f"Point-mass simulation reports saved to {args.output_dir}")


if __name__ == "__main__":
    main()
