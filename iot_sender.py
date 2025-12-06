import json
import time
import random
import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC = "glucose/data"

client = mqtt.Client()
client.connect(BROKER, 1883)

while True:
    glucose_value = round(random.uniform(3.0, 35.0), 1)

    data = {
        "device_id": "windows_sensor_01",
        "glucose": glucose_value,
        "unit": "mmol",
    }

    client.publish(TOPIC, json.dumps(data))
    print("MQTT sent:", data)

    time.sleep(5)
