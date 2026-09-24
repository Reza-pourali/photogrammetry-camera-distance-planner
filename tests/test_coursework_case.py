import unittest

from src.distance_planner import (
    CameraParameters,
    ConstraintParameters,
    ObjectGeometry,
    analyze_distance_range,
)


class TestCourseworkCase(unittest.TestCase):
    def setUp(self):
        self.camera = CameraParameters(
            focal_length_mm=4.8933,
            sensor_width_mm=6.4736,
            sensor_height_mm=4.8608,
            image_width_px=9248,
            image_height_px=6944,
        )
        self.object_geometry = ObjectGeometry(
            width_mm=162.0,
            height_mm=52.0,
        )
        self.constraints = ConstraintParameters(
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

    def test_reproduces_original_coursework_values(self):
        result = analyze_distance_range(
            self.camera,
            self.object_geometry,
            self.constraints,
        )

        self.assertAlmostEqual(result.resolution_upper_mm, 36350.22857142857, places=6)
        self.assertAlmostEqual(result.fov_coursework_upper_mm, 190.3096728970784, places=6)
        self.assertAlmostEqual(result.scale_upper_mm, 8495423.798125578, places=6)
        self.assertAlmostEqual(result.workspace_upper_mm, 190.3096728970784, places=6)
        self.assertAlmostEqual(result.dof_lower_mm, 179.25257328454614, places=6)
        self.assertAlmostEqual(result.points_lower_mm, 40.31482408802683, places=6)
        self.assertAlmostEqual(result.final_min_m, 0.17925257328454614, places=9)
        self.assertAlmostEqual(result.final_max_m, 0.1903096728970784, places=9)
        self.assertTrue(result.feasible)

    def test_invalid_focal_length_is_rejected(self):
        bad_camera = CameraParameters(
            focal_length_mm=0.0,
            sensor_width_mm=6.4736,
            sensor_height_mm=4.8608,
            image_width_px=9248,
            image_height_px=6944,
        )
        with self.assertRaises(ValueError):
            analyze_distance_range(
                bad_camera,
                self.object_geometry,
                self.constraints,
            )


if __name__ == "__main__":
    unittest.main()
