"""Scalar engineering equations. See docs/calculations.md for derivations."""

import math


def positive(name, value):
    """Reject missing, non-finite, or non-positive physical inputs."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")


def non_negative(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number.")
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and at least zero.")


def fraction(name, value):
    positive(name, value)
    if value > 1:
        raise ValueError(f"{name} must be at most one.")


def weight_n(mass_kg, gravity_m_s2):
    positive("mass_kg", mass_kg)
    positive("gravity_m_s2", gravity_m_s2)
    return mass_kg * gravity_m_s2


def rotor_disk_area_m2(rotor_count, diameter_m):
    if isinstance(rotor_count, bool) or not isinstance(rotor_count, int):
        raise ValueError("rotor_count must be a positive integer.")
    positive("rotor_count", rotor_count)
    positive("diameter_m", diameter_m)
    return rotor_count * math.pi * (diameter_m / 2) ** 2


def ideal_hover_power_w(thrust_n, air_density_kg_m3, disk_area_m2):
    positive("thrust_n", thrust_n)
    positive("air_density_kg_m3", air_density_kg_m3)
    positive("disk_area_m2", disk_area_m2)
    induced_speed_m_s = math.sqrt(thrust_n / (2 * air_density_kg_m3 * disk_area_m2))
    return thrust_n * induced_speed_m_s


def electrical_hover_power_w(ideal_power_w, figure_of_merit, motor_efficiency,
                             auxiliary_power_w):
    positive("ideal_power_w", ideal_power_w)
    fraction("figure_of_merit", figure_of_merit)
    fraction("motor_efficiency", motor_efficiency)
    non_negative("auxiliary_power_w", auxiliary_power_w)
    return ideal_power_w / (figure_of_merit * motor_efficiency) + auxiliary_power_w


def stall_speed_m_s(weight, air_density_kg_m3, wing_area_m2, maximum_lift_coefficient):
    positive("weight_n", weight)
    positive("air_density_kg_m3", air_density_kg_m3)
    positive("wing_area_m2", wing_area_m2)
    positive("maximum_lift_coefficient", maximum_lift_coefficient)
    return math.sqrt(2 * weight / (air_density_kg_m3 * wing_area_m2
                                  * maximum_lift_coefficient))


def cruise_drag_n(weight, speed_m_s, air_density_kg_m3, wing_area_m2,
                  aspect_ratio, oswald_efficiency, zero_lift_drag_coefficient,
                  maximum_lift_coefficient):
    positive("speed_m_s", speed_m_s)
    positive("aspect_ratio", aspect_ratio)
    fraction("oswald_efficiency", oswald_efficiency)
    non_negative("zero_lift_drag_coefficient", zero_lift_drag_coefficient)
    stall_speed = stall_speed_m_s(weight, air_density_kg_m3, wing_area_m2,
                                 maximum_lift_coefficient)
    if speed_m_s <= stall_speed:
        raise ValueError("Cruise speed must exceed the model's stall speed.")

    dynamic_pressure_pa = 0.5 * air_density_kg_m3 * speed_m_s ** 2
    lift_coefficient = weight / (dynamic_pressure_pa * wing_area_m2)
    induced_drag_coefficient = lift_coefficient ** 2 / (math.pi * aspect_ratio
                                                       * oswald_efficiency)
    drag_coefficient = zero_lift_drag_coefficient + induced_drag_coefficient
    return dynamic_pressure_pa * wing_area_m2 * drag_coefficient


def electrical_cruise_power_w(drag_n, speed_m_s, propeller_efficiency,
                              motor_efficiency, auxiliary_power_w):
    positive("drag_n", drag_n)
    positive("speed_m_s", speed_m_s)
    fraction("propeller_efficiency", propeller_efficiency)
    fraction("motor_efficiency", motor_efficiency)
    non_negative("auxiliary_power_w", auxiliary_power_w)
    return drag_n * speed_m_s / (propeller_efficiency * motor_efficiency) + auxiliary_power_w


def usable_battery_energy_wh(voltage_v, capacity_ah, usable_fraction):
    positive("voltage_v", voltage_v)
    positive("capacity_ah", capacity_ah)
    fraction("usable_fraction", usable_fraction)
    return voltage_v * capacity_ah * usable_fraction


def segment_energy_wh(power_w, duration_s):
    non_negative("power_w", power_w)
    non_negative("duration_s", duration_s)
    return power_w * duration_s / 3600
