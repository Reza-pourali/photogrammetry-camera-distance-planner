"""Camera-to-object distance planning for close-range photogrammetry.

This module refactors the mathematical definitions used in the original
graduate coursework script into a reusable and testable API.

Important
---------
The constraint equations and their interpretation are intentionally preserved
from the original coursework model. They should be treated as a documented
coursework/design model rather than a universal camera-planning standard.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class CameraParameters:
    focal_length_mm: float
    sensor_width_mm: float
    sensor_height_mm: float
    image_width_px: int
    image_height_px: int


@dataclass(frozen=True)
class ObjectGeometry:
    width_mm: float
    height_mm: float


@dataclass(frozen=True)
class ConstraintParameters:
    f_stop: float = 2.8
    incidence_angle_deg: float = 90.0
    min_target_pixels: float = 10.0
    target_dimension_mm: float = 52.0
    repeated_images: float = 1.0
    network_strength: float = 0.7
    relative_measurement_error: float = 1.0
    image_measurement_precision_px: float = 0.2
    point_count_parameter: float = 20.0


@dataclass(frozen=True)
class DistancePlan:
    pixel_size_mm: float
    object_diameter_mm: float
    average_point_spacing_mm: float
    resolution_upper_mm: float
    fov_coursework_upper_mm: float
    scale_upper_mm: float
    workspace_upper_mm: float
    dof_lower_mm: float
    points_lower_mm: float
    final_min_mm: float
    final_max_mm: float

    @property
    def final_min_m(self) -> float:
        return self.final_min_mm / 1000.0

    @property
    def final_max_m(self) -> float:
        return self.final_max_mm / 1000.0

    @property
    def feasible(self) -> bool:
        return self.final_min_mm <= self.final_max_mm

    @property
    def limiting_lower_constraint(self) -> str:
        return "DOF" if self.dof_lower_mm >= self.points_lower_mm else "Points"

    @property
    def limiting_upper_constraint(self) -> str:
        values = {
            "Resolution": self.resolution_upper_mm,
            "Scale": self.scale_upper_mm,
            "FOV (coursework model)": self.fov_coursework_upper_mm,
            "Workspace": self.workspace_upper_mm,
        }
        return min(values, key=values.get)


def _positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive.")


def depth_of_field_lower_bound(
    focal_length_mm: float,
    f_stop: float,
    working_distance_mm: float,
) -> float:
    """Near-limit distance used by the original coursework DOF equation."""
    _positive("focal_length_mm", focal_length_mm)
    _positive("f_stop", f_stop)
    _positive("working_distance_mm", working_distance_mm)

    delta = focal_length_mm / 1720.0
    hyperfocal_term = (focal_length_mm ** 2) / (f_stop * delta)
    return working_distance_mm / (
        1.0 + (working_distance_mm - focal_length_mm) / hyperfocal_term
    )


def resolution_upper_bound(
    focal_length_mm: float,
    target_dimension_mm: float,
    incidence_angle_deg: float,
    pixel_size_mm: float,
    min_target_pixels: float,
) -> float:
    _positive("focal_length_mm", focal_length_mm)
    _positive("target_dimension_mm", target_dimension_mm)
    _positive("pixel_size_mm", pixel_size_mm)
    _positive("min_target_pixels", min_target_pixels)

    phi = math.radians(incidence_angle_deg)
    return (
        focal_length_mm
        * target_dimension_mm
        * math.sin(phi)
        / (pixel_size_mm * min_target_pixels)
    )


def fov_coursework_upper_bound(
    focal_length_mm: float,
    object_diameter_mm: float,
    minimum_frame_dimension_mm: float,
    incidence_angle_deg: float,
) -> float:
    """FOV bound exactly as defined and used in the original coursework."""
    _positive("focal_length_mm", focal_length_mm)
    _positive("object_diameter_mm", object_diameter_mm)
    _positive("minimum_frame_dimension_mm", minimum_frame_dimension_mm)

    phi = math.radians(incidence_angle_deg)
    alpha = math.atan(
        (0.9 * minimum_frame_dimension_mm) / (2.0 * focal_length_mm)
    )
    return (
        object_diameter_mm
        * math.sin(alpha + phi)
        / (2.0 * math.sin(alpha))
    )


def scale_upper_bound(
    object_diameter_mm: float,
    focal_length_mm: float,
    repeated_images: float,
    network_strength: float,
    relative_measurement_error: float,
    image_measurement_precision_mm: float,
) -> float:
    for name, value in [
        ("object_diameter_mm", object_diameter_mm),
        ("focal_length_mm", focal_length_mm),
        ("repeated_images", repeated_images),
        ("network_strength", network_strength),
        ("relative_measurement_error", relative_measurement_error),
        ("image_measurement_precision_mm", image_measurement_precision_mm),
    ]:
        _positive(name, value)

    return (
        object_diameter_mm
        * focal_length_mm
        * math.sqrt(repeated_images)
        / (
            network_strength
            * relative_measurement_error
            * image_measurement_precision_mm
        )
    )


def points_lower_bound(
    average_spacing_mm: float,
    focal_length_mm: float,
    point_count_parameter: float,
    frame_dimension_mm: float,
) -> float:
    for name, value in [
        ("average_spacing_mm", average_spacing_mm),
        ("focal_length_mm", focal_length_mm),
        ("point_count_parameter", point_count_parameter),
        ("frame_dimension_mm", frame_dimension_mm),
    ]:
        _positive(name, value)

    return (
        average_spacing_mm
        * focal_length_mm
        * math.sqrt(point_count_parameter)
        / frame_dimension_mm
    )


def analyze_distance_range(
    camera: CameraParameters,
    object_geometry: ObjectGeometry,
    constraints: ConstraintParameters = ConstraintParameters(),
) -> DistancePlan:
    """Evaluate all coursework constraints and return the final distance range."""

    for name, value in [
        ("focal_length_mm", camera.focal_length_mm),
        ("sensor_width_mm", camera.sensor_width_mm),
        ("sensor_height_mm", camera.sensor_height_mm),
        ("image_width_px", camera.image_width_px),
        ("image_height_px", camera.image_height_px),
        ("object_width_mm", object_geometry.width_mm),
        ("object_height_mm", object_geometry.height_mm),
    ]:
        _positive(name, float(value))

    if constraints.point_count_parameter <= 1:
        raise ValueError("point_count_parameter must be greater than 1.")

    # Preserved from the source script: horizontal pixel size is used.
    pixel_size_mm = camera.sensor_width_mm / camera.image_width_px

    object_diameter_mm = math.hypot(
        object_geometry.width_mm,
        object_geometry.height_mm,
    )
    min_frame_dimension_mm = min(
        camera.sensor_width_mm,
        camera.sensor_height_mm,
    )

    sigma_i_mm = (
        constraints.image_measurement_precision_px * pixel_size_mm
    )

    average_spacing_mm = object_diameter_mm / (
        constraints.point_count_parameter - 1.0
    )

    resolution_upper_mm = resolution_upper_bound(
        camera.focal_length_mm,
        constraints.target_dimension_mm,
        constraints.incidence_angle_deg,
        pixel_size_mm,
        constraints.min_target_pixels,
    )

    fov_upper_mm = fov_coursework_upper_bound(
        camera.focal_length_mm,
        object_diameter_mm,
        min_frame_dimension_mm,
        constraints.incidence_angle_deg,
    )

    scale_upper_mm = scale_upper_bound(
        object_diameter_mm,
        camera.focal_length_mm,
        constraints.repeated_images,
        constraints.network_strength,
        constraints.relative_measurement_error,
        sigma_i_mm,
    )

    workspace_upper_mm = min(fov_upper_mm, scale_upper_mm)

    dof_lower_mm = depth_of_field_lower_bound(
        camera.focal_length_mm,
        constraints.f_stop,
        workspace_upper_mm,
    )

    points_lower_mm = points_lower_bound(
        average_spacing_mm,
        camera.focal_length_mm,
        constraints.point_count_parameter,
        min_frame_dimension_mm,
    )

    final_min_mm = max(dof_lower_mm, points_lower_mm)
    final_max_mm = min(
        resolution_upper_mm,
        scale_upper_mm,
        fov_upper_mm,
        workspace_upper_mm,
    )

    return DistancePlan(
        pixel_size_mm=pixel_size_mm,
        object_diameter_mm=object_diameter_mm,
        average_point_spacing_mm=average_spacing_mm,
        resolution_upper_mm=resolution_upper_mm,
        fov_coursework_upper_mm=fov_upper_mm,
        scale_upper_mm=scale_upper_mm,
        workspace_upper_mm=workspace_upper_mm,
        dof_lower_mm=dof_lower_mm,
        points_lower_mm=points_lower_mm,
        final_min_mm=final_min_mm,
        final_max_mm=final_max_mm,
    )
