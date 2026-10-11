"""Five-state point-mass model with ideal attitude and fixed wing trim."""

import math

from analysis import calculations as calc


CONTROL = {
    "reference_altitude_m": 10.0,
    "altitude_gain_s2": 1.0,
    "vertical_damping_s": 2.0,
    "speed_gain_s": 1.0,
    "tilt_time_constant_s": 0.4,
    "maximum_tilt_rate_deg_s": 20.0,
    "transition_start_s": 5.0,
    "transition_ramp_s": 25.0,
    "assumed_maximum_total_thrust_n": 58.86,
}


def speed_reference(time_s, config, scenario):
    if scenario == "hover":
        return 0.0
    if scenario != "transition":
        raise ValueError("Scenario must be hover or transition.")
    progress = (time_s - CONTROL["transition_start_s"]) / CONTROL["transition_ramp_s"]
    progress = min(1.0, max(0.0, progress))
    smooth_ramp = 3 * progress ** 2 - 2 * progress ** 3
    return config["cruise_speed_m_s"] * smooth_ramp


def forces_and_derivatives(time_s, state, config, mass_kg, scenario):
    """Return [x_dot, z_dot, vx_dot, vz_dot, tilt_dot] and force diagnostics."""
    calc.positive("mass_kg", mass_kg)
    _, altitude, forward_speed, vertical_speed, tilt = state
    weight = mass_kg * config["gravity_m_s2"]
    speed = math.hypot(forward_speed, vertical_speed)
    cruise_q = 0.5 * config["air_density_kg_m3"] * config["cruise_speed_m_s"] ** 2
    trimmed_cl = weight / (cruise_q * config["wing_area_m2"])
    if trimmed_cl > config["maximum_lift_coefficient"]:
        raise ValueError("Chosen cruise trim exceeds assumed CLmax.")
    drag_coefficient = (config["zero_lift_drag_coefficient"]
                        + trimmed_cl ** 2 / (math.pi * config["aspect_ratio"]
                                             * config["oswald_efficiency"]))
    # Wing pressure uses forward speed; vertical-flow aerodynamics are omitted.
    dynamic_pressure = 0.5 * config["air_density_kg_m3"] * max(0.0, forward_speed) ** 2
    lift = dynamic_pressure * config["wing_area_m2"] * trimmed_cl
    drag = dynamic_pressure * config["wing_area_m2"] * drag_coefficient
    if speed > 1e-9:
        aero_x = -drag * forward_speed / speed - lift * vertical_speed / speed
        aero_z = -drag * vertical_speed / speed + lift * forward_speed / speed
    else:
        aero_x = 0.0
        aero_z = 0.0

    commanded_speed = speed_reference(time_s, config, scenario)
    desired_acceleration_x = CONTROL["speed_gain_s"] * (commanded_speed - forward_speed)
    desired_acceleration_z = (CONTROL["altitude_gain_s2"]
                              * (CONTROL["reference_altitude_m"] - altitude)
                              - CONTROL["vertical_damping_s"] * vertical_speed)
    requested_x = max(0.0, mass_kg * desired_acceleration_x - aero_x)
    requested_z = max(0.0, mass_kg * desired_acceleration_z + weight - aero_z)
    requested_thrust = math.hypot(requested_x, requested_z)
    maximum_thrust = CONTROL["assumed_maximum_total_thrust_n"]
    thrust = min(requested_thrust, maximum_thrust)
    requested_tilt = math.atan2(requested_x, requested_z)
    rate_limit = math.radians(CONTROL["maximum_tilt_rate_deg_s"])
    tilt_rate = (requested_tilt - tilt) / CONTROL["tilt_time_constant_s"]
    tilt_rate = min(rate_limit, max(-rate_limit, tilt_rate))

    # Thrust tilt is measured forward from vertical; attitude is assumed controlled.
    thrust_x = thrust * math.sin(tilt)
    thrust_z = thrust * math.cos(tilt)
    derivatives = [forward_speed, vertical_speed,
                   (thrust_x + aero_x) / mass_kg,
                   (thrust_z + aero_z - weight) / mass_kg,
                   tilt_rate]
    diagnostics = {
        "speed_reference_m_s": commanded_speed,
        "total_thrust_n": thrust,
        "requested_thrust_n": requested_thrust,
        "wing_vertical_force_n": aero_z,
        "wing_support_fraction": aero_z / weight,
        "thrust_limited": requested_thrust > maximum_thrust,
    }
    return derivatives, diagnostics


def simulate(config, mass_kg, scenario, maximum_step_s=0.05):
    import numpy as np
    from scipy.integrate import solve_ivp

    duration = 20.0 if scenario == "hover" else 60.0
    altitude = CONTROL["reference_altitude_m"]
    initial_altitude = altitude - 0.25 if scenario == "hover" else altitude
    initial_state = [0.0, initial_altitude, 0.0, 0.0, 0.0]
    samples = np.linspace(0.0, duration, int(duration * 10) + 1)

    def derivatives(time_s, state):
        return forces_and_derivatives(time_s, state, config, mass_kg, scenario)[0]

    solution = solve_ivp(derivatives, (0.0, duration), initial_state,
                         t_eval=samples, rtol=1e-7, atol=1e-9,
                         max_step=maximum_step_s)
    if not solution.success or not np.isfinite(solution.y).all():
        raise RuntimeError(f"Simulation failed: {solution.message}")
    rows = []
    for index, time_s in enumerate(solution.t):
        state = solution.y[:, index]
        _, values = forces_and_derivatives(time_s, state, config, mass_kg, scenario)
        rows.append({
            "time_s": float(time_s), "x_m": float(state[0]),
            "altitude_m": float(state[1]), "forward_speed_m_s": float(state[2]),
            "vertical_speed_m_s": float(state[3]), "tilt_deg": math.degrees(state[4]),
            **values,
        })
    summary = {
        "scenario": scenario, "mass_kg": mass_kg,
        "final_speed_m_s": rows[-1]["forward_speed_m_s"],
        "final_altitude_error_m": rows[-1]["altitude_m"] - altitude,
        "maximum_altitude_error_m": max(abs(row["altitude_m"] - altitude) for row in rows),
        "minimum_altitude_m": min(row["altitude_m"] for row in rows),
        "final_tilt_deg": rows[-1]["tilt_deg"],
        "final_wing_support_fraction": rows[-1]["wing_support_fraction"],
        "maximum_thrust_n": max(row["total_thrust_n"] for row in rows),
        "sampled_thrust_limit_count": sum(row["thrust_limited"] for row in rows),
    }
    return rows, summary
