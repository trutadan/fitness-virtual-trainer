import torch
import torch.nn as nn


class SimpleGRURepetitionTrackerNet(nn.Module):
    def __init__(self, input_size: int) -> None:
        super(SimpleGRURepetitionTrackerNet, self).__init__()
        self.gru1 = nn.GRU(input_size, 512, batch_first=True, bidirectional=True)
        self.layer_norm1 = nn.LayerNorm(512 * 2)
        self.dropout1 = nn.Dropout(0.25)

        self.gru2 = nn.GRU(512 * 2, 256, batch_first=True, bidirectional=True)
        self.layer_norm2 = nn.LayerNorm(256 * 2)
        self.dropout2 = nn.Dropout(0.25)

        self.fc1 = nn.Linear(256 * 2, 128)
        self.fc2 = nn.Linear(128, 32)
        self.fc3 = nn.Linear(32, 1)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x, _ = self.gru1(x)
        x = self.layer_norm1(x)
        x = self.dropout1(x)

        x, _ = self.gru2(x)
        x = self.layer_norm2(x)
        x = self.dropout2(x)

        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)

        return x


class SimpleLSTMRepetitionTrackerNet(nn.Module):
    def __init__(self, input_size: int) -> None:
        super(SimpleLSTMRepetitionTrackerNet, self).__init__()
        self.lstm1 = nn.LSTM(input_size, 512, batch_first=True)
        self.lstm2 = nn.LSTM(512, 256, batch_first=True)

        self.fc1 = nn.Linear(256, 128)
        self.fc2 = nn.Linear(128, 32)
        self.fc3 = nn.Linear(32, 1)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x, _ = self.lstm1(x)
        x, _ = self.lstm2(x)

        x = self.fc1(x)
        x = self.relu(x)

        x = self.fc2(x)
        x = self.relu(x)

        x = self.fc3(x)

        return x


class GRURepetitionTrackerNet(nn.Module):
    def __init__(self, input_size: int) -> None:
        super(GRURepetitionTrackerNet, self).__init__()
        # self.gru1 = nn.GRU(input_size, 256, batch_first=True, bidirectional=True)
        self.gru1 = nn.GRU(input_size, 512, batch_first=True, bidirectional=True)
        # self.batch_norm1 = nn.BatchNorm1d(256 * 2)
        # self.layer_norm1 = nn.LayerNorm(256 * 2)
        self.layer_norm1 = nn.LayerNorm(512 * 2)
        # self.dropout1 = nn.Dropout(0.5)
        self.dropout1 = nn.Dropout(0.25)

        # self.gru2 = nn.GRU(256 * 2, 128, batch_first=True)
        # self.gru2 = nn.GRU(256 * 2, 128, batch_first=True, bidirectional=True)
        self.gru2 = nn.GRU(512 * 2, 256, batch_first=True, bidirectional=True)
        # self.batch_norm2 = nn.BatchNorm1d(128)
        # self.layer_norm2 = nn.LayerNorm(128)
        self.layer_norm2 = nn.LayerNorm(256 * 2)
        # self.dropout2 = nn.Dropout(0.5)
        self.dropout2 = nn.Dropout(0.25)

        # self.gru3 = nn.GRU(128, 64, batch_first=True)
        self.gru3 = nn.GRU(256 * 2, 128, batch_first=True, bidirectional=True)
        # self.batch_norm3 = nn.BatchNorm1d(64)
        # self.layer_norm3 = nn.LayerNorm(64)
        self.layer_norm3 = nn.LayerNorm(128 * 2)
        # self.dropout3 = nn.Dropout(0.5)
        self.dropout3 = nn.Dropout(0.25)

        self.gru4 = nn.GRU(128 * 2, 64, batch_first=True, bidirectional=True)
        self.layer_norm4 = nn.LayerNorm(64 * 2)
        self.dropout4 = nn.Dropout(0.25)

        self.fc1 = nn.Linear(64 * 2, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x, _ = self.gru1(x)
        # x = self.batch_norm1(x)
        x = self.layer_norm1(x)
        x = self.dropout1(x)

        x, _ = self.gru2(x)
        # x = self.batch_norm2(x)
        x = self.layer_norm2(x)
        x = self.dropout2(x)

        x, _ = self.gru3(x)
        # x = self.batch_norm3(x)
        x = self.layer_norm3(x)
        x = self.dropout3(x)

        x, _ = self.gru4(x)
        x = self.layer_norm4(x)
        x = self.dropout4(x)

        x = self.fc1(x)
        x = self.relu(x)

        x = self.fc2(x)
        x = self.relu(x)

        x = self.fc3(x)

        return x
