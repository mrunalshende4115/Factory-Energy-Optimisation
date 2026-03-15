import json
import time
from sensor_sim import generate_reading

TEMP_ALERT_THRESHOLD = 40.0
LOAD_ALERT_THRESHOLD = 0.9

def edge_process(raw):
    """Add derived metrics + alerts"""
    r = raw.copy()
    r["powerFactor"] = round(r["load"] * 0.95, 2)
    r["isTempHigh"] = r["temperature"] > TEMP_ALERT_THRESHOLD
    r["isLoadHigh"] = r["load"] > LOAD_ALERT_THRESHOLD
    r["isAlert"] = r["isTempHigh"] or r["isLoadHigh"]
    r["state"] = "ALERT" if r["isAlert"] else "RUNNING"
    return r

if __name__ == "__main__":
    while True:
        raw = generate_reading("M1")
        processed = edge_process(raw)
        print("EDGE OUTPUT:\n", json.dumps(processed, indent=2))
        time.sleep(2)