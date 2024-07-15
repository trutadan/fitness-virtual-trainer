
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
import glob
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from typing import List, Tuple
from sklearn.model_selection import KFold
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler

from repetition_segmentation_model.models import SimpleGRURepetitionTrackerNet, SimpleLSTMRepetitionTrackerNet, GRURepetitionTrackerNet


class RepetitionClassification:
    def __init__(self, data_directory: str, learning_rate: float = 0.001, n_splits: int = 5) -> None:
        self.__data_directory = data_directory
        self.__learning_rate = learning_rate
        self.__n_splits = n_splits

    @staticmethod
    def __prepare_labels(labels: List[int]) -> List[List[int]]:
        binary_labels = [[1]]
        for i in range(1, len(labels)):
            binary_labels.append([1] if int(labels[i]) > int(labels[i - 1]) else [0])

        return binary_labels

    @staticmethod
    def __prepare_data(features: np.ndarray, labels: np.ndarray, batch_size: int = 64) -> DataLoader:
        features_tensor = torch.tensor(features, dtype=torch.float32)
        labels_tensor = torch.tensor(labels, dtype=torch.float32)
        dataset = TensorDataset(features_tensor, labels_tensor)
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)

    def train(self, model: nn.Module, train_loader: DataLoader, num_epochs: int = 25) -> None:
        model.train()
        optimizer = optim.Adam(model.parameters(), lr=self.__learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)

        for epoch in range(num_epochs):
            for features, labels in train_loader:
                optimizer.zero_grad()
                outputs = model(features)
                loss = nn.BCEWithLogitsLoss()(outputs, labels)
                loss.backward()
                optimizer.step()

            scheduler.step()
            print(f'Epoch {epoch + 1}, Loss: {loss.item()}')

    def test(self, model: nn.Module, test_loader: DataLoader) -> Tuple[float, float, float, float]:
        model.eval()
        y_true, y_pred = [], []

        with torch.no_grad():
            for features, labels in test_loader:
                outputs = model(features)
                predictions = torch.sigmoid(outputs) > 0.5
                y_true.extend(labels.flatten().tolist())
                y_pred.extend(predictions.flatten().tolist())

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.title('Confusion Matrix')
        plt.show()

        print(f'Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}')
        return accuracy, precision, recall, f1

    def __preprocess_angles(self) -> Tuple[np.ndarray, np.ndarray]:
        all_features, all_labels = self.__load_data()
        angles = all_features[:, -4:]

        scaler = StandardScaler()
        angles_normalized = scaler.fit_transform(angles)

        return angles_normalized, all_labels

    def __preprocess_key_points(self) -> Tuple[np.ndarray, np.ndarray]:
        all_features, all_labels = self.__load_data()
        key_points = all_features[:, :-4]

        scaler = StandardScaler()
        key_points_normalized = scaler.fit_transform(key_points)

        return key_points_normalized, all_labels

    def __preprocess_key_points_and_angles(self) -> Tuple[np.ndarray, np.ndarray]:
        all_features, all_labels = self.__load_data()

        key_points = all_features[:, :-4]
        angles = all_features[:, -4:]

        scaler_key_points = StandardScaler()
        scaler_angles = StandardScaler()

        key_points_normalized = scaler_key_points.fit_transform(key_points)
        angles_normalized = scaler_angles.fit_transform(angles)

        features_normalized = np.concatenate([key_points_normalized, angles_normalized], axis=1)

        return features_normalized, all_labels

    def __load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        all_features, all_labels = [], []
        for file_path in glob.glob(f"{self.__data_directory}/*.json"):
            with open(file_path, 'r') as file:
                data = json.load(file)

                labels = [entry['label'] for entry in data]
                binary_labels = self.__prepare_labels(labels)

                all_labels.extend(binary_labels)
                all_features.extend([entry['features'] for entry in data])

        return np.array(all_features), np.array(all_labels)

    def compare_data_and_models(self) -> List[float]:
        preprocessing_methods = [
            self.__preprocess_angles,
            self.__preprocess_key_points,
            self.__preprocess_key_points_and_angles
        ]
        preprocessing_labels = [
            "Angles",
            "Key Points",
            "Both Angles and Key Points"
        ]
        accuracies = []

        for preprocess_method, preprocess_label in zip(preprocessing_methods, preprocessing_labels):
            features, labels = preprocess_method()
            model = SimpleGRURepetitionTrackerNet(input_size=len(features[0]))
            kf = KFold(n_splits=self.__n_splits, shuffle=True, random_state=42)
            accuracies_per_preprocessing = []

            for train_index, test_index in kf.split(features):
                train_features, test_features = features[train_index], features[test_index]
                train_labels, test_labels = labels[train_index], labels[test_index]

                train_loader = self.__prepare_data(train_features, train_labels)
                test_loader = self.__prepare_data(test_features, test_labels)

                self.train(model, train_loader)
                accuracy, _, _, _ = self.test(model, test_loader)
                accuracies_per_preprocessing.append(accuracy)

            avg_accuracy = np.mean(accuracies_per_preprocessing)
            accuracies.append(avg_accuracy)
            print(f'Average Accuracy with {preprocess_label}: {avg_accuracy}')

        return accuracies


# model instantiation and usage
data_directory = '../infinityai_squat/data/processed/'
model_manager = RepetitionClassification(data_directory)
print(model_manager.compare_data_and_models())
