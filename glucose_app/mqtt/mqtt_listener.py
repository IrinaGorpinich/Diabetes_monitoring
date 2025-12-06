import json
import requests
import paho.mqtt.client as mqtt

DJANGO_URL = "http://127.0.0.1:8000/api/iot-data/"
TOKEN = "ed928b71b1974cddb36795a4cebdbb416af7eeee"
HEADERS = {"Authorization": f"Token {TOKEN}"}

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received MQTT:", data)

        r = requests.post(DJANGO_URL, json=data, headers=HEADERS)
        print("Forwared to Django:", r.status_code)

    except Exception as e:
        print("Error:", e)

client = mqtt.Client()
client.connect("localhost", 1883)
client.subscribe("glucose/data")
client.on_message = on_message

print("MQTT listener started...")
client.loop_forever()



