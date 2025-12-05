import numpy as np
import torch
import torch.nn as nn
import joblib
from sklearn.preprocessing import MinMaxScaler
data = np.random.uniform(4.0, 13.0, size=(100, 1))

scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

joblib.dump(scaler, "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/ml/scaler_test.pkl")
print("Scaler saved as scaler_test.pkl")

SEQ_LEN = 10
X, y = [], []
for i in range(len(data_scaled) - SEQ_LEN):
    X.append(data_scaled[i:i+SEQ_LEN])
    y.append(data_scaled[i+SEQ_LEN])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

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

model = GlucoseLSTM()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(200):
    optimizer.zero_grad()
    outputs = model(torch.tensor(X))
    loss = criterion(outputs, torch.tensor(y))
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 50 == 0:
        print(f"Epoch {epoch + 1}, Loss: {loss.item():.4f}")

torch.save(model.state_dict(), "/Users/gorpinicirina/Documents/diabetes_monitoring/glucose_app/ml/lstm_weights.pth")
print("Model weights saved as lstm_weights.pth")