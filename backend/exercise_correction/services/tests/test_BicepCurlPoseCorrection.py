import unittest
from pose_correction.PoseAnalyzer import PoseAnalyzer
from pose_correction.BicepCurlPoseCorrection import BicepCurlPoseCorrection
from constants import BLAZE_POSE_LANDMARKS


class TestBicepCurlPoseCorrection(unittest.TestCase):
    def setUp(self):
        self.pose_analyzer = PoseAnalyzer(key_points_dictionary=BLAZE_POSE_LANDMARKS)
        self.landmarks_dictionary = {
            0: [(0, 0, 0)] * 33,
            1: [(1, 1, 1)] * 33,
            2: [(2, 2, 2)] * 33,
        }
        self.angles = {
            'right_shoulder_elbow_wrist': {0: 120, 1: 110, 2: 100},
            'right_elbow_wrist_index': {0: 90, 1: 80, 2: 70},
            'right_hip_shoulder_elbow': {0: 100, 1: 90, 2: 80},
            'right_shoulder_hip_knee': {0: 130, 1: 120, 2: 110},
        }
        self.curl_correction = BicepCurlPoseCorrection()

    def test_process_video(self):
        correction_advice = self.curl_correction.process_video('videos/curl.mp4')
        expected_output = {
            'curl_depth': ("Bad curl depth, please go deeper.", 3),
            'wrist_position': ("Good wrist position.", 1),
            'elbow_position': ("Perfect elbow position!", 1),
            'back_arching_momentum': ("Good back stability!", 1),
            'eccentric_concentric_ratio': ("Your movement is controlled, great job!", 1)
        }

        self.assertEqual(correction_advice, expected_output)

    def test_curl_depth(self):
        result = self.curl_correction.curl_depth(55)
        self.assertEqual(result, ("Perfect curl depth!", 1))

        result = self.curl_correction.curl_depth(65)
        self.assertEqual(result, ("Good curl depth, but could be better.", 2))

        result = self.curl_correction.curl_depth(140)
        self.assertEqual(result, ("Bad curl depth, please go deeper.", 3))

    def test_wrist_position(self):
        result = self.curl_correction.wrist_position(175)
        self.assertEqual(result, ("Good wrist position.", 1))

        result = self.curl_correction.wrist_position(185)
        self.assertEqual(result, ("Bad wrist position, please straighten your wrist.", 3))

    def test_elbow_position(self):
        result = self.curl_correction.elbow_position(10)
        self.assertEqual(result, ("Perfect elbow position!", 1))

        result = self.curl_correction.elbow_position(20)
        self.assertEqual(result, ("Good elbow position, but could be better.", 2))

        result = self.curl_correction.elbow_position(35)
        self.assertEqual(result, ("Bad elbow position, please keep your elbows closer to your body.", 3))

    def test_back_arching_momentum(self):
        result = self.curl_correction.back_arching_momentum(175)
        self.assertEqual(result, ("Good back stability!", 1))

        result = self.curl_correction.back_arching_momentum(165)
        self.assertEqual(result, ("Poor back stability, avoid arching your back.", 3))

    def test_eccentric_concentric_ratio(self):
        angles = {i: angle for i, angle in enumerate([130, 125, 119, 117, 115, 110, 113, 125, 130])}
        result = self.curl_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("Your movement is controlled, great job!", 1))

        angles = {i: angle for i, angle in enumerate([140, 135, 130, 125, 120, 116, 114, 112, 110, 113, 115, 125, 130])}
        result = self.curl_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("Your movement pace is good, but try to slow down the lowering phase.", 2))

        angles = {i: angle for i, angle in enumerate([150, 145, 140, 135, 130, 135, 140, 145, 150])}
        result = self.curl_correction.eccentric_concentric_ratio(angles)
        self.assertEqual(result, ("You need to also control the descent movement, aim for a slower eccentric phase.", 3))


if __name__ == "__main__":
    unittest.main()
