from ..constants import BLAZE_POSE_LANDMARKS

from ..pose_correction.AnglesAnalyzer import AnglesAnalyzer
from ..pose_correction.PoseAnalyzer import PoseAnalyzer
from ..pose_correction.PoseCorrection import PoseCorrection


class SquatPoseCorrection(PoseCorrection):
    def __init__(self) -> None:
        super().__init__()
        self.__LANDMARKS_DICTIONARY = BLAZE_POSE_LANDMARKS
        self._REPETITION_START_THRESHOLD = 135
        self._ERROR_THRESHOLD = 15
        self._CHANGE_THRESHOLD = 15
        self._angle_names = ['right_shoulder_hip_knee', 'right_hip_knee_ankle']
        self._segmentation_angle_name = 'right_hip_knee_ankle'
        # squat depth
        self.__PERFECT_SQUAT_DEPTH = 90
        self.__GOOD_SQUAT_DEPTH = (90, self._REPETITION_START_THRESHOLD)
        self.__BAD_SQUAT_DEPTH = self._REPETITION_START_THRESHOLD
        # head tilt
        self.__HEAD_TILT_THRESHOLD = (120, 160)
        # heel vertical movement
        self.__HEEL_VERTICAL_MOVEMENT_THRESHOLD = 0.001
        self.__HEEL_VERTICAL_MOVEMENT_ERROR_THRESHOLD = 0.1
        # hip slope
        self.__HIP_SLOPE_THRESHOLD = (0.09, 0.15)
        # trunk slope
        self.__TRUNK_SLOPE_THRESHOLD = 15
        # trunk vertical incline degree
        self.__TRUNK_VERTICAL_INCLINE_DEGREE = 170
        # toe knee distance
        self.__TOE_KNEE_DISTANCE_THRESHOLD = 0.01
        # eccentric-concentric ratio
        self.__PERFECT_RATIO = 2
        self.__GOOD_RATIO = (1.5, 2)
        self.__BAD_RATIO = 1.5

    def _get_correction_advice(self, landmarks: dict, angles: dict) -> dict:
        """
        Provides correction advice based on the given landmarks and angles.

        :param landmarks: A dictionary of body landmarks.
        :param angles: A dictionary of calculated angles between landmarks.

        :return: A dictionary with correction advice.
        """
        # initialize the correction advice dictionary
        correction_advice = dict()

        # filter angles to only include those above the threshold
        filtered_angles = {frame: angle for frame, angle in angles['right_hip_knee_ankle'].items() if angle >
                           self._ERROR_THRESHOLD}

        # get the frame with the minimum angle value above the threshold
        minimum_squat_depth_frame = min(filtered_angles, key=filtered_angles.get)

        # get the minimum squat depth
        minimum_squat_depth = filtered_angles[minimum_squat_depth_frame]

        # get the squat depth correction
        squat_depth_correction = self.squat_depth(minimum_squat_depth)

        # add the squat depth correction to the advice dictionary
        correction_advice['squat_depth'] = squat_depth_correction
        if squat_depth_correction[1] == 3:
            return correction_advice

        # initialize flags for each pose correction
        head_position = True
        thoracic_position = True
        hip_position = True
        frontal_knee = True
        foot_position = True

        # iterate over each frame to check for pose corrections
        previous_frame_landmarks = landmarks[min(landmarks.keys())]
        for frame in landmarks.keys():
            # get the landmarks and angles for the current frame
            frame_landmarks = landmarks[frame]

            segmentation_angle = angles[self._segmentation_angle_name][frame]

            # check if the squat depth is within the threshold
            if segmentation_angle < self._REPETITION_START_THRESHOLD:
                if head_position and not self.head_position(frame_landmarks):
                    correction_advice['head_position'] = "You need to keep your head straight.", 3
                    head_position = False

                if thoracic_position and not self.thoracic_position(frame_landmarks):
                    correction_advice['thoracic_position'] = "You need to keep your chest up.", 3
                    thoracic_position = False

                if hip_position and not self.hip_position(frame_landmarks):
                    correction_advice['hip_position'] = "You need to keep your hips parallel to the ground.", 3
                    hip_position = False

                if frontal_knee and not self.frontal_knee_position(frame_landmarks):
                    correction_advice['frontal_knee_position'] = "You need to keep your knees in line with your toes.", 3
                    frontal_knee = False

                if foot_position and not self.foot_position(previous_frame_landmarks[
                                                                self.__LANDMARKS_DICTIONARY['right heel']][1],
                                                            frame_landmarks[
                                                                self.__LANDMARKS_DICTIONARY['right heel']][1]):
                    correction_advice['foot_position'] = "You need to keep your entire foot in contact with the ground.", 3
                    foot_position = False

            previous_frame_landmarks = frame_landmarks

        if head_position:
            correction_advice['head_position'] = "Your head position is good.", 1

        if thoracic_position:
            correction_advice['thoracic_position'] = "Your thoracic position is good.", 1

        if hip_position:
            correction_advice['hip_position'] = "Your hip position is good.", 1

        if frontal_knee:
            correction_advice['frontal_knee_position'] = "Your knee position is good.", 1

        if foot_position:
            correction_advice['foot_position'] = "Your foot position is good.", 1

        # get the trunk position
        correction_advice['trunk_position'] = self.trunk_position(landmarks[minimum_squat_depth_frame])

        # get the eccentric-concentric ratio
        correction_advice['eccentric_concentric_ratio'] = self.eccentric_concentric_ratio(angles['right_hip_knee_ankle'])

        return correction_advice

    def squat_depth(self, minimum_execution_depth: float) -> tuple:
        """
        Squat depth is at least 90 degrees at the knee joint.

        :param minimum_execution_depth: The minimum depth of the squat from the user repetition.

        :return: A tuple containing the correction advice and the correction level.
        """
        # check if the squat depth is within the threshold
        if minimum_execution_depth > self.__BAD_SQUAT_DEPTH:
            return "This is not considered a squat. You need to go deeper in depth.", 3

        elif self.__GOOD_SQUAT_DEPTH[0] < minimum_execution_depth < self.__GOOD_SQUAT_DEPTH[1]:
            return "You need to go deeper in depth.", 2

        return "You depth is good.", 1

    def head_position(self, landmarks: list) -> bool:
        """
        Line of neck is perpendicular to the ground and gaze is aimed forward.

        :param landmarks: Dictionary of landmarks.

        :return: True if the head position is correct, False otherwise.
        """
        # extract coordinates for each keypoint
        head_tilt_angle = self._pose_analyzer.compute_head_pitch_angle(landmarks)

        # check if the head tilt angle is within the threshold
        if self.__HEAD_TILT_THRESHOLD[0] < head_tilt_angle < self.__HEAD_TILT_THRESHOLD[1]:
            return True

        return False

    def thoracic_position(self, landmarks: list) -> bool:
        """
        Chest is held upward and shoulder blades are retracted.

        :param landmarks: Dictionary of landmarks.

        :return: True if the thoracic position is correct, False otherwise.
        """
        # extract coordinates for each keypoint
        right_shoulder = landmarks[self.__LANDMARKS_DICTIONARY['right shoulder']]
        right_hip = landmarks[self.__LANDMARKS_DICTIONARY['right hip']]

        # calculate trunk angle
        trunk_angle = PoseAnalyzer.calculate_vertical_orientation_angle(right_shoulder, right_hip)

        # check if the trunk is vertical
        if trunk_angle <= self.__TRUNK_VERTICAL_INCLINE_DEGREE:
            return True
        else:
            return False

    def trunk_position(self, landmarks: list) -> tuple:
        """
        Trunk is parallel to tibia, while maintaining slightly lordotic lumbar spine.

        :param landmarks: Dictionary of landmarks.

        :return: A tuple containing the correction advice and the correction level.
        """
        # extract coordinates for each keypoint
        shoulder = landmarks[self.__LANDMARKS_DICTIONARY['right shoulder']]
        hip = landmarks[self.__LANDMARKS_DICTIONARY['right hip']]
        knee = landmarks[self.__LANDMARKS_DICTIONARY['right knee']]
        ankle = landmarks[self.__LANDMARKS_DICTIONARY['right ankle']]

        # calculate angles
        trunk_angle = abs(PoseAnalyzer.calculate_vertical_orientation_angle(shoulder, hip))
        tibia_angle = abs(PoseAnalyzer.calculate_vertical_orientation_angle(knee, ankle))

        # determine parallelism
        angle_difference = abs(trunk_angle - tibia_angle)
        if angle_difference < self.__TRUNK_SLOPE_THRESHOLD:
            return "Your trunk is parallel to your tibia.", 1

        return "Your trunk is not parallel to your tibia.", 3

    def hip_position(self, landmarks: list) -> bool:
        """
        Line of hips is parallel to ground in frontal plane throughout squat.

        :param landmarks: Dictionary of landmarks.

        :return: True if the hip position is correct, False otherwise.
        """
        # extract coordinates for each keypoint
        left_hip = landmarks[self.__LANDMARKS_DICTIONARY['left hip']]
        right_hip = landmarks[self.__LANDMARKS_DICTIONARY['right hip']]

        # calculate slope
        if (right_hip[0] - left_hip[0]) == 0:
            slope = float('inf')
        else:
            slope = (right_hip[1] - left_hip[1]) / (right_hip[0] - left_hip[0])

        # check if the slope exceeds the threshold
        if self.__HIP_SLOPE_THRESHOLD[0] <= abs(slope) <= self.__HIP_SLOPE_THRESHOLD[1]:
            return False

        return True

    def frontal_knee_position(self, landmarks: list) -> bool:
        """
        Lateral aspect of knee does not cross medial malleolus for either leg.

        :param landmarks: Dictionary of landmarks.

        :return: True if the knee position is correct, False otherwise.
        """
        # extract x-coordinates of knee and toe landmarks
        right_knee_x = landmarks[self.__LANDMARKS_DICTIONARY['right knee']][0]
        right_toe_x = landmarks[self.__LANDMARKS_DICTIONARY['right foot index']][0]
        left_knee_x = landmarks[self.__LANDMARKS_DICTIONARY['left knee']][0]
        left_toe_x = landmarks[self.__LANDMARKS_DICTIONARY['left foot index']][0]

        # calculate distances
        distance_between_knees = abs(right_knee_x - left_knee_x)
        distance_between_toes = abs(right_toe_x - left_toe_x)

        # compare distances and check if the difference exceeds the threshold
        distance_difference = abs(distance_between_knees - distance_between_toes)

        return distance_difference > self.__TOE_KNEE_DISTANCE_THRESHOLD

    def foot_position(self, previous_vertical_position: float, current_vertical_position: float) -> bool:
        """
        Entire foot remains in contact with the ground throughout squat.

        :param previous_vertical_position: The vertical position of the foot in the previous frame.
        :param current_vertical_position: The vertical position of the foot in the current frame.

        :return: True if the foot position is correct, False otherwise.
        """
        # calculate the range of motion
        range_of_motion = abs(current_vertical_position - previous_vertical_position)

        # check if the range of motion exceeds the error threshold(may be due to noise)
        if range_of_motion > self.__HEEL_VERTICAL_MOVEMENT_ERROR_THRESHOLD:
            return True

        # check if the range of motion exceeds the threshold
        if range_of_motion > self.__HEEL_VERTICAL_MOVEMENT_THRESHOLD:
            return False

        return True

    def eccentric_concentric_ratio(self, angles: dict) -> tuple:
        """
        Ascent-descent timing ratio is at least 2:1. Eccentric phase is slower than concentric phase.
        The movement is controlled and the subject does not drop into the squat.

        :param angles: List of angles representing knee-hip-ankle.

        :return: A tuple containing the correction advice and the correction level.
        """
        # get eccentric and concentric frames
        eccentric, concentric = AnglesAnalyzer.get_eccentric_and_concentric_frames(angles,
                                                                                   self._REPETITION_START_THRESHOLD)

        # compute ratio
        ratio = self._pose_analyzer.compute_eccentric_concentric_ratio(eccentric, concentric)
        if ratio >= self.__PERFECT_RATIO:
            return "Your movement is controlled, not dropping into the squat.", 1

        if self.__GOOD_RATIO[0] <= ratio <= self.__GOOD_RATIO[1]:
            return "Your movement pace is good, but try to control the descent more.", 2

        return "You need to also control the descent movement, not just the ascent.", 3
