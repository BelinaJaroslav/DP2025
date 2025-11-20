from flask import Flask
import paho.mqtt.client as mqtt
app = Flask(__name__)


@app.route('/')
def hello_world():
    BROKER = "cassandra2.tul.cz"
    PORT = 1883
    TOPIC = "FVE/#"  # subscribe pattern, but MQTT wildcards don’t match suffixes, see below

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code", rc)
        client.subscribe(TOPIC)  # subscribe to all under FVE/

    def on_message(client, userdata, msg):
        if msg.topic.endswith("_TX"):
            print(f"{msg.topic} => {msg.payload.decode(errors='ignore')}")
            # example return
            # FVE/Postolka_TX => {"SoC": 96, "P_PV": 1330, "GRID_LIMIT": 7000, "PRICE_CZK": 3.07, "P_HOME": 61, "P_HOME_L1": 21, "P_HOME_L2": 7, "P_HOME_L3": 33, "P_EPS": 345, "P_GRID": 366, "P_GRID_L1": 298, "P_GRID_L2": 63, "P_GRID_L3": 5, "P_BAT": -906, "PVenergy": 2.3, "PVenergy_T": 468.8, "ToBAT": 9.3, "ToBAT_T": 765.9, "FromBAT": 2.4, "FromBAT_T": 797.2, "SELL_T": 2737.62, "BUY_T": 5380.72, "Consumed": 8.8, "Consumed_T": 1920.4, "Date": "20.11.2025", "Time": "11:46:09"}

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.loop_forever()

    # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run()



