import requests
import time
import random

URL = "http://192.168.X.X:8000/api/iot-data/"
TOKEN = "ed928b71b1974cddb36795a4cebdbb416af7eeee"
HEADERS = {
    "Authorization": f"Token {TOKEN}"
}

while True:
    glucose_value = round(random.uniform(3.0, 35.0), 1)

    data = {
        "device_id": "windows_sensor_01",
        "glucose": glucose_value,
        "unit": "mmol",
    }

    r = requests.post(URL, json=data, headers=HEADERS)
    print("Sent:", data, "Response:", r.status_code)

    time.sleep(5)