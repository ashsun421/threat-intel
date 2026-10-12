import json
import os
import time

import paho.mqtt.client as mqtt

from app.config import EVE_PATH, MQTT_HOST, MQTT_PORT


def follow(path):
    while not os.path.exists(path):
        time.sleep(1)
    with open(path) as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line


if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(MQTT_HOST, MQTT_PORT)
    client.loop_start()
    for line in follow(EVE_PATH):
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        client.publish(f"ids/{evt.get('event_type', 'unknown')}", json.dumps(evt))
