import unittest

from constants import BLAZE_POSE_LANDMARKS
from pose_correction.PoseAnalyzer import PoseAnalyzer
from pose_correction.SquatPoseCorrection import SquatPoseCorrection


class TestSquatPoseCorrection(unittest.TestCase):
    def setUp(self):
        self.pose_analyzer = PoseAnalyzer(key_points_dictionary=BLAZE_POSE_LANDMARKS)
        self.landmarks_dictionary = {
            0: [(0, 0, 0)] * 33,
            1: [(1, 1, 1)] * 33,
            2: [(2, 2, 2)] * 33,
        }
        self.angles = {
            'right_hip_knee_ankle': [120, 110, 100],
            'right_shoulder_hip_knee': [130, 120, 110],
        }
        self.squat_correction = SquatPoseCorrection()

    def test_process_video(self):
        correction_advice = self.squat_correction.process_video('../videos/squat.mp4')
        expected_output = {
            'segment_1.mp4': {
                'squat_depth': ('You depth is good.', 1),
                'head_position': ('Your head position is good.', 1),
                'thoracic_position': ('Your thoracic position is good.', 1),
                'hip_position': ('Your hip position is good.', 1),
                'frontal_knee_position': ('Your knee position is good.', 1),
                'foot_position': ('Your foot position is good.', 1),
                'trunk_position': ('Your trunk is parallel to your tibia.', 1),
                'eccentric_concentric_ratio': ('Your movement is controlled, not dropping into the squat.', 1)
            }
        }

        self.assertEqual(correction_advice, expected_output)

    def test_squat_depth(self):
        result = self.squat_correction.squat_depth(95)
        self.assertEqual(result, ("You need to go deeper in depth.", 2))

        result = self.squat_correction.squat_depth(85)
        self.assertEqual(result, ("You depth is good.", 1))

        result = self.squat_correction.squat_depth(140)
        self.assertEqual(result, ("This is not considered a squat. You need to go deeper in depth.", 3))

    def test_thoracic_position(self):
        landmarks = self.landmarks_dictionary[0]
        result = self.squat_correction.thoracic_position(landmarks)
        self.assertTrue(result)

    def test_trunk_position(self):
        landmarks = self.landmarks_dictionary[0]
        result = self.squat_correction.trunk_position(landmarks)
        self.assertEqual(result, ("Your trunk is parallel to your tibia.", 1))

    def test_hip_position(self):
        landmarks = self.landmarks_dictionary[0]
        result = self.squat_correction.hip_position(landmarks)
        self.assertTrue(result)

    def test_frontal_knee_position(self):
        landmarks = self.landmarks_dictionary[0]
        result = self.squat_correction.frontal_knee_position(landmarks)
        self.assertFalse(result)

    def test_foot_position(self):
        previous_vertical_position = 0.0
        current_vertical_position = 0.02
        result = self.squat_correction.foot_position(previous_vertical_position, current_vertical_position)
        self.assertFalse(result)

    def test_eccentric_concentric_ratio(self):
        angles = {i: angle for i, angle in enumerate([130, 125, 123, 121, 120, 118, 116, 115, 110, 115, 120, 125, 130])}
        result = self.squat_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("Your movement is controlled, not dropping into the squat.", 1))
