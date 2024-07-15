import unittest
import numpy as np
from landmarks_extractor.BlazePoseLandmarksExtractor import BlazePoseLandmarksExtractor


class TestBlazePoseLandmarksExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = BlazePoseLandmarksExtractor()

    def test_filter_low_confidence_keypoints(self):
        data = {
            0: [(1, 2, 3, 0.4), (4, 5, 6, 0.6)],
            1: [(7, 8, 9, 0.3), (10, 11, 12, 0.7)]
        }
        expected_output = {
            0: [None, np.array([4, 5, 6])],
            1: [None, np.array([10, 11, 12])]
        }

        filtered_data = self.extractor.filter_low_confidence_keypoints(data, 0.5)

        self.assertEqual(len(filtered_data), len(expected_output))

        for frame in expected_output:
            for expected, actual in zip(expected_output[frame], filtered_data[frame]):
                if expected is None:
                    self.assertIsNone(actual)
                else:
                    np.testing.assert_array_equal(expected, actual)

    def test_interpolate_keypoints(self):
        data = {
            0: [np.array([1, 2, 3]), None],
            1: [np.array([4, 5, 6]), np.array([7, 8, 9])],
            2: [None, np.array([10, 11, 12])]
        }
        expected_output = {
            0: [np.array([1, 2, 3]), np.array([4, 5, 6])],
            1: [np.array([4, 5, 6]), np.array([7, 8, 9])],
            2: [np.array([7, 8, 9]), np.array([10, 11, 12])]
        }

        interpolated_data = self.extractor.interpolate_keypoints(data)

        self.assertEqual(len(interpolated_data), len(expected_output))

        for frame in expected_output:
            for expected, actual in zip(expected_output[frame], interpolated_data[frame]):
                if expected is None:
                    self.assertIsNone(actual)
                else:
                    np.testing.assert_array_equal(expected, actual)

    def test_convert_arrays_to_lists(self):
        data = {
            0: [np.array([1, 2, 3]), None],
            1: [np.array([4, 5, 6]), np.array([7, 8, 9])]
        }
        expected_output = {
            0: [[1, 2, 3], None],
            1: [[4, 5, 6], [7, 8, 9]]
        }

        list_converted_data = self.extractor.convert_arrays_to_lists(data)

        self.assertEqual(list_converted_data, expected_output)

    def test_process_keypoints(self):
        data = {
            0: [(1, 2, 3, 0.4), (4, 5, 6, 0.6)],
            1: [(7, 8, 9, 0.3), (10, 11, 12, 0.7)],
            2: [(13, 14, 15, 0.9), (25, 14, 1, 0.2)]
        }
        expected_output = {
            0: [[13, 14, 15], [4, 5, 6]],
            1: [[13, 14, 15], [10, 11, 12]],
            2: [[13, 14, 15], [16, 17, 18]]
        }

        processed_data = self.extractor.process_keypoints(data, 0.5)

        self.assertEqual(len(processed_data), len(expected_output))

        for frame in expected_output:
            for expected, actual in zip(expected_output[frame], processed_data[frame]):
                if expected is None:
                    self.assertIsNone(actual)
                else:
                    self.assertEqual(expected, actual)
