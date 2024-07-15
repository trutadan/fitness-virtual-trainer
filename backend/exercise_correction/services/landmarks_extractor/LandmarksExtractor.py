import pickle

from abc import ABC, abstractmethod


class LandmarksExtractor(ABC):
    def __init__(self) -> None:
        self._landmarks_dictionary = {}
        self._total_frames = 0

    def get_landmarks_dictionary(self) -> dict:
        return self._landmarks_dictionary

    def get_total_frames(self) -> int:
        return self._total_frames

    @abstractmethod
    def extract_landmarks_from_video(self, video_path: str) -> None:
        """
        Extracts landmarks from the video and stores them in a dictionary.

        :param video_path: Path to the video file.
        """
        pass

    def save_landmarks(self, file_path: str) -> None:
        """
        Saves the extracted landmarks to a pickle file.

        :param file_path: Path to the file where landmarks should be saved.
        """
        with open(file_path, 'wb') as file:
            pickle.dump(self._landmarks_dictionary, file)

    def load_landmarks(self, file_path: str) -> None:
        """
        Loads the landmarks from a pickle file.

        :param file_path: Path to the file from which landmarks should be loaded.
        """
        with open(file_path, 'rb') as file:
            self._landmarks_dictionary = pickle.load(file)
