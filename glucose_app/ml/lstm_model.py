import numpy as np
import torch
import torch.nn as nn
import joblib

scaler = joblib.load("/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/ml/scaler_test.pkl")

SEQ_LEN = 10
DEVICE = torch.device("cpu")

class GlucoseLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=32, output_size=1):
        super(GlucoseLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc1 = nn.Linear(hidden_size, 16)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(16, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.fc1(out)
        out = self.relu(out)
        out = self.fc2(out)
        return out

model = GlucoseLSTM().to(DEVICE)

model.load_state_dict(torch.load("/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/ml/lstm_weights.pth",  map_location=DEVICE))
model.eval()

def prepare_sequence(data):
    data = np.array(data).reshape(-1, 1)
    data = scaler.transform(data)
    X = []
    for i in range(len(data) - SEQ_LEN):
        X.append(data[i:i + SEQ_LEN])
    return np.array(X)

def predict_next_value(values):
    seq = prepare_sequence(values)
    if len(seq) == 0:
        return None, "not_enough_data"

    x = torch.tensor(seq[-1], dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        pred_scaled = model(x).item()

    pred = scaler.inverse_transform([[pred_scaled]])[0][0]

    if pred < 3.5:
        risk = "Hypoglycemia risk"
    elif pred > 10:
        risk = "Hyperglycemia risk"
    else:
        risk = "Normal"
    return pred, risk