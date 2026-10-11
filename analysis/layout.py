"""Provisional disc envelopes and static hover balance, in metres/newtons."""

import math
import json

from analysis import calculations as calc
from analysis.run_analysis import unique_json_object


def load_layouts(path):
    with open(path, encoding="utf-8") as stream:
        settings = json.load(stream, object_pairs_hook=unique_json_object)
    positive = {"hinge_height_m", "surface_thickness_m", "tail_chord_m",
                "fuselage_half_width_m", "boom_half_width_m", "fuselage_half_height_m"}
    non_negative = {"hub_axial_offset_m", "planning_clearance_m", "tail_leading_edge_offset_m"}
    fractions = {"cg_reference_chord_fraction", "tail_boom_centre_fraction"}
    stations = {"battery_min_x_m", "battery_max_x_m", "main_structure_x_m", "esc_x_m",
                "avionics_x_m", "wiring_x_m", "landing_gear_x_m", "payload_x_m",
                "contingency_x_m", "fuselage_forward_x_m", "fuselage_aft_x_m"}
    expected = positive | non_negative | fractions | stations | {"layouts", "evidence_status"}
    if not isinstance(settings, dict) or set(settings) != expected:
        raise ValueError("Layout settings must contain exactly the documented fields.")
    if not isinstance(settings["evidence_status"], str) or not settings["evidence_status"].strip():
        raise ValueError("Layout settings require an evidence label.")
    for field in positive:
        calc.positive(field, settings[field])
    for field in non_negative:
        calc.non_negative(field, settings[field])
    for field in fractions:
        calc.fraction(field, settings[field])
    for field in stations:
        value = settings[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{field} must be a finite number.")
    if settings["battery_min_x_m"] >= settings["battery_max_x_m"]:
        raise ValueError("Battery centre travel must have increasing limits.")
    if settings["fuselage_forward_x_m"] >= settings["fuselage_aft_x_m"]:
        raise ValueError("Fuselage longitudinal limits must increase aft.")
    layouts = settings["layouts"]
    if not isinstance(layouts, list) or not layouts:
        raise ValueError("At least one provisional layout is required.")
    identifiers = set()
    for layout in layouts:
        fields = {"id", "name", "front_x_m", "rear_x_m", "front_spacing_m", "rear_spacing_m", "tail_span_m"}
        if not isinstance(layout, dict) or set(layout) != fields:
            raise ValueError("Each layout must contain exactly the documented fields.")
        for field in ("id", "name"):
            if not isinstance(layout[field], str) or not layout[field].strip():
                raise ValueError("Layout ID and name must be nonempty strings.")
        if layout["id"] in identifiers:
            raise ValueError("Layout IDs must be unique.")
        identifiers.add(layout["id"])
        front = layout["front_x_m"]
        if isinstance(front, bool) or not isinstance(front, (int, float)) or not math.isfinite(front) or front > 0:
            raise ValueError("Front hinge must be at or ahead of the main-wing leading edge.")
        for field in ("rear_x_m", "front_spacing_m", "rear_spacing_m", "tail_span_m"):
            calc.positive(field, layout[field])
        if layout["tail_span_m"] < layout["rear_spacing_m"]:
            raise ValueError("Rear hinge centres must lie within the assumed tail span.")
    return settings


def rotor_envelope(diameter_m, hub_offset_m):
    """Disc normal tilts forward 0..90 deg about a lateral hinge; x is aft."""
    calc.positive("diameter_m", diameter_m)
    calc.non_negative("hub_offset_m", hub_offset_m)
    radius = diameter_m / 2
    sweep_radius = math.hypot(radius, hub_offset_m)
    # Integrate the continuous top-view width at each lateral coordinate.
    plan_area = (math.pi * radius ** 2 / 2 + radius * hub_offset_m
                 + sweep_radius ** 2 * math.asin(radius / sweep_radius))
    return {
        "disc_area_m2": math.pi * radius ** 2,
        "plan_sweep_area_m2": plan_area,
        "bounding_sphere_radius_m": sweep_radius,
        "x_min_relative_hinge_m": -sweep_radius,
        "x_max_relative_hinge_m": radius,
        "y_half_extent_m": radius,
        "z_min_relative_hinge_m": -radius,
        "z_max_relative_hinge_m": sweep_radius,
    }


def disc_point(diameter_m, hub_offset_m, tilt_rad, u_m, v_m):
    """One disc point relative to its hinge; u^2+v^2 must be <= R^2."""
    calc.positive("diameter_m", diameter_m)
    calc.non_negative("hub_offset_m", hub_offset_m)
    calc.non_negative("tilt_rad", tilt_rad)
    if tilt_rad > math.pi / 2:
        raise ValueError("Tilt must lie between zero and pi/2.")
    for name, value in (("u_m", u_m), ("v_m", v_m)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be a finite number.")
    if math.hypot(u_m, v_m) > diameter_m / 2 + 1e-12:
        raise ValueError("Point is outside the rotor disc.")
    sine, cosine = math.sin(tilt_rad), math.cos(tilt_rad)
    return (-hub_offset_m * sine + u_m * cosine, v_m,
            hub_offset_m * cosine + u_m * sine)


def centre_of_gravity(rows):
    if not rows:
        raise ValueError("Mass positions cannot be empty.")
    for row in rows:
        calc.positive("mass_kg", row["mass_kg"])
        x = row["x_m"]
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
            raise ValueError("Mass position must be a finite number.")
    mass = math.fsum(row["mass_kg"] for row in rows)
    moment = math.fsum(row["mass_kg"] * row["x_m"] for row in rows)
    return moment / mass


def battery_position(other_rows, battery_mass_kg, target_cg_m):
    calc.positive("battery_mass_kg", battery_mass_kg)
    centre_of_gravity(other_rows)
    if isinstance(target_cg_m, bool) or not isinstance(target_cg_m, (int, float)) or not math.isfinite(target_cg_m):
        raise ValueError("Target CG must be a finite number.")
    total_mass = math.fsum(row["mass_kg"] for row in other_rows) + battery_mass_kg
    other_moment = math.fsum(row["mass_kg"] * row["x_m"] for row in other_rows)
    return (total_mass * target_cg_m - other_moment) / battery_mass_kg


def hover_balance(weight_n, front_x_m, rear_x_m, cg_x_m):
    """Two symmetric rotors per row; vertical thrust, no other moments."""
    calc.positive("weight_n", weight_n)
    for x in (front_x_m, rear_x_m, cg_x_m):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
            raise ValueError("Thrust lines and CG must be finite numbers.")
    if not front_x_m < cg_x_m < rear_x_m:
        raise ValueError("CG must be strictly between the thrust rows.")
    front_fraction = (rear_x_m - cg_x_m) / (rear_x_m - front_x_m)
    return {
        "front_fraction": front_fraction,
        "rear_fraction": 1 - front_fraction,
        "front_each_n": weight_n * front_fraction / 2,
        "rear_each_n": weight_n * (1 - front_fraction) / 2,
    }


def unequal_hover_power(config, balance):
    single_area = calc.rotor_disk_area_m2(1, config["rotor_diameter_m"])
    ideal = 2 * math.fsum(calc.ideal_hover_power_w(
        balance[key], config["air_density_kg_m3"], single_area)
        for key in ("front_each_n", "rear_each_n"))
    return calc.electrical_hover_power_w(
        ideal, config["hover_figure_of_merit"], config["motor_esc_efficiency"],
        config["auxiliary_power_w"])


def positioned_mass_rows(mass_budget, layout, assumptions):
    """Keep the existing mass budget; split structure 2/3 main and 1/3 tail/boom."""
    masses = {row["component"]: row["total_mass_kg"] for row in mass_budget}
    expected = {"Wing and airframe", "Tilting motors", "Propellers", "ESCs", "Battery",
                "Tilt assemblies and servos", "Avionics", "Wiring and connectors",
                "Landing gear", "Unselected observation payload", "Design contingency"}
    if set(masses) != expected:
        raise ValueError("Update layout mass-placement rules for the changed mass budget.")
    rows = []

    def add(component, fraction, x, group):
        rows.append({"component": component, "group": group,
                     "mass_kg": masses[component] * fraction, "x_m": x})

    add("Wing and airframe", 2 / 3, assumptions["main_structure_x_m"], "main structure")
    add("Wing and airframe", 1 / 3,
        assumptions["tail_boom_centre_fraction"] * layout["rear_x_m"], "tail and boom")
    for component in ("Tilting motors", "Propellers", "Tilt assemblies and servos"):
        for row_name in ("front", "rear"):
            add(component, 0.5, layout[f"{row_name}_x_m"], row_name + " pair")
    for component, station in (
            ("ESCs", "esc"), ("Avionics", "avionics"), ("Wiring and connectors", "wiring"),
            ("Landing gear", "landing_gear"), ("Unselected observation payload", "payload"),
            ("Design contingency", "contingency")):
        add(component, 1, assumptions[f"{station}_x_m"], "central allowance")
    return rows, masses["Battery"]


def screen_layout(config, mass_budget, layout, assumptions):
    if config["rotor_count"] != 4:
        raise ValueError("This layout model requires two front and two rear rotors.")
    envelope = rotor_envelope(config["rotor_diameter_m"], assumptions["hub_axial_offset_m"])
    radius = config["rotor_diameter_m"] / 2
    gap = assumptions["planning_clearance_m"]
    other, battery_mass = positioned_mass_rows(mass_budget, layout, assumptions)
    mass = math.fsum(row["mass_kg"] for row in other) + battery_mass
    chord = math.sqrt(config["wing_area_m2"] / config["aspect_ratio"])
    reference_cg = assumptions["cg_reference_chord_fraction"] * chord
    required_battery = battery_position(other, battery_mass, reference_cg)
    balance = hover_balance(calc.weight_n(mass, config["gravity_m_s2"]),
                            layout["front_x_m"], layout["rear_x_m"], reference_cg)
    power = unequal_hover_power(config, balance)
    equal_balance = {"front_each_n": mass * config["gravity_m_s2"] / 4,
                     "rear_each_n": mass * config["gravity_m_s2"] / 4}
    equal_power = unequal_hover_power(config, equal_balance)

    def cg_at(x):
        return centre_of_gravity(other + [{"mass_kg": battery_mass, "x_m": x}])

    # Sphere bounds prove cross-row separation even for independently tilting discs.
    cross_distance = math.hypot(layout["rear_x_m"] - layout["front_x_m"],
                                (layout["front_spacing_m"] - layout["rear_spacing_m"]) / 2)
    clearances = {
        "front_pair_gap_m": layout["front_spacing_m"] - 2 * radius,
        "rear_pair_gap_m": layout["rear_spacing_m"] - 2 * radius,
        "cross_row_sphere_gap_m": cross_distance - 2 * envelope["bounding_sphere_radius_m"],
        "front_body_lateral_gap_m": layout["front_spacing_m"] / 2 - radius - assumptions["fuselage_half_width_m"],
        "rear_boom_lateral_gap_m": layout["rear_spacing_m"] / 2 - radius - assumptions["boom_half_width_m"],
        "surface_vertical_lower_bound_m": assumptions["hinge_height_m"] - assumptions["surface_thickness_m"] / 2,
        "rear_disc_main_wing_x_gap_m": layout["rear_x_m"] - envelope["bounding_sphere_radius_m"] - chord,
        "front_disc_tail_x_gap_m": layout["rear_x_m"] + assumptions["tail_leading_edge_offset_m"]
                                  - layout["front_x_m"] - radius,
    }
    body_distance = math.sqrt(
        max(assumptions["fuselage_forward_x_m"] - layout["rear_x_m"],
            layout["rear_x_m"] - assumptions["fuselage_aft_x_m"], 0) ** 2
        + max(layout["rear_spacing_m"] / 2 - assumptions["fuselage_half_width_m"], 0) ** 2
        + max(assumptions["hinge_height_m"] - assumptions["fuselage_half_height_m"], 0) ** 2)
    clearances["rear_body_sphere_gap_m"] = body_distance - envelope["bounding_sphere_radius_m"]
    # At x >= a surface LE aft of its hinge, u >= 0, so z >= hinge height.
    surface_proof_applies = layout["front_x_m"] <= 0 and assumptions["tail_leading_edge_offset_m"] >= 0
    screened = surface_proof_applies and all(value >= gap for value in clearances.values())
    result = {
        "layout": layout["id"], "name": layout["name"], "mass_kg": mass,
        "row_separation_m": layout["rear_x_m"] - layout["front_x_m"],
        "rear_spacing_m": layout["rear_spacing_m"],
        "wing_and_prop_width_m": max(math.sqrt(config["wing_area_m2"] * config["aspect_ratio"]),
                                     layout["front_spacing_m"] + 2 * radius,
                                     layout["rear_spacing_m"] + 2 * radius, layout["tail_span_m"]),
        "disc_sweep_screen_met": screened, "reference_cg_x_m": reference_cg,
        "required_battery_x_m": required_battery,
        "battery_reference_reachable": assumptions["battery_min_x_m"] <= required_battery <= assumptions["battery_max_x_m"],
        "cg_min_x_m": cg_at(assumptions["battery_min_x_m"]),
        "cg_max_x_m": cg_at(assumptions["battery_max_x_m"]),
        "equal_load_cg_x_m": (layout["front_x_m"] + layout["rear_x_m"]) / 2,
        "front_thrust_fraction": balance["front_fraction"],
        "front_each_n": balance["front_each_n"], "rear_each_n": balance["rear_each_n"],
        "electrical_hover_power_w": power, "extra_hover_power_w": power - equal_power,
        "front_support_offset_m": -layout["front_x_m"],
        "front_support_thrust_moment_nm": balance["front_each_n"] * -layout["front_x_m"],
        "tail_half_thrust_moment_nm": balance["rear_each_n"] * layout["rear_spacing_m"] / 2,
        "boom_rear_thrust_moment_nm": 2 * balance["rear_each_n"] * (layout["rear_x_m"] - chord),
    }
    return result, clearances, other, battery_mass
