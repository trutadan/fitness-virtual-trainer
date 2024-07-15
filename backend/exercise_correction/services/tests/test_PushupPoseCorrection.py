import unittest

from constants import BLAZE_POSE_LANDMARKS
from pose_correction.PoseAnalyzer import PoseAnalyzer
from pose_correction.PushUpPoseCorrection import PushUpPoseCorrection


class TestPushUpPoseCorrection(unittest.TestCase):
    def setUp(self):
        self.pose_analyzer = PoseAnalyzer(key_points_dictionary=BLAZE_POSE_LANDMARKS)
        self.landmarks_dictionary = {
            0: [(0, 0, 0)] * 33,
            1: [(1, 1, 1)] * 33,
            2: [(2, 2, 2)] * 33,
        }
        self.angles = {
            'right_shoulder_elbow_wrist': {0: 120, 1: 110, 2: 100},
            'right_elbow_wrist_index': {0: 110, 1: 105, 2: 100},
            'right_hip_shoulder_elbow': {0: 50, 1: 55, 2: 60},
            'right_shoulder_hip_knee': {0: 175, 1: 165, 2: 160},
        }
        self.pushup_correction = PushUpPoseCorrection()

    def test_process_video(self):
        correction_advice = self.pushup_correction.process_video('videos/pushup.mp4')
        expected_output = {
            'push_up_depth': ("Bad range of motion, lower yourself further.", 3),
            'hand_position': ("Good hand position!", 1),
            'body_alignment': ("Bad body alignment, maintain a straight line from head to heels.", 3),
            'elbow_position': ("Perfect elbow position!", 1),
            'eccentric_concentric_ratio': ("Your movement is controlled, great job!", 1)
        }

        self.assertEqual(correction_advice, expected_output)

    def test_get_correction_advice(self):
        landmarks = self.landmarks_dictionary
        angles = self.angles
        advice = self.pushup_correction._get_correction_advice(landmarks, angles)
        self.assertIn('push_up_depth', advice)
        self.assertIn('hand_position', advice)
        self.assertIn('body_alignment', advice)
        self.assertIn('elbow_position', advice)
        self.assertIn('eccentric_concentric_ratio', advice)

    def test_hand_position(self):
        result = self.pushup_correction.hand_position(95)
        self.assertEqual(result, ("Good hand position!", 1))

        result = self.pushup_correction.hand_position(145)
        self.assertEqual(result, ("Good hand position!", 1))

        result = self.pushup_correction.hand_position(120)
        self.assertEqual(result, ("Bad hand position, please adjust your hands.", 3))

    def test_body_alignment(self):
        result = self.pushup_correction.body_alignment(160)
        self.assertEqual(result, ("Good body alignment!", 1))

        result = self.pushup_correction.body_alignment(130)
        self.assertEqual(result, ("Bad body alignment, maintain a straight line from head to heels.", 3))

    def test_elbow_position(self):
        result = self.pushup_correction.elbow_position(50)
        self.assertEqual(result, ("Perfect elbow position!", 1))

        result = self.pushup_correction.elbow_position(40)
        self.assertEqual(result, ("Bad elbow position, keep your elbows closer to your body.", 3))

        result = self.pushup_correction.elbow_position(70)
        self.assertEqual(result, ("Bad elbow position, keep your elbows closer to your body.", 3))

    def test_range_of_motion(self):
        result = self.pushup_correction.push_up_depth(85)
        self.assertEqual(result, ("Perfect range of motion!", 1))

        result = self.pushup_correction.push_up_depth(95)
        self.assertEqual(result, ("Good range of motion, but could be better.", 2))

        result = self.pushup_correction.push_up_depth(125)
        self.assertEqual(result, ("Bad range of motion, lower yourself further.", 3))

    def test_eccentric_concentric_ratio(self):
        angles = {i: angle for i, angle in enumerate([140, 135, 120, 115, 113, 111, 110, 114, 134, 140])}
        result = self.pushup_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("Your movement is controlled, great job!", 1))

        angles = {i: angle for i, angle in enumerate([140, 135, 120, 115, 113, 112, 111, 110, 114, 123, 134, 140])}
        result = self.pushup_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("Your movement pace is good, but try to slow down the lowering phase.", 2))

        angles = {i: angle for i, angle in enumerate([160, 155, 150, 145, 140, 145, 150, 155, 160])}
        result = self.pushup_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("You need to also control the descent movement, aim for a slower eccentric phase.", 3))


if __name__ == "__main__":
    unittest.main()
