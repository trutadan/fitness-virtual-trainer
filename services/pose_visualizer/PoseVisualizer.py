import cv2

from pose_correction.PoseAnalyzer import PoseAnalyzer


class PoseVisualizer:
    def __init__(self, video_path, landmarks_dictionary, key_points_dictionary):
        self._video_path = video_path
        self._landmarks_dictionary = landmarks_dictionary
        self._key_points_dictionary = key_points_dictionary

    def visualize_video(self, show_angles: bool = False) -> None:
        """
        Visualizes the video with the pose skeleton and angles drawn on it.

        :param show_angles: Whether to show the angles on the video.
        """
        # open the video file
        cap = cv2.VideoCapture(self._video_path)
        frame_index = 0

        # loop through the video frames
        while cap.isOpened():
            # read the frame and check if it has landmarks
            success, image = cap.read()
            if not success or frame_index not in self._landmarks_dictionary:
                break

            # draw the skeleton on the image
            landmarks = self._landmarks_dictionary[frame_index]
            self.draw_skeleton(image, landmarks)

            # draw the angles on the image
            if show_angles:
                self.draw_angles(image, landmarks)

            # display the image
            cv2.imshow('Pose', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break

            frame_index += 1

        # release the video capture and close the window
        cap.release()
        cv2.destroyAllWindows()

    def visualize_frame(self, frame_number: int, show_angles: bool = False) -> None:
        """
        Visualizes a specific frame from the video with the pose skeleton and angles drawn on it.

        :param frame_number: The frame number to visualize.
        :param show_angles: Whether to show the angles on the video.
        """
        # open the video file
        cap = cv2.VideoCapture(self._video_path)

        # set the frame to the specific frame number
        cap.set(1, frame_number)

        # read the frame and check if it has landmarks
        success, image = cap.read()
        if success and frame_number in self._landmarks_dictionary:
            # draw the skeleton on the image
            landmarks = self._landmarks_dictionary[frame_number]
            self.draw_skeleton(image, landmarks)

            # draw the angles on the image
            if show_angles:
                self.draw_angles(image, landmarks)

            # display the image
            cv2.imshow('Pose Frame', image)

            # wait indefinitely until a key is pressed
            cv2.waitKey(0)

        # release the video capture and close the window
        cap.release()
        cv2.destroyAllWindows()

    @staticmethod
    def draw_angle_between_points(image, point1, point2, point3) -> None:
        """
        Draws the angle calculated between any three points on the image.

        :param image: The image on which to draw.
        :param point1: The first point (A) in the angle calculation.
        :param point2: The vertex of the angle (B).
        :param point3: The third point (C) in the angle calculation.
        """
        # calculate the angle
        angle = PoseAnalyzer.compute_angle_between_points(point1, point2, point3)

        # convert the vertex point (point2) position to pixel coordinates for text placement
        point2_px = int(point2[0] * image.shape[1]), int(point2[1] * image.shape[0])

        # draw the angle text near the vertex point
        cv2.putText(image, f"{int(angle)} deg", point2_px, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    def draw_skeleton(self, image, landmarks: dict) -> None:
        """
        Draws the pose skeleton on the image using the landmarks.

        :param image: The image on which to draw.
        :param landmarks: The landmarks' dictionary.
        """
        # draw the skeleton using landmarks
        raise NotImplementedError("draw_skeleton method not implemented")

    def draw_angles(self, image, landmarks: dict) -> None:
        """
        Draws the computed angles on the skeleton.

        :param image: The image on which to draw.
        :param landmarks: The landmarks' dictionary.
        """
        # draw the computed metrics on the skeleton
        raise NotImplementedError("draw_angles method not implemented")
