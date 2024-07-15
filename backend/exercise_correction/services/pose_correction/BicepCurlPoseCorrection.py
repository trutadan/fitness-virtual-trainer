from ..constants import BLAZE_POSE_LANDMARKS

from ..pose_correction.AnglesAnalyzer import AnglesAnalyzer
from ..pose_correction.PoseCorrection import PoseCorrection


class BicepCurlPoseCorrection(PoseCorrection):
    def __init__(self) -> None:
        super().__init__()
        self.__LANDMARKS_DICTIONARY = BLAZE_POSE_LANDMARKS
        self._REPETITION_START_THRESHOLD = 120
        self._ERROR_THRESHOLD = 15
        self._CHANGE_THRESHOLD = 90
        self._angle_names = ['right_shoulder_elbow_wrist', 'right_elbow_wrist_index', 'right_hip_shoulder_elbow',
                             'right_shoulder_hip_knee']
        self._segmentation_angle_name = 'right_shoulder_elbow_wrist'
        # curl depth
        self.__PERFECT_CURL_DEPTH = 60
        self.__GOOD_CURL_DEPTH = (60, self._REPETITION_START_THRESHOLD)
        self.__BAD_CURL_DEPTH = self._REPETITION_START_THRESHOLD
        # wrist position
        self.__WRIST_POSITION = (150, 180)
        # elbow position relative to trunk
        self.__PERFECT_ELBOW_POSITION = 15
        self.__GOOD_ELBOW_POSITION = (15, 25)
        self.__BAD_ELBOW_POSITION = 25
        # back arching momentum
        self.__MOMENTUM = (170, 180)
        # eccentric concentric ratio
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
        minimum_curl_depth_frame = min(filtered_angles, key=filtered_angles.get)

        # get the minimum curl depth
        minimum_curl_depth = filtered_angles[minimum_curl_depth_frame]

        # get the curl depth correction
        squat_depth_correction = self.curl_depth(minimum_curl_depth)

        # add the curl depth correction to the advice dictionary
        correction_advice['curl_depth'] = squat_depth_correction
        if squat_depth_correction[1] == 3:
            return correction_advice

        minimum_wrist_flexion_angle = 180
        maximum_hip_shoulder_elbow_angle = 0
        minimum_knee_hip_shoulder_angle = 180

        for frame in landmarks.keys():
            segmentation_angle = angles[self._segmentation_angle_name][frame]

            # check if the squat depth is within the threshold
            if segmentation_angle < self._REPETITION_START_THRESHOLD:
                if angles['right_elbow_wrist_index'][frame] < minimum_wrist_flexion_angle:
                    if abs(angles['right_elbow_wrist_index'][frame] - angles['right_elbow_wrist_index'][frame - 1]) < 15:
                        minimum_wrist_flexion_angle = angles['right_elbow_wrist_index'][frame]

                if angles['right_hip_shoulder_elbow'][frame] > maximum_hip_shoulder_elbow_angle:
                    maximum_hip_shoulder_elbow_angle = angles['right_hip_shoulder_elbow'][frame]

                if angles['right_shoulder_hip_knee'][frame] < minimum_knee_hip_shoulder_angle:
                    minimum_knee_hip_shoulder_angle = angles['right_shoulder_hip_knee'][frame]

        # wrist position
        wrist_position_advice = self.wrist_position(minimum_wrist_flexion_angle)
        correction_advice['wrist_position'] = wrist_position_advice

        # elbow position
        elbow_position_advice = self.elbow_position(maximum_hip_shoulder_elbow_angle)
        correction_advice['elbow_position'] = elbow_position_advice

        # back arching momentum
        back_arching_momentum_advice = self.back_arching_momentum(minimum_knee_hip_shoulder_angle)
        correction_advice['back_arching_momentum'] = back_arching_momentum_advice

        # eccentric-concentric ratio
        eccentric_concentric_advice = self.eccentric_concentric_ratio(angles['right_shoulder_elbow_wrist'])
        correction_advice['eccentric_concentric_ratio'] = eccentric_concentric_advice

        return correction_advice

    def curl_depth(self, minimum_curl_depth_angle: float) -> tuple:
        """
        Evaluates the depth of the curl.

        :param minimum_curl_depth_angle: The minimum angle of the curl depth.

        :return: A tuple indicating the quality of the curl depth.
        """
        if minimum_curl_depth_angle <= self.__PERFECT_CURL_DEPTH:
            return "Perfect curl depth!", 1

        elif self.__GOOD_CURL_DEPTH[0] < minimum_curl_depth_angle <= self.__GOOD_CURL_DEPTH[1]:
            return "Good curl depth, but could be better.", 2

        return "Bad curl depth, please go deeper.", 3

    def wrist_position(self, minimum_wrist_flexion_angle: float) -> tuple:
        """
        Evaluates the wrist position during the curl.

        :param minimum_wrist_flexion_angle: The minimum angle of wrist flexion.

        :return: A tuple indicating the quality of the wrist position.
        """
        if self.__WRIST_POSITION[0] <= minimum_wrist_flexion_angle <= self.__WRIST_POSITION[1]:
            return "Good wrist position.", 1

        return "Bad wrist position, please straighten your wrist.", 3

    def elbow_position(self, maximum_hip_shoulder_elbow_angle: float) -> tuple:
        """
        Evaluates the elbow position relative to the trunk.

        :param maximum_hip_shoulder_elbow_angle: The maximum angle between the hip, shoulder, and elbow.

        :return: A tuple indicating the quality of the elbow position.
        """
        if maximum_hip_shoulder_elbow_angle <= self.__PERFECT_ELBOW_POSITION:
            return "Perfect elbow position!", 1

        elif self.__GOOD_ELBOW_POSITION[0] < maximum_hip_shoulder_elbow_angle <= self.__GOOD_ELBOW_POSITION[1]:
            return "Good elbow position, but could be better.", 2

        return "Bad elbow position, please keep your elbows closer to your body.", 3

    def back_arching_momentum(self, minimum_knee_hip_shoulder_angle: float) -> tuple:
        """
        Evaluates back arching and momentum during the curl.

        :param minimum_knee_hip_shoulder_angle: The minimum angle between the knee, hip, and shoulder.

        :return: A tuple indicating the quality of back stability.
        """
        if self.__MOMENTUM[0] <= minimum_knee_hip_shoulder_angle <= self.__MOMENTUM[1]:
            return "Good back stability!", 1

        return "Poor back stability, avoid arching your back.", 3

    def eccentric_concentric_ratio(self, angles: dict) -> tuple:
        """
        Evaluates the eccentric-concentric ratio during the curl.

        :param angles: A list of angles during the curl movement.

        :return: A tuple indicating the quality of the eccentric-concentric ratio.
        """
        # get eccentric and concentric frames
        eccentric, concentric = AnglesAnalyzer.get_eccentric_and_concentric_frames(angles,
                                                                                   self._REPETITION_START_THRESHOLD)

        ratio = self._pose_analyzer.compute_eccentric_concentric_ratio(eccentric, concentric)
        if ratio >= self.__PERFECT_RATIO:
            return "Your movement is controlled, great job!", 1

        if self.__GOOD_RATIO[0] <= ratio <= self.__GOOD_RATIO[1]:
            return "Your movement pace is good, but try to slow down the lowering phase.", 2

        return "You need to also control the descent movement, aim for a slower eccentric phase.", 3
