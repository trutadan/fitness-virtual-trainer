import unittest
import numpy as np

from constants import BLAZE_POSE_LANDMARKS
from pose_correction.PoseAnalyzer import PoseAnalyzer


class TestPoseAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = PoseAnalyzer()

    @staticmethod
    def generate_landmarks(**kwargs):
        """
        Generate a list of 33 landmarks with provided coordinates for specific key points.

        :param kwargs: Key points with their coordinates.

        :return: List of 33 tuples representing the landmarks.
        """
        landmarks = [(0, 0, 0)] * 33
        for key, value in kwargs.items():
            index = BLAZE_POSE_LANDMARKS[key]
            landmarks[index] = value
        return landmarks

    def test_compute_angle_between_points(self):
        a = (1, 0)
        b = (0, 0)
        c = (0, 1)
        expected_angle = 90
        computed_angle = self.analyzer.compute_angle_between_points(a, b, c)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_calculate_vertical_orientation_angle(self):
        upper_point = (0, 1)
        lower_point = (0, 0)
        expected_angle = 0
        computed_angle = self.analyzer.calculate_vertical_orientation_angle(upper_point, lower_point)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_normal_vector(self):
        p1 = (0, 0, 0)
        p2 = (1, 0, 0)
        p3 = (0, 1, 0)
        expected_normal = np.array([0, 0, 1])
        computed_normal = self.analyzer.compute_normal_vector(p1, p2, p3)
        np.testing.assert_array_almost_equal(computed_normal, expected_normal, decimal=2)

    def test_compute_eccentric_concentric_ratio(self):
        eccentric_frames = [1, 2, 3, 4, 5]
        concentric_frames = [6, 7, 8]
        expected_ratio = 5 / 3
        computed_ratio = self.analyzer.compute_eccentric_concentric_ratio(eccentric_frames, concentric_frames)
        self.assertAlmostEqual(computed_ratio, expected_ratio, places=2)

    def test_compute_right_hip_knee_ankle_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'right hip': (0, 0, 0),
                'right knee': (1, 0, 0),
                'right ankle': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_right_hip_knee_ankle_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_left_hip_knee_ankle_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'left hip': (0, 0, 0),
                'left knee': (1, 0, 0),
                'left ankle': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_left_hip_knee_ankle_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_right_shoulder_hip_knee_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'right shoulder': (0, 0, 0),
                'right hip': (1, 0, 0),
                'right knee': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_right_shoulder_hip_knee_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_left_shoulder_hip_knee_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'left shoulder': (0, 0, 0),
                'left hip': (1, 0, 0),
                'left knee': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_left_shoulder_hip_knee_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_right_shoulder_elbow_wrist_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'right shoulder': (0, 0, 0),
                'right elbow': (1, 0, 0),
                'right wrist': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_right_shoulder_elbow_wrist_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_left_shoulder_elbow_wrist_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'left shoulder': (0, 0, 0),
                'left elbow': (1, 0, 0),
                'left wrist': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_left_shoulder_elbow_wrist_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_left_elbow_wrist_index_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'left elbow': (0, 0, 0),
                'left wrist': (1, 0, 0),
                'left index': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_left_elbow_wrist_index_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_right_elbow_wrist_index_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'right elbow': (0, 0, 0),
                'right wrist': (1, 0, 0),
                'right index': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_right_elbow_wrist_index_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_left_hip_shoulder_elbow_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'left hip': (0, 0, 0),
                'left shoulder': (1, 0, 0),
                'left elbow': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_left_hip_shoulder_elbow_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_right_hip_shoulder_elbow_angle(self):
        landmarks = self.generate_landmarks(
            **{
                'right hip': (0, 0, 0),
                'right shoulder': (1, 0, 0),
                'right elbow': (1, 1, 0)
            }
        )
        expected_angle = 90
        computed_angle = self.analyzer.compute_right_hip_shoulder_elbow_angle(landmarks)
        self.assertAlmostEqual(computed_angle, expected_angle, places=2)

    def test_compute_right_foot_knee_alignment(self):
        landmarks = self.generate_landmarks(
            **{
                'right hip': (0, 1, 0),
                'right knee': (0, 0, 0),
                'right ankle': (0, -1, 0),
                'right foot index': (0, -2, 0)
            }
        )
        alignment = abs(self.analyzer.compute_right_foot_knee_alignment(landmarks))
        self.assertAlmostEqual(alignment, 1, places=2)

    def test_compute_left_foot_knee_alignment(self):
        landmarks = self.generate_landmarks(
            **{
                'left hip': (0, 1, 0),
                'left knee': (0, 0, 0),
                'left ankle': (0, -1, 0),
                'left foot index': (0, -2, 0)
            }
        )
        alignment = abs(self.analyzer.compute_left_foot_knee_alignment(landmarks))
        self.assertAlmostEqual(alignment, 1, places=2)