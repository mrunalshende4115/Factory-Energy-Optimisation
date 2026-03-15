import time
import json
import requests
import boto3
from sensor_sim import generate_reading
from edge_node import edge_process


API_URL = "https://p41xpcerk1.execute-api.us-east-1.amazonaws.com/prod/ingest"
FOG_NODE_ID = "fog-1"
MACHINES = ["M1", "M2", "M3"]


sns = boto3.client("sns", region_name="us-east-1")
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:817321140247:machine-energy-alerts"
ENERGY_THRESHOLD = 50  # adjust as needed

def send_alert(machine_id, energy_value):
    """Send SNS email alert when energy spikes."""
    message = (
        f"⚠️ ENERGY SPIKE DETECTED\n"
        f"Machine: {machine_id}\n"
        f"Energy: {energy_value}\n"
        f"Fog Node: {FOG_NODE_ID}"
    )

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="Machine Energy Alert"
    )

    print(f"ALERT SENT for {machine_id}: {energy_value}")



sqs = boto3.client("sqs", region_name="us-east-1")
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/817321140247/factory-iot-queue"


def send_to_sqs(reading):
    """Send each processed reading to SQS."""
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(reading)
    )
    print("Sent to SQS:", reading)



def send_batch_to_api(batch):
    payload = {
        "fogNodeId": FOG_NODE_ID,
        "readings": batch
    }
    print("FOG SENDING BATCH TO API:\n", json.dumps(payload, indent=2))
    r = requests.post(API_URL, json=payload)
    print("FOG RESPONSE:", r.status_code, r.text)



if __name__ == "__main__":
    batch = []

    while True:
        for mid in MACHINES:
            raw = generate_reading(mid)
            processed = edge_process(raw)

            
            energy = processed.get("energy", 0)

            if energy > ENERGY_THRESHOLD:
                send_alert(mid, energy)

            
            send_to_sqs(processed)

            
            batch.append(processed)

        
        if len(batch) >= 5:
            send_batch_to_api(batch)
            batch = []

        time.sleep(2)