import mediapipe as mp

from mediapipe.framework.formats import landmark_pb2

from pose_visualizer.PoseVisualizer import PoseVisualizer
from constants import BLAZE_POSE_LANDMARKS


class SquatPoseVisualizer(PoseVisualizer):
    def __init__(self, video_path, landmarks_dictionary):
        super().__init__(video_path, landmarks_dictionary, BLAZE_POSE_LANDMARKS)

    def draw_skeleton(self, image, landmarks: dict) -> None:
        """
        Draws the pose skeleton on the image.

        :param image: The image to draw on.
        :param landmarks: The landmarks' dictionary.
        """
        # load the MediaPipe pose drawing module
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose

        # convert list of tuples to LandmarkList
        landmark_list = landmark_pb2.NormalizedLandmarkList()
        for lm in landmarks:
            landmark = landmark_list.landmark.add()
            landmark.x, landmark.y, landmark.z, landmark.visibility = lm

        # draw the landmarks on the image
        mp_drawing.draw_landmarks(
            image,
            landmark_list,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
        )

    def draw_angles(self, image, landmarks: dict) -> None:
        """
        Draws the angles between the key points on the image.

        :param image: The image to draw on.
        :param landmarks: The landmarks' dictionary.
        """
        self.draw_angle_between_points(image, landmarks[self._key_points_dictionary['left hip']], landmarks[self._key_points_dictionary['left knee']], landmarks[self._key_points_dictionary['left ankle']])
        self.draw_angle_between_points(image, landmarks[self._key_points_dictionary['right hip']], landmarks[self._key_points_dictionary['right knee']], landmarks[self._key_points_dictionary['right ankle']])
        self.draw_angle_between_points(image, landmarks[self._key_points_dictionary['left shoulder']], landmarks[self._key_points_dictionary['left hip']], landmarks[self._key_points_dictionary['left knee']])
        self.draw_angle_between_points(image, landmarks[self._key_points_dictionary['right shoulder']], landmarks[self._key_points_dictionary['right hip']], landmarks[self._key_points_dictionary['right knee']])
