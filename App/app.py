from flask import Flask
import threading
import json
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import os

app = Flask(__name__)

# --- Mongo Setup ---
mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/fve")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["fve"]
collection = db["measurements"]
#prediction_collection = db["predictions"]


# --- MQTT Setup ---
BROKER = os.environ.get("MQTT_BROKER", "cassandra2.tul.cz")
PORT = int(os.environ.get("MQTT_PORT", 1883))
TOPIC = "FVE/#"


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT with result code:", rc)
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    if topic.endswith("_TX"):
        print(f"{topic} => {payload}")

        try:
            data = json.loads(payload)
        except Exception:
            print("Invalid JSON, storing raw payload.")
            data = {"raw_payload": payload}

        doc = {
            "topic": topic,
            "data": data
        }

        collection.insert_one(doc)
        print("Saved to MongoDB")


def mqtt_worker():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()


# Start MQTT in background
threading.Thread(target=mqtt_worker, daemon=True).start()


@app.route("/")
def home():
    return "MQTT Listener Running. Data is stored in MongoDB."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
