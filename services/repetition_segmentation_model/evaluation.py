import cv2
import numpy as np
import torch
import torch.nn as nn
import mediapipe as mp

from joblib import load

from constants import BLAZE_POSE_LANDMARKS
from pose_correction.PoseAnalyzer import PoseAnalyzer
from repetition_segmentation_model.models import SimpleGRURepetitionTrackerNet


def predict(model: nn.Module, inputs: torch.Tensor) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        outputs = model(inputs)

    return outputs.numpy()


scaler_key_points = load('scaler_key_points.joblib')
scaler_angles = load('scaler_angles.joblib')

video_path = '../videos/squat.mp4'
pose = mp.solutions.pose.Pose(
    static_image_mode=False,
    model_complexity=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
pose_analyzer = PoseAnalyzer(BLAZE_POSE_LANDMARKS)
cap = cv2.VideoCapture(video_path)

model_path = '../model_saves/gru_best_model_fold_1.pth'

model = SimpleGRURepetitionTrackerNet(input_size=103)
model.load_state_dict(torch.load(model_path))
model.eval()

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        landmarks = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
        flattened_landmarks = np.array([coord for lm in landmarks for coord in lm[:3]]).reshape(1, -1)
        angles = np.array([
            pose_analyzer.compute_right_hip_knee_ankle_angle(landmarks),
            pose_analyzer.compute_left_hip_knee_ankle_angle(landmarks),
            pose_analyzer.compute_right_shoulder_hip_knee_angle(landmarks),
            pose_analyzer.compute_left_shoulder_hip_knee_angle(landmarks),
        ]).reshape(1, -1)

        key_points_normalized = scaler_key_points.transform(flattened_landmarks)
        angles_normalized = scaler_angles.transform(angles)

        features = np.hstack([key_points_normalized, angles_normalized])
        key_points_tensor = torch.tensor(features, dtype=torch.float32)
        predictions = predict(model, key_points_tensor)

        print(f"Predictions: {predictions}")
        mp.solutions.drawing_utils.draw_landmarks(
            image, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)

    cv2.imshow('Frame with Pose', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
