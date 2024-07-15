from ..constants import BLAZE_POSE_LANDMARKS

from ..pose_correction.AnglesAnalyzer import AnglesAnalyzer
from ..pose_correction.PoseCorrection import PoseCorrection


class PushUpPoseCorrection(PoseCorrection):
    def __init__(self) -> None:
        super().__init__()
        self.__LANDMARKS_DICTIONARY = BLAZE_POSE_LANDMARKS
        self._REPETITION_START_THRESHOLD = 135
        self._ERROR_THRESHOLD = 15
        self._CHANGE_THRESHOLD = 90
        self._angle_names = ['right_shoulder_elbow_wrist', 'right_hip_shoulder_elbow', 'right_shoulder_hip_knee',
                             'right_elbow_wrist_index']
        self._segmentation_angle_name = 'right_shoulder_elbow_wrist'
        # hand placement
        self.__HAND_POSITION = (100, 140)
        # body alignment
        self.__BODY_ALIGNMENT = (140, 180)
        # elbow position
        self.__ELBOW_POSITION = (45, 60)
        # range of motion
        self.__PERFECT_RANGE_OF_MOTION = 90
        self.__GOOD_RANGE_OF_MOTION = (90, 120)
        self.__BAD_RANGE_OF_MOTION = 120
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
        filtered_angles = {frame: angle for frame, angle in angles['right_shoulder_elbow_wrist'].items()
                           if angle > self._ERROR_THRESHOLD}

        # get the frame with the minimum angle value above the threshold
        minimum_push_up_depth_frame = min(filtered_angles, key=filtered_angles.get)

        # get the minimum push_up depth
        minimum_push_up_depth = filtered_angles[minimum_push_up_depth_frame]

        # get the push_up depth correction
        push_up_depth_correction = self.push_up_depth(minimum_push_up_depth)

        # add the push_up depth correction to the advice dictionary
        correction_advice['push_up_depth'] = push_up_depth_correction
        if push_up_depth_correction[1] == 3:
            return correction_advice

        minimum_wrist_flexion_angle = 180
        minimum_knee_hip_shoulder_angle = 180
        maximum_hip_shoulder_elbow_angle = None

        for frame in landmarks.keys():
            segmentation_angle = angles[self._segmentation_angle_name][frame]

            # check if the squat depth is within the threshold
            if segmentation_angle < self._REPETITION_START_THRESHOLD:
                if maximum_hip_shoulder_elbow_angle is None:
                    maximum_hip_shoulder_elbow_angle = angles['right_hip_shoulder_elbow'][frame]

                if angles['right_elbow_wrist_index'][frame] < minimum_wrist_flexion_angle:
                    minimum_wrist_flexion_angle = angles['right_elbow_wrist_index'][frame]

                if angles['right_shoulder_hip_knee'][frame] < minimum_knee_hip_shoulder_angle:
                    minimum_knee_hip_shoulder_angle = angles['right_shoulder_hip_knee'][frame]

        # hand position
        hand_position_advice = self.hand_position(minimum_wrist_flexion_angle)
        correction_advice['hand_position'] = hand_position_advice

        # body alignment
        body_alignment_advice = self.body_alignment(minimum_knee_hip_shoulder_angle)
        correction_advice['body_alignment'] = body_alignment_advice

        # elbow position
        elbow_position_advice = self.elbow_position(maximum_hip_shoulder_elbow_angle)
        correction_advice['elbow_position'] = elbow_position_advice

        # eccentric-concentric ratio
        eccentric_concentric_advice = self.eccentric_concentric_ratio(angles['right_shoulder_elbow_wrist'])
        correction_advice['eccentric_concentric_ratio'] = eccentric_concentric_advice

        return correction_advice

    def push_up_depth(self, elbow_flexion_angle: float) -> tuple:
        """
        Evaluates the range of motion during the push-up.

        :param elbow_flexion_angle: The angle of elbow flexion.

        :return: A tuple indicating the quality of the range of motion.
        """
        if elbow_flexion_angle <= self.__PERFECT_RANGE_OF_MOTION:
            return "Perfect range of motion!", 1

        elif self.__GOOD_RANGE_OF_MOTION[0] < elbow_flexion_angle <= self.__GOOD_RANGE_OF_MOTION[1]:
            return "Good range of motion, but could be better.", 2

        else:
            return "Bad range of motion, lower yourself further.", 3

    def hand_position(self, hand_orientation_angle: float) -> tuple:
        """
        Evaluates the hand position during the push-up.

        :param hand_orientation_angle: The angle of hand orientation.

        :return: A tuple indicating the quality of the hand position.
        """
        if hand_orientation_angle >= self.__HAND_POSITION[1] or self.__HAND_POSITION[0] >= hand_orientation_angle:
            return "Good hand position!", 1

        else:
            return "Bad hand position, please adjust your hands.", 3

    def body_alignment(self, body_alignment_angle: float) -> tuple:
        """
        Evaluates body alignment during the push-up.

        :param body_alignment_angle: The angle of body alignment from head to heels.

        :return: A tuple indicating the quality of the body alignment.
        """
        if self.__BODY_ALIGNMENT[0] <= body_alignment_angle <= self.__BODY_ALIGNMENT[1]:
            return "Good body alignment!", 1

        return "Bad body alignment, maintain a straight line from head to heels.", 3

    def elbow_position(self, elbow_angle: float) -> tuple:
        """
        Evaluates the elbow position during the push-up.

        :param elbow_angle: The angle between the shoulder and elbow relative to the trunk.

        :return: A tuple indicating the quality of the elbow position.
        """
        if self.__ELBOW_POSITION[0] <= elbow_angle <= self.__ELBOW_POSITION[1]:
            return "Perfect elbow position!", 1

        else:
            return "Bad elbow position, keep your elbows closer to your body.", 3

    def eccentric_concentric_ratio(self, angles: dict) -> tuple:
        """
        Evaluates the eccentric-concentric ratio during the push-up.

        :param angles: A list of angles during the push-up movement.

        :return: A tuple indicating the quality of the eccentric-concentric ratio.
        """
        eccentric, concentric = AnglesAnalyzer.get_eccentric_and_concentric_frames(angles,
                                                                                   self._REPETITION_START_THRESHOLD)

        ratio = self._pose_analyzer.compute_eccentric_concentric_ratio(eccentric, concentric)
        print(ratio)
        if ratio >= self.__PERFECT_RATIO:
            return "Your movement is controlled, great job!", 1

        if self.__GOOD_RATIO[0] <= ratio <= self.__GOOD_RATIO[1]:
            return "Your movement pace is good, but try to slow down the lowering phase.", 2

        return "You need to also control the descent movement, aim for a slower eccentric phase.", 3
