import os
import glob
import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from joblib import dump
from typing import List, Tuple
from matplotlib import pyplot as plt
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

from repetition_segmentation_model.models import SimpleGRURepetitionTrackerNet, SimpleLSTMRepetitionTrackerNet, GRURepetitionTrackerNet


class RepetitionRegression:
    def __init__(self, dataset_directory: str, save_directory: str) -> None:
        self.__data_directory = dataset_directory
        self.__save_directory = save_directory
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

    @staticmethod
    def __prepare_labels(labels: List[float]) -> List[List[float]]:
        labels_array = np.array(labels)
        fractions = labels_array - np.floor(labels_array)
        adjusted_fractions = np.where(fractions > 0.5, 1 - fractions, fractions)
        return [[value] for value in adjusted_fractions]

    @staticmethod
    def __prepare_data(features: np.ndarray, labels: np.ndarray, batch_size: int = 64) -> DataLoader:
        features_tensor = torch.tensor(features, dtype=torch.float32)
        labels_tensor = torch.tensor(labels, dtype=torch.float32)
        dataset = TensorDataset(features_tensor, labels_tensor)
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)

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

    def __preprocess_key_points_and_angles(self) -> Tuple[np.ndarray, np.ndarray]:
        all_features, all_labels = self.__load_data()

        key_points = all_features[:, :-4]
        angles = all_features[:, -4:]

        scaler_key_points = StandardScaler()
        scaler_angles = StandardScaler()

        key_points_normalized = scaler_key_points.fit_transform(key_points)
        angles_normalized = scaler_angles.fit_transform(angles)

        dump(scaler_key_points, 'scaler_key_points.joblib')
        dump(scaler_angles, 'scaler_angles.joblib')

        features_normalized = np.concatenate([key_points_normalized, angles_normalized], axis=1)

        return features_normalized, all_labels

    def evaluate(self, model: nn.Module, test_loader: DataLoader) -> Tuple[List[float], List[float], float]:
        model.eval()
        criterion = nn.MSELoss()
        total_loss = 0
        predictions = []
        truths = []

        with torch.no_grad():
            for batch_features, batch_labels in test_loader:
                outputs = model(batch_features)
                loss = criterion(outputs, batch_labels)
                total_loss += loss.item()
                predictions.extend(outputs.detach().numpy())
                truths.extend(batch_labels.detach().numpy())

        avg_loss = total_loss / len(test_loader)
        print(f'Test Loss: {avg_loss}')
        return predictions, truths, avg_loss

    def __visualize_predictions(self, predictions: List[float], truths: List[float]) -> None:
        plt.figure(figsize=(10, 5))
        plt.scatter(truths, predictions, alpha=0.5, color='blue')
        plt.xlabel('True Values')
        plt.ylabel('Predictions')
        plt.title('Prediction vs True Value')
        plt.plot([min(truths), max(truths)], [min(truths), max(truths)], 'r--')
        plt.show()

    def train(self, model: nn.Module, train_loader: DataLoader, valid_loader: DataLoader, num_epochs: int = 25, fold_index: int = 1) -> None:
        model.train()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        best_loss = float('inf')

        for epoch in range(num_epochs):
            total_loss = 0
            for batch_features, batch_labels in train_loader:
                model.train()
                optimizer.zero_grad()
                outputs = model(batch_features)
                loss = criterion(outputs, batch_labels)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            # validation step
            model.eval()
            valid_loss = 0
            with torch.no_grad():
                for batch_features, batch_labels in valid_loader:
                    outputs = model(batch_features)
                    loss = criterion(outputs, batch_labels)
                    valid_loss += loss.item()

            print(f'Fold {fold_index}, Epoch {epoch + 1}: Training Loss {total_loss / len(train_loader)}, Validation '
                  f'Loss {valid_loss / len(valid_loader)}')

            # save the best model iteration
            if valid_loss < best_loss:
                best_loss = valid_loss
                torch.save(model.state_dict(), os.path.join(self.__save_directory, f'gru_best_model_fold_{fold_index}.pth'))
                print(f"Saved new best model at epoch {epoch + 1} with loss {best_loss}")

            if epoch == num_epochs - 1:
                predictions, truths, _ = self.evaluate(model, valid_loader)
                self.__visualize_predictions(predictions, truths)

    def k_fold_validation(self, num_splits: int = 5, num_epochs: int = 25) -> None:
        features, labels = self.__preprocess_key_points_and_angles()

        kf = KFold(n_splits=num_splits, shuffle=True)
        for fold, (train_idx, test_idx) in enumerate(kf.split(features)):
            train_features, test_features = features[train_idx], features[test_idx]
            train_labels, test_labels = labels[train_idx], labels[test_idx]

            train_loader = self.__prepare_data(train_features, train_labels)
            test_loader = self.__prepare_data(test_features, test_labels)

            model = SimpleGRURepetitionTrackerNet(input_size=train_features.shape[1])
            print(f"Training fold {fold + 1}/{num_splits}")
            self.train(model, train_loader, test_loader, num_epochs, fold + 1)


data_directory = '../infinityai_squat/data/processed/'
save_directory = '../model_saves/'
rc = RepetitionRegression(data_directory, save_directory)
rc.k_fold_validation(num_splits=5, num_epochs=25)
