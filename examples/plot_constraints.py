"""Create a compact visualization of the coursework constraint values."""

from pathlib import Path
import sys
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.distance_planner import (
    CameraParameters,
    ConstraintParameters,
    ObjectGeometry,
    analyze_distance_range,
)


camera = CameraParameters(
    focal_length_mm=4.8933,
    sensor_width_mm=6.4736,
    sensor_height_mm=4.8608,
    image_width_px=9248,
    image_height_px=6944,
)
obj = ObjectGeometry(width_mm=162.0, height_mm=52.0)
result = analyze_distance_range(camera, obj, ConstraintParameters())

labels = [
    "DOF lower",
    "Points lower",
    "FOV upper",
    "Resolution upper",
]
values_m = [
    result.dof_lower_mm / 1000.0,
    result.points_lower_mm / 1000.0,
    result.fov_coursework_upper_mm / 1000.0,
    result.resolution_upper_mm / 1000.0,
]

fig, ax = plt.subplots(figsize=(8, 4.8))
ax.bar(labels, values_m)
ax.set_yscale("log")
ax.set_ylabel("Distance (m, log scale)")
ax.set_title("Coursework Constraint Summary")
ax.axhline(result.final_min_m, linestyle="--", label="Final minimum")
ax.axhline(result.final_max_m, linestyle=":", label="Final maximum")
ax.legend()
fig.tight_layout()

output = Path(__file__).resolve().parents[1] / "figures" / "constraint_summary.png"
fig.savefig(output, dpi=180, bbox_inches="tight")
print(f"Saved: {output}")
