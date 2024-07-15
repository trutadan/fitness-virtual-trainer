from typing import List

import cv2
import mediapipe as mp
import numpy as np
from scipy.interpolate import interp1d

from ..landmarks_extractor.LandmarksExtractor import LandmarksExtractor


class BlazePoseLandmarksExtractor(LandmarksExtractor):
    def __init__(self) -> None:
        super().__init__()
        self._pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def extract_landmarks_from_video(self, video_path: str) -> None:
        """
        Extracts pose landmarks from a video and stores them in a dictionary.

        :param video_path: Path to the video file.
        """
        self._landmarks_dictionary = dict()

        cap = cv2.VideoCapture(video_path)
        frame_index = 0

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break

            # convert the image to RGB as MediaPipe requires RGB images
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self._pose.process(image_rgb)

            # store the landmarks if pose landmarks are detected
            if results.pose_landmarks:
                landmarks = [(lm.x, lm.y, lm.z, lm.visibility) for lm in results.pose_landmarks.landmark]
                self._landmarks_dictionary[frame_index] = landmarks

            frame_index += 1

        self._total_frames = frame_index - 1

        cap.release()

    @staticmethod
    def extract_landmarks_from_image(image_path: str) -> List[tuple] or None:
        """
        Extracts pose landmarks from a single image.

        :param image_path: Path to the image file.

        :return: List of tuples containing the landmarks or None if no landmarks were found.
        """
        pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Error loading image.")

        # convert the image to RGB since MediaPipe requires RGB images
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = [(lm.x, lm.y, lm.z, lm.visibility) for lm in results.pose_landmarks.landmark]
            return landmarks
        else:
            return None

    @staticmethod
    def filter_low_confidence_keypoints(data, threshold=0.5):
        """
        Filters out low confidence keypoints from the data.

        :param data: Dictionary of keypoints.
        :param threshold: Confidence threshold for filtering.

        :return: Filtered dictionary of keypoints.
        """
        filtered_data = {}

        for frame, keypoints in data.items():
            filtered_keypoints = [
                np.array(values[:-1]) if values[-1] >= threshold else None for values in keypoints
            ]
            filtered_data[frame] = filtered_keypoints

        return filtered_data

    @staticmethod
    def interpolate_keypoints(data):
        """
        Interpolates missing keypoints in the data.

        :param data: Dictionary of keypoints.
        :return: Dictionary of keypoints with interpolated missing values.
        """
        # sort frames and get number of keypoints
        frames = sorted(data.keys())
        num_keypoints = len(data[frames[0]])

        # create dictionary to store interpolated data
        interpolated_data = {frame: [None] * num_keypoints for frame in frames}

        for i in range(num_keypoints):
            keypoint_values = []
            valid_frames = []

            # get valid frames and keypoint values for the current keypoint
            for frame in frames:
                keypoint = data[frame][i]
                if keypoint is not None:
                    keypoint_values.append(keypoint)
                    valid_frames.append(frame)

            # if there are more than one valid frames, interpolate missing values
            if len(valid_frames) > 1:
                # interpolate each dimension of the keypoint
                keypoint_values = np.array(keypoint_values)
                interpolated_keypoints = []

                for dim in range(keypoint_values.shape[1]):
                    dim_values = keypoint_values[:, dim]
                    interp_func = interp1d(valid_frames, dim_values, bounds_error=False, fill_value="extrapolate")
                    interpolated_keypoints.append(interp_func(frames))

                interpolated_keypoints = np.array(interpolated_keypoints).T

                # fill in the interpolated values
                for j, frame in enumerate(frames):
                    if data[frame][i] is None:
                        interpolated_data[frame][i] = interpolated_keypoints[j]
                    else:
                        interpolated_data[frame][i] = data[frame][i]
            elif len(valid_frames) == 1:
                # of there is only one valid frame, use its keypoint to fill in all frames
                for frame in frames:
                    interpolated_data[frame][i] = data[valid_frames[0]][i]
            else:
                # if no valid frames, set all to None
                for frame in frames:
                    interpolated_data[frame][i] = None

        return interpolated_data

    @staticmethod
    def convert_arrays_to_lists(data):
        """
        Converts numpy arrays in the keypoints data to lists.

        :param data: Dictionary of keypoints.

        :return: Dictionary of keypoints with lists instead of numpy arrays.
        """
        for frame, keypoints in data.items():
            for i in range(len(keypoints)):
                if keypoints[i] is not None:
                    keypoints[i] = keypoints[i].tolist()

        return data

    def process_keypoints(self, data, threshold=0.5):
        """
        Processes keypoints by filtering low confidence points, interpolating missing points,
        and converting arrays to lists.

        :param data: Dictionary of keypoints.
        :param threshold: Confidence threshold for filtering.

        :return: Processed dictionary of keypoints.
        """
        filtered_data = self.filter_low_confidence_keypoints(data, threshold)
        interpolated_data = self.interpolate_keypoints(filtered_data)
        list_converted_data = self.convert_arrays_to_lists(interpolated_data)

        return list_converted_data
