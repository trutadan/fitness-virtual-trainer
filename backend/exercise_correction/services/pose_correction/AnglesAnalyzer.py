import pickle
import uuid

import cv2
import numpy as np

from typing import List, Tuple, Dict

from .PoseAnalyzer import PoseAnalyzer


class AnglesAnalyzer:
    def __init__(self, landmarks_dictionary: dict, pose_analyzer: PoseAnalyzer) -> None:
        self._landmarks_dictionary = landmarks_dictionary
        self._pose_analyzer = pose_analyzer
        self._angles = {}

    def get_angles(self) -> dict:
        return self._angles

    def compute_angles(self, angle_names: List[str]) -> None:
        """
        Computes angles for all frames and stores them.

        :param angle_names: List of angle names to compute.
        """
        # initialize the angles dictionary
        for angle_name in angle_names:
            self._angles[angle_name] = dict()

        # compute angles for all frames
        for frame, landmarks in self._landmarks_dictionary.items():
            for angle_name in angle_names:
                if hasattr(self._pose_analyzer, f'compute_{angle_name}_angle'):
                    angle_value = getattr(self._pose_analyzer, f'compute_{angle_name}_angle')(landmarks)
                    self._angles[angle_name][frame] = angle_value

    def compute_statistics(self) -> dict:
        """
        Computes statistics for all angles.

        :return: A dictionary containing statistics for each angle.
        """
        statistics = {}
        for angle_name, angle_values in self._angles.items():
            angle_array = np.array(list(angle_values.values()))
            statistics[angle_name] = {
                'mean': np.mean(angle_array),
                'std': np.std(angle_array),
                'min': np.min(angle_array),
                'max': np.max(angle_array),
            }
        return statistics

    def save_angles(self, filepath: str) -> None:
        """
        Saves the computed angles to a pickle file.

        :param filepath: Path to the file where angles should be saved.
        """
        with open(filepath, 'wb') as file:
            pickle.dump(self._angles, file)

    def load_angles(self, filepath: str) -> None:
        """
        Loads the angles from a pickle file.

        :param filepath: Path to the file from which angles should be loaded.
        """
        with open(filepath, 'rb') as file:
            self._angles = pickle.load(file)

    @staticmethod
    def get_repetition_split_frames(flexion_angles: Dict[int, float], angle_threshold: float,
                                    error_threshold: float = 15,
                                    change_threshold: float = 20) -> List[int]:
        """
        Identifies the frames where repetitions start and end based on the specified angle threshold.

        :param flexion_angles: Dictionary with frame numbers as keys and flexion angles as values.
        :param angle_threshold: Angle threshold to identify the start and end of repetitions.
        :param error_threshold: Angle threshold to ignore when identifying repetitions.
        :param change_threshold: Maximum allowed change between consecutive angles to consider valid.

        :return: List of frame numbers where repetitions start and end.
        """
        # initialize variables
        in_repetition = False
        sequences = []
        current_sequence = []

        # sort the frames by frame number
        sorted_frames = sorted(flexion_angles.keys())

        previous_angle = None

        for frame in sorted_frames:
            angle = flexion_angles[frame]

            # ignore angles smaller than error_threshold
            if angle < error_threshold:
                continue

            # ignore sudden large changes
            if previous_angle is not None and abs(angle - previous_angle) > change_threshold:
                continue

            previous_angle = angle

            # check if the angle is below the threshold
            if angle < angle_threshold:
                # check if we are already in a repetition
                if not in_repetition:
                    in_repetition = True
                # add the frame to the current sequence
                current_sequence.append(frame)
            # check if the angle is above the threshold
            elif in_repetition and angle >= angle_threshold:
                # check if we are in a repetition
                if current_sequence:
                    # add the current sequence to the list of sequences
                    sequences.append(current_sequence)
                    current_sequence = []
                # set the repetition flag to False
                in_repetition = False

        # add the last sequence if it exists
        if current_sequence:
            sequences.append(current_sequence)

        # get the maximum angle frame between each sequence
        repetition_indices = []
        for j in range(len(sequences) - 1):
            start = sequences[j][-1] + 1
            end = sequences[j + 1][0]
            valid_frames = [frame for frame in range(start, end) if frame in flexion_angles]
            if valid_frames:
                max_angle_frame = max(valid_frames, key=flexion_angles.get)
                repetition_indices.append(max_angle_frame)

        return repetition_indices

    @staticmethod
    def split_video_into_repetitions(video_path: str, split_frames: list) -> list:
        """
        Splits video into segments of videos based on the specified split frames indicating repetitions and saves them.

        :param video_path: The path to the video file.
        :param split_frames: List of frames where the video should be split into repetitions.
        """
        # open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise FileNotFoundError("Could not open video file.")

        # get video properties
        frame_rate = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # prepare to collect segments
        video_names = []
        start_frame = 0

        # add end frame
        split_frames.append(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)

        # loop through the frames and split the video
        current_segment = 1
        for end_frame in split_frames:
            video_name = f'./media/processed_videos/s{uuid.uuid4().hex}.mp4'
            out = cv2.VideoWriter(video_name, fourcc, frame_rate, (width, height))

            # move to start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            for _ in range(start_frame, end_frame + 1):
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)

            out.release()
            video_names.append(video_name)
            current_segment += 1

            # next segment starts at the end of the previous
            start_frame = end_frame - 1

        cap.release()

        return video_names

    @staticmethod
    def get_valid_repetition_frames(data_frames: List[int], repetition_frames: List[int]) -> List[int]:
        """
        Ensures repetition frames are within the valid range of frames and adds the first and last frame if not present.

        :param data_frames: List of data frame numbers.
        :param repetition_frames: List of frames where each repetition ends.

        :return: Sorted list of valid repetition frames.
        """
        if len(data_frames) == 0:
            return []

        valid_repetition_frames = sorted(
            [frame for frame in repetition_frames if data_frames[0] <= frame <= data_frames[-1]])

        if data_frames[0] not in valid_repetition_frames:
            valid_repetition_frames.insert(0, data_frames[0])
        if data_frames[-1] not in valid_repetition_frames:
            valid_repetition_frames.append(data_frames[-1])

        return valid_repetition_frames

    @staticmethod
    def split_data_into_segments(data: Dict[int, any], repetition_frames: List[int]) -> List[Dict[int, any]]:
        """
        Splits the data into segments based on repetition frame indices.

        :param data: Dictionary with frame numbers as keys and data values as values.
        :param repetition_frames: List of frames where each repetition ends.

        :return: List of dictionaries, each representing a segment of the original data.
        """
        data_frames = sorted(data.keys())
        valid_repetition_frames = AnglesAnalyzer.get_valid_repetition_frames(data_frames, repetition_frames)

        segments = []
        for i in range(len(valid_repetition_frames) - 1):
            start = valid_repetition_frames[i]
            end = valid_repetition_frames[i + 1]
            segment = {frame: value for frame, value in data.items() if start <= frame <= end}
            segments.append(segment)

        return segments

    @staticmethod
    def split_angles_data_into_repetitions(angle_data: Dict[str, Dict[int, float]], repetition_frames: List[int]) -> \
            List[Dict[str, Dict[int, float]]]:
        """
        Splits angle data for each type into segments based on repetition frame indices.

        :param angle_data: Dictionary with angle types as keys and dictionaries of frame numbers and angle values as values.
        :param repetition_frames: List of frames where each repetition ends; adjustments made for overlaps.

        :return: List of dictionaries, each representing a segment of the original angle data.
        """
        angle_segments = []
        for angle_type, angles in angle_data.items():
            segments = AnglesAnalyzer.split_data_into_segments(angles, repetition_frames)
            for i, segment in enumerate(segments):
                if len(angle_segments) <= i:
                    angle_segments.append({})
                angle_segments[i][angle_type] = segment

        return angle_segments

    @staticmethod
    def split_landmarks_data_into_repetitions(frame_data: Dict[int, any], repetition_frames: List[int]) -> List[
                                                                                                        Dict[int, any]]:
        """
        Splits the frame data into segments based on repetition frame indices, with one frame overlap at each end.

        :param frame_data: Dictionary with frame numbers as keys and list of keypoints as values.
        :param repetition_frames: List of frames where each repetition ends; adjustments made for overlaps.

        :return: List of dictionaries, each representing a segment of the original data.
        """
        return AnglesAnalyzer.split_data_into_segments(frame_data, repetition_frames)

    @staticmethod
    def get_frames_under_tension(angles: Dict[int, float], angle_threshold: float) -> List[int]:
        """
        Returns the frame numbers where angles are below the specified threshold.

        :param angles: Dictionary with frame numbers as keys and angles as values.
        :param angle_threshold: Angle threshold.

        :return: List of frame numbers under tension.
        """
        return [frame for frame, angle in angles.items() if angle < angle_threshold]

    @staticmethod
    def get_eccentric_and_concentric_frames(angles: dict, angle_threshold: float) -> Tuple[List[int], List[int]]:
        """
        Identify eccentric and concentric frames based on the minimum angle within the frames under tension.

        :param angles: Dictionary with frame numbers as keys and angles as values.
        :param angle_threshold: Threshold to identify frames under tension.

        :return: A tuple containing two lists:
            - The first list contains frame numbers of eccentric frames.
            - The second list contains frame numbers of concentric frames.
        """
        # get the frames under tension
        frames_under_tension = AnglesAnalyzer.get_frames_under_tension(angles, angle_threshold)
        if not frames_under_tension:
            # if no frames are under tension
            return [], []

        # get the frame with the minimum angle within the tension frames
        min_angle_frame = min(frames_under_tension, key=lambda frame: angles[frame])

        # eccentric frames are those before the minimum angle frame
        eccentric_frames = [frame for frame in frames_under_tension if frame < min_angle_frame]

        # concentric frames are those after the minimum angle frame
        concentric_frames = [frame for frame in frames_under_tension if frame > min_angle_frame]

        return eccentric_frames, concentric_frames
