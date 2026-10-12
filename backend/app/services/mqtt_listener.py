import json
from datetime import datetime

import paho.mqtt.client as mqtt

from app.config import MQTT_HOST, MQTT_PORT
from app.db import SessionLocal
from app.models import Alert, Event


def on_message(client, userdata, msg):
    try:
        evt = json.loads(msg.payload)
        ts = datetime.fromisoformat(evt["timestamp"])
        with SessionLocal() as db:
            db.add(Event(timestamp=ts, event_type=evt["event_type"],
                         src_ip=evt.get("src_ip"), dest_ip=evt.get("dest_ip"), raw=evt))
            if evt["event_type"] == "alert":
                db.add(Alert(timestamp=ts, signature=evt["alert"]["signature"],
                             severity=evt["alert"]["severity"],
                             src_ip=evt.get("src_ip"), dest_ip=evt.get("dest_ip"), raw=evt))
            db.commit()
    except Exception as exc:  # keep the listener alive on a bad message
        print("failed to process message:", exc)


if __name__ == "__main__":
    c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    c.on_message = on_message
    c.connect(MQTT_HOST, MQTT_PORT)
    c.subscribe("ids/#")
    c.loop_forever()
