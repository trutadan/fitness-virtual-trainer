import json
import cv2
import h5py
import mediapipe as mp
import numpy as np

from typing import List

from pose_correction.PoseAnalyzer import PoseAnalyzer


class InfinityAIRepetitionsExtractor:
    def __init__(self, dataset_path: str) -> None:
        self.__pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.__dataset_path = dataset_path

    def get_repetition_count(self, video_number: str) -> List[float]:
        with open(f"{self.__dataset_path}{video_number}.json", 'r') as file:
            data = json.load(file)

        return [image['rep_count'] for image in data['images']]

    def get_bounding_box(self, video_number: str) -> List[List[float]]:
        with open(f"{self.__dataset_path}{video_number}.json", 'r') as file:
            data = json.load(file)

        return [annotation["bbox"] for annotation in data['annotations']]

    @staticmethod
    def crop_image(image: np.ndarray, bounding_box: List[float]) -> np.ndarray:
        """Crops the given image using the bounding box."""
        x, y, w, h = map(int, bounding_box)
        return image[y:y+h, x:x+w]

    def save_to_json(self, data: List[dict], video_number: str) -> None:
        """Saves the given data to a JSON file."""
        with open(f"{self.__dataset_path}processed/{video_number}.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def read_from_json(self, video_number: str) -> List[dict]:
        """Reads data from a JSON file."""
        with open(f"{self.__dataset_path}processed/{video_number}.json", 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_to_hdf5(self, data: List[dict], video_number: str) -> None:
        """Saves processed data to an HDF5 file."""
        with h5py.File(f"{self.__dataset_path}processed/{video_number}.hdf5", 'w') as f:
            for i, entry in enumerate(data):
                group = f.create_group(f'frame_{i}')
                group.create_dataset('features', data=np.array(entry['features']), compression='gzip')
                group.create_dataset('label', data=entry['label'])

    def read_from_hdf5(self, video_number: str) -> List[dict]:
        """Reads data from an HDF5 file."""
        data = []
        file_path = f"{self.__dataset_path}processed/{video_number}.hdf5"
        with h5py.File(file_path, 'r') as f:
            for frame_key in sorted(f.keys(), key=lambda x: int(x.split('_')[-1])):
                frame_data = f[frame_key]
                features = np.array(frame_data['features'])

                label = np.array(frame_data['label'])
                label = label[()] if label.shape == () else label[0]

                data.append({"features": features, "label": label})

        return data

    def process_video(self, video_number: str) -> List[dict]:
        bounding_boxes = self.get_bounding_box(video_number)
        repetition_counts = self.get_repetition_count(video_number)
        total_frames = len(bounding_boxes)

        cap = cv2.VideoCapture(f"{self.__dataset_path}{video_number}.mp4")
        frame_step = max(1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) // total_frames)

        dataset = []
        pose_analyzer = PoseAnalyzer()

        for frame_index in range(0, total_frames * frame_step, frame_step):
            ret, frame = cap.read()
            if not ret:
                break

            bbox = bounding_boxes[frame_index // frame_step]
            cropped_frame = self.crop_image(frame, bbox)
            image_rgb = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

            results = self.__pose.process(image_rgb)

            if results.pose_landmarks:
                landmarks = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
                flattened_landmarks = [coord for lm in landmarks for coord in lm[:3]]

                angles = [
                    pose_analyzer.compute_right_hip_knee_ankle_angle(landmarks),
                    pose_analyzer.compute_left_hip_knee_ankle_angle(landmarks),
                    pose_analyzer.compute_right_shoulder_hip_knee_angle(landmarks),
                    pose_analyzer.compute_left_shoulder_hip_knee_angle(landmarks),
                ]

                features = flattened_landmarks + angles
                dataset.append({
                    "features": features,
                    "label": repetition_counts[frame_index // frame_step]
                })

        cap.release()
        return dataset

    def prepare_hdf5_dataset(self) -> None:
        for number in range(100):
            video_number = f"{number:06}"
            print(f"Processing video {video_number}.mp4...")

            data = self.process_video(video_number)
            self.save_to_hdf5(data, video_number)

    def prepare_json_dataset(self) -> None:
        for number in range(100):
            video_number = f"{number:06}"
            print(f"Processing video {video_number}.mp4...")

            data = self.process_video(video_number)
            self.save_to_json(data, video_number)

    def parse_json_repetition_frames(self, video_number: str) -> List[int]:
        with open(f"{self.__dataset_path}{video_number}.json", 'r') as file:
            data = json.load(file)

        repetition_changes = []
        last_integer_rep_count = 0

        for image in data['images']:
            rep_count = image['rep_count']
            frame_number = image['frame_numer']

            if int(rep_count) > last_integer_rep_count:
                repetition_changes.append(frame_number)
                last_integer_rep_count = int(rep_count)

        last_rep_count = data['images'][-1]['rep_count']
        last_frame_number = data['images'][-1]['frame_numer']
        if last_rep_count - last_integer_rep_count >= 0.90:
            repetition_changes.append(last_frame_number)

        return repetition_changes


extractor = InfinityAIRepetitionsExtractor('../infinityai_squat/data/')
extractor.prepare_json_dataset()
