from ..landmarks_extractor.BlazePoseLandmarksExtractor import BlazePoseLandmarksExtractor
from ..pose_correction.AnglesAnalyzer import AnglesAnalyzer
from ..pose_correction.PoseAnalyzer import PoseAnalyzer


class PoseCorrection:
    def __init__(self) -> None:
        self._angle_names = list()
        self._segmentation_angle_name = None
        self._pose_analyzer = PoseAnalyzer()
        self._REPETITION_START_THRESHOLD = None
        self._ERROR_THRESHOLD = None
        self._CHANGE_THRESHOLD = None

    def process_video(self, video_path: str) -> dict:
        """
        Processes the video to extract landmarks, compute angles, and provide correction advice.

        :param video_path: Path to the video file.
        :return: A dictionary with correction advice for each repetition represented by a video segment.
        """
        # extract landmarks
        landmarks_extractor = BlazePoseLandmarksExtractor()
        landmarks_extractor.extract_landmarks_from_video(video_path)
        landmarks_dictionary = landmarks_extractor.get_landmarks_dictionary()

        processed_landmarks_dictionary = landmarks_extractor.process_keypoints(landmarks_dictionary)

        # compute angles and metrics
        angles_analyzer = AnglesAnalyzer(processed_landmarks_dictionary, self._pose_analyzer)

        angles_analyzer.compute_angles(self._angle_names)
        all_angles = angles_analyzer.get_angles()
        # print(all_angles)

        # get repetitions delimitation frames from video
        repetition_frames = angles_analyzer.get_repetition_split_frames(all_angles[self._segmentation_angle_name],
                                                                        self._REPETITION_START_THRESHOLD,
                                                                        self._ERROR_THRESHOLD,
                                                                        self._CHANGE_THRESHOLD)

        # split video into repetitions
        video_names = angles_analyzer.split_video_into_repetitions(video_path, repetition_frames)

        # split landmarks and angles into repetitions
        landmarks_on_repetitions = angles_analyzer.split_landmarks_data_into_repetitions(processed_landmarks_dictionary,
                                                                                         repetition_frames)
        angles_on_repetitions = angles_analyzer.split_angles_data_into_repetitions(all_angles, repetition_frames)

        # get correction advice for each repetition
        all_correction_advice = dict()
        for repetition in range(len(angles_on_repetitions)):
            if landmarks_on_repetitions[repetition] == [] or angles_on_repetitions[repetition] == []:
                continue

            correction_advice = self._get_correction_advice(landmarks_on_repetitions[repetition],
                                                            angles_on_repetitions[repetition])
            all_correction_advice[video_names[repetition]] = correction_advice

        return all_correction_advice

    def _get_correction_advice(self, landmarks: dict, angles: dict) -> dict:
        """
        Provides correction advice based on the given landmarks and angles.

        :param landmarks: A dictionary of body landmarks.
        :param angles: A dictionary of calculated angles between landmarks.

        :return: A dictionary with repetition videos, correction advice and their correction level.
        """
        pass
