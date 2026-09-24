"""Reproduce the numerical case used in the original coursework script."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.distance_planner import (
    CameraParameters,
    ConstraintParameters,
    ObjectGeometry,
    analyze_distance_range,
)


def main() -> None:
    camera = CameraParameters(
        focal_length_mm=4.8933,
        sensor_width_mm=6.4736,
        sensor_height_mm=4.8608,
        image_width_px=9248,
        image_height_px=6944,
    )

    object_geometry = ObjectGeometry(
        width_mm=162.0,
        height_mm=52.0,
    )

    constraints = ConstraintParameters(
        f_stop=2.8,
        incidence_angle_deg=90.0,
        min_target_pixels=10.0,
        target_dimension_mm=52.0,
        repeated_images=1.0,
        network_strength=0.7,
        relative_measurement_error=1.0,
        image_measurement_precision_px=0.2,
        point_count_parameter=20.0,
    )

    result = analyze_distance_range(camera, object_geometry, constraints)

    print("Close-Range Photogrammetry Distance Plan")
    print("=" * 47)
    print(f"Pixel size                    : {result.pixel_size_mm:.7f} mm")
    print(f"Object diagonal               : {result.object_diameter_mm:.4f} mm")
    print()
    print("Individual constraints")
    print("-" * 47)
    print(f"Resolution upper bound        : {result.resolution_upper_mm / 1000:.4f} m")
    print(f"FOV coursework upper bound    : {result.fov_coursework_upper_mm / 1000:.4f} m")
    print(f"Scale upper bound             : {result.scale_upper_mm / 1000:.4f} m")
    print(f"Workspace upper bound         : {result.workspace_upper_mm / 1000:.4f} m")
    print(f"DOF lower bound               : {result.dof_lower_mm / 1000:.4f} m")
    print(f"Points lower bound            : {result.points_lower_mm / 1000:.4f} m")
    print()
    print("Final allowable range")
    print("-" * 47)
    print(f"{result.final_min_m:.4f} m <= D <= {result.final_max_m:.4f} m")
    print(f"Feasible                      : {result.feasible}")
    print(f"Limiting lower constraint     : {result.limiting_lower_constraint}")
    print(f"Limiting upper constraint     : {result.limiting_upper_constraint}")


if __name__ == "__main__":
    main()
