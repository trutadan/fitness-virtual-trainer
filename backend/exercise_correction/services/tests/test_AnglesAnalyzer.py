import unittest
import os

from pose_correction.PoseAnalyzer import PoseAnalyzer
from pose_correction.AnglesAnalyzer import AnglesAnalyzer


class TestAnglesAnalyzer(unittest.TestCase):
    def setUp(self):
        self.pose_analyzer = PoseAnalyzer()
        self.landmarks_dictionary = {
            0: [(0, 0, 0)] * 33,
            1: [(0, 0, 0)] * 33,
            2: [(0, 0, 0)] * 33,
        }
        self.analyzer = AnglesAnalyzer(self.landmarks_dictionary, self.pose_analyzer)

    def test_get_angles(self):
        self.assertEqual(self.analyzer.get_angles(), {})

    def test_compute_angles(self):
        angle_names = ['right_hip_knee_ankle', 'left_hip_knee_ankle']
        self.analyzer.compute_angles(angle_names)
        self.assertIn('right_hip_knee_ankle', self.analyzer.get_angles())
        self.assertIn('left_hip_knee_ankle', self.analyzer.get_angles())

    def test_compute_statistics(self):
        angle_names = ['right_hip_knee_ankle']
        self.analyzer.compute_angles(angle_names)
        stats = self.analyzer.compute_statistics()
        self.assertIn('right_hip_knee_ankle', stats)
        self.assertIn('mean', stats['right_hip_knee_ankle'])
        self.assertIn('std', stats['right_hip_knee_ankle'])
        self.assertIn('min', stats['right_hip_knee_ankle'])
        self.assertIn('max', stats['right_hip_knee_ankle'])

    def test_save_load_angles(self):
        angle_names = ['right_hip_knee_ankle']
        self.analyzer.compute_angles(angle_names)
        filepath = 'test_angles.pkl'
        self.analyzer.save_angles(filepath)
        self.analyzer._angles = {}
        self.analyzer.load_angles(filepath)
        self.assertIn('right_hip_knee_ankle', self.analyzer.get_angles())
        os.remove(filepath)

    def test_get_repetition_split_frames(self):
        flexion_angles = {i: angle for i, angle in enumerate([30, 25, 20, 15, 10, 15, 20, 25, 30, 27, 23, 20, 17, 21, 24])}
        angle_threshold = 20
        expected_frames = [8]
        computed_frames = self.analyzer.get_repetition_split_frames(flexion_angles, angle_threshold)
        self.assertEqual(computed_frames, expected_frames)

    def test_split_angles_data_into_repetitions(self):
        angle_data = {
            'right_hip_knee_ankle': {0: 10, 1: 20, 2: 30, 3: 40, 4: 50},
            'left_hip_knee_ankle': {0: 15, 1: 25, 2: 35, 3: 45, 4: 55}
        }
        repetition_frames = [2, 3, 4]
        expected_segments = [
            {
                'right_hip_knee_ankle': {0: 10, 1: 20, 2: 30},
                'left_hip_knee_ankle': {0: 15, 1: 25, 2: 35}
            },
            {
                'right_hip_knee_ankle': {2: 30, 3: 40},
                'left_hip_knee_ankle': {2: 35, 3: 45}
            },
            {
                'right_hip_knee_ankle': {3: 40, 4: 50},
                'left_hip_knee_ankle': {3: 45, 4: 55}
            }
        ]
        computed_segments = self.analyzer.split_angles_data_into_repetitions(angle_data, repetition_frames)
        self.assertEqual(computed_segments, expected_segments)

    def test_split_landmarks_data_into_repetitions(self):
        frame_data = {
            0: [(0, 0, 0)] * 33,
            1: [(1, 1, 1)] * 33,
            2: [(2, 2, 2)] * 33,
            3: [(3, 3, 3)] * 33
        }
        repetition_frames = [1, 3]
        expected_segments = [
            {
                0: [(0, 0, 0)] * 33,
                1: [(1, 1, 1)] * 33
            },
            {
                1: [(1, 1, 1)] * 33,
                2: [(2, 2, 2)] * 33,
                3: [(3, 3, 3)] * 33
            }
        ]
        computed_segments = self.analyzer.split_landmarks_data_into_repetitions(frame_data, repetition_frames)
        self.assertEqual(computed_segments, expected_segments)

    def test_get_frames_under_tension(self):
        angles = {i: angle for i, angle in enumerate([10, 15, 20, 25, 30])}
        angle_threshold = 20
        expected_frames = [0, 1]
        computed_frames = self.analyzer.get_frames_under_tension(angles, angle_threshold)
        self.assertEqual(computed_frames, expected_frames)

    def test_get_eccentric_and_concentric_frames(self):
        angles = {i: angle for i, angle in enumerate([30, 25, 20, 15, 14, 12, 10, 11, 14, 15, 20, 25, 30])}
        angle_threshold = 20
        expected_eccentric_frames = [3, 4, 5]
        expected_concentric_frames = [7, 8, 9]
        computed_eccentric_frames, computed_concentric_frames = self.analyzer.get_eccentric_and_concentric_frames(angles, angle_threshold)
        self.assertEqual(computed_eccentric_frames, expected_eccentric_frames)
        self.assertEqual(computed_concentric_frames, expected_concentric_frames)


if __name__ == "__main__":
    unittest.main()
