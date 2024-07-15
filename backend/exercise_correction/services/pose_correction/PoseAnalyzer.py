import numpy as np

from math import acos, degrees, atan2

from ..constants import BLAZE_POSE_LANDMARKS


class PoseAnalyzer:
    def __init__(self, key_points_dictionary: dict = BLAZE_POSE_LANDMARKS) -> None:
        self._key_points_dictionary = key_points_dictionary

    @staticmethod
    def compute_angle_between_points(a: tuple, b: tuple, c: tuple) -> float:
        """
        Calculates the angle ABC (in degrees) between points A, B, and C.

        :param a: The first point (A) in the angle calculation.
        :param b: The second point (B) which is the vertex of the angle.
        :param c: The third point (C) in the angle calculation.

        :return: The angle between the points A, B, and C in degrees.
        """
        # calculate the vectors AB and BC
        ba = np.array([a[0] - b[0], a[1] - b[1]])
        bc = np.array([c[0] - b[0], c[1] - b[1]])

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba == 0 or norm_bc == 0:
            return float('nan')

        # calculate the cosine of the angle
        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)

        # clip to avoid numerical errors
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        # calculate the angle in degrees
        angle = degrees(acos(cosine_angle))

        return angle

    @staticmethod
    def compute_normalized_height_angle_between_points(a: tuple, b: tuple, c: tuple) -> float:
        """
        Calculates the angle ABC (in degrees) between points A, B, and C using the Law of Cosines.

        :param a: The first point (A) in the angle calculation.
        :param b: The second point (B) which is the vertex of the angle.
        :param c: The third point (C) in the angle calculation.

        :return: The angle between the points A, B, and C in degrees.
        """
        # calculate the lengths of the sides of the triangle
        ab = np.linalg.norm(np.array(a) - np.array(b))
        bc = np.linalg.norm(np.array(b) - np.array(c))
        ac = np.linalg.norm(np.array(a) - np.array(c))

        # apply the Law of Cosines
        angle = degrees(acos((ab ** 2 + bc ** 2 - ac ** 2) / (2 * ab * bc)))

        return angle

    @staticmethod
    def compute_normal_vector(p1: tuple, p2: tuple, p3: tuple) -> float or None:
        """
        Compute the normal vector of the plane defined by points p1, p2, and p3.

        :param p1: The first point.
        :param p2: The second point.
        :param p3: The third point.

        :return: The normal vector of the plane defined by points p1, p2, and p3.
        """
        # calculate the vectors v1 and v2
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p1)

        # calculate the normal vector
        normal = np.cross(v1, v2)
        norm = np.linalg.norm(normal)

        # check if the norm is zero
        if norm == 0:
            return None

        # normalize the normal vector
        return normal / norm

    def compute_right_hip_knee_ankle_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the hip, knee, and ankle landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the hip, knee, and ankle landmarks.
        """
        right_hip = landmarks[self._key_points_dictionary['right hip']]
        right_knee = landmarks[self._key_points_dictionary['right knee']]
        right_ankle = landmarks[self._key_points_dictionary['right ankle']]

        return self.compute_angle_between_points(right_hip, right_knee, right_ankle)

    def compute_left_hip_knee_ankle_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the hip, knee, and ankle landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the hip, knee, and ankle landmarks.
        """
        left_hip = landmarks[self._key_points_dictionary['left hip']]
        left_knee = landmarks[self._key_points_dictionary['left knee']]
        left_ankle = landmarks[self._key_points_dictionary['left ankle']]

        return self.compute_angle_between_points(left_hip, left_knee, left_ankle)

    def compute_right_shoulder_hip_knee_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the shoulder, hip, and knee landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the shoulder, hip, and knee landmarks.
        """
        right_shoulder = landmarks[self._key_points_dictionary['right shoulder']]
        right_hip = landmarks[self._key_points_dictionary['right hip']]
        right_knee = landmarks[self._key_points_dictionary['right knee']]

        return self.compute_angle_between_points(right_shoulder, right_hip, right_knee)

    def compute_left_shoulder_hip_knee_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the shoulder, hip, and knee landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the shoulder, hip, and knee landmarks.
        """
        left_shoulder = landmarks[self._key_points_dictionary['left shoulder']]
        left_hip = landmarks[self._key_points_dictionary['left hip']]
        left_knee = landmarks[self._key_points_dictionary['left knee']]

        return self.compute_angle_between_points(left_shoulder, left_hip, left_knee)

    def compute_right_shoulder_elbow_wrist_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the shoulder, elbow, and wrist landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the shoulder, elbow, and wrist landmarks.
        """
        right_shoulder = landmarks[self._key_points_dictionary['right shoulder']]
        right_elbow = landmarks[self._key_points_dictionary['right elbow']]
        right_wrist = landmarks[self._key_points_dictionary['right wrist']]

        return self.compute_angle_between_points(right_shoulder, right_elbow, right_wrist)

    def compute_left_shoulder_elbow_wrist_angle(self, landmarks: list) -> float:
        """
        Computes the angle between the shoulder, elbow, and wrist landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the shoulder, elbow, and wrist landmarks.
        """
        left_shoulder = landmarks[self._key_points_dictionary['left shoulder']]
        left_elbow = landmarks[self._key_points_dictionary['left elbow']]
        left_wrist = landmarks[self._key_points_dictionary['left wrist']]

        return self.compute_angle_between_points(left_shoulder, left_elbow, left_wrist)

    def compute_right_elbow_wrist_index_angle(self, landmarks: list) -> float:
        """
        Compute the angle between the right elbow, wrist, and index landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the right elbow, wrist, and index landmarks.
        """
        right_elbow = landmarks[self._key_points_dictionary['right elbow']]
        right_wrist = landmarks[self._key_points_dictionary['right wrist']]
        right_index = landmarks[self._key_points_dictionary['right index']]

        return self.compute_angle_between_points(right_elbow, right_wrist, right_index)

    def compute_left_elbow_wrist_index_angle(self, landmarks: list) -> float:
        """
        Compute the angle between the left elbow, wrist, and index landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the left elbow, wrist, and index landmarks.
        """
        left_elbow = landmarks[self._key_points_dictionary['left elbow']]
        left_wrist = landmarks[self._key_points_dictionary['left wrist']]
        left_index = landmarks[self._key_points_dictionary['left index']]

        return self.compute_angle_between_points(left_elbow, left_wrist, left_index)

    def compute_right_hip_shoulder_elbow_angle(self, landmarks: list) -> float:
        """
        Compute the angle between the right hip, shoulder, and elbow landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the right hip, shoulder, and elbow landmarks.
        """
        right_hip = landmarks[self._key_points_dictionary['right hip']]
        right_shoulder = landmarks[self._key_points_dictionary['right shoulder']]
        right_elbow = landmarks[self._key_points_dictionary['right elbow']]

        return self.compute_angle_between_points(right_hip, right_shoulder, right_elbow)

    def compute_left_hip_shoulder_elbow_angle(self, landmarks: list) -> float:
        """
        Compute the angle between the left hip, shoulder, and elbow landmarks.

        :param landmarks: Dictionary of landmarks.

        :return: The angle between the left hip, shoulder, and elbow landmarks.
        """
        left_hip = landmarks[self._key_points_dictionary['left hip']]
        left_shoulder = landmarks[self._key_points_dictionary['left shoulder']]
        left_elbow = landmarks[self._key_points_dictionary['left elbow']]

        return self.compute_angle_between_points(left_hip, left_shoulder, left_elbow)

    def compute_right_foot_knee_alignment(self, landmarks: list) -> bool:
        """
        Compute the alignment of the right foot and knee.

        :param landmarks: Dictionary of landmarks.

        :return: True if the foot and knee are aligned, False otherwise.
        """
        right_hip = landmarks[self._key_points_dictionary['right hip']]
        right_knee = landmarks[self._key_points_dictionary['right knee']]
        right_ankle = landmarks[self._key_points_dictionary['right ankle']]
        right_foot_index = landmarks[self._key_points_dictionary['right foot index']]

        return self._compute_foot_knee_alignment(right_hip, right_knee, right_ankle, right_foot_index)

    def compute_left_foot_knee_alignment(self, landmarks: list) -> bool:
        """
        Compute the alignment of the left foot and knee.

        :param landmarks: Dictionary of landmarks.

        :return: True if the foot and knee are aligned, False otherwise.
        """
        left_hip = landmarks[self._key_points_dictionary['left hip']]
        left_knee = landmarks[self._key_points_dictionary['left knee']]
        left_ankle = landmarks[self._key_points_dictionary['left ankle']]
        left_foot_index = landmarks[self._key_points_dictionary['left foot index']]

        return self._compute_foot_knee_alignment(left_hip, left_knee, left_ankle, left_foot_index)

    @staticmethod
    def calculate_vertical_orientation_angle(upper_point, lower_point):
        """
        Calculate the angle in degrees between the line formed by two points and the vertical axis.

        :param upper_point: The coordinates (x, y) of the upper point.
        :param lower_point: The coordinates (x, y) of the lower point.

        :return: The angle in degrees.
        """
        # calculate the difference in coordinates
        dx = upper_point[0] - lower_point[0]
        dy = upper_point[1] - lower_point[1]

        # calculate the angle using atan2, atan2 returns the angle in radians
        angle_radians = atan2(dx, dy)

        # convert radians to degrees
        angle_degrees = degrees(angle_radians)

        return abs(angle_degrees)

    def compute_head_pitch_angle(self, landmarks: list) -> float or None:
        """
        Compute the pitch of the head based on the normal vector to the face plane.

        :param landmarks: Dictionary of landmarks.

        :return: The pitch of the head.
        """
        # get the landmarks for the eyes and nose
        eye_left = landmarks[self._key_points_dictionary['left eye']][:3]
        eye_right = landmarks[self._key_points_dictionary['right eye']][:3]
        nose = landmarks[self._key_points_dictionary['nose']][:3]

        # compute the normal vector
        normal_vector = self.compute_normal_vector(eye_left, eye_right, nose)
        if normal_vector is None:
            return None

        # calculate the angle between the normal vector and the vertical axis
        vertical_axis = np.array([0, 0, 1])
        cosine_of_angle = np.dot(normal_vector, vertical_axis) / (
                    np.linalg.norm(normal_vector) * np.linalg.norm(vertical_axis))
        angle = acos(max(min(cosine_of_angle, 1), -1))

        return degrees(angle)

    @staticmethod
    def _compute_foot_knee_alignment(hip, knee, ankle, foot_index) -> bool:
        """
        Compute the alignment of the foot and knee.

        :param hip: Coordinates of the hip.
        :param knee: Coordinates of the knee.
        :param ankle: Coordinates of the ankle.
        :param foot_index: Coordinates of the foot index.

        :return: True if the foot and knee are aligned, False otherwise.
        """
        # create vectors
        knee_to_hip = np.array([hip[0] - knee[0], hip[1] - knee[1], hip[2] - knee[2]])
        ankle_to_foot_index = np.array([foot_index[0] - ankle[0], foot_index[1] - ankle[1], foot_index[2] - ankle[2]])

        # normalize vectors
        knee_to_hip_unit = knee_to_hip / np.linalg.norm(knee_to_hip)
        ankle_to_foot_index_unit = ankle_to_foot_index / np.linalg.norm(ankle_to_foot_index)

        # compute the dot product
        return np.dot(knee_to_hip_unit, ankle_to_foot_index_unit)

    @staticmethod
    def compute_eccentric_concentric_ratio(eccentric_frames: list, concentric_frames: list) -> float:
        """
        Computes the eccentric to concentric ratio.

        :param eccentric_frames: List of eccentric frames.
        :param concentric_frames: List of concentric frames.

        :return: The eccentric to concentric ratio.
        """
        if len(concentric_frames) == 0:
            return 0

        return len(eccentric_frames) / len(concentric_frames)
