import random
import time
import requests

API_KEY = "d5454ab0bc0efa26aace3cfbeb59393b"   # API key
CITY = "Dublin"

def get_real_sensor_reading():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    r = requests.get(url).json()

    # If API fails → return simulated fallback
    if "main" not in r:
        print("REAL SENSOR ERROR:", r)
        return {
            "temperature": round(random.uniform(25, 45), 2),
            "humidity": round(random.uniform(35, 75), 2)
        }

    return {
        "temperature": r["main"]["temp"],
        "humidity": r["main"]["humidity"]
    }

def generate_reading(machine_id):
    """90% simulated, 10% real online sensor"""
    # 10% chance → real sensor
    if random.random() < 0.1:
        real = get_real_sensor_reading()
        return {
            "machineId": machine_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "energy": round(random.uniform(12, 20), 2),  # simulated
            "temperature": real["temperature"],          # REAL
            "humidity": real["humidity"],                # REAL
            "load": round(random.uniform(0.5, 1.0), 2),  # simulated
            "source": "real"
        }

    # 90% simulated
    return {
        "machineId": machine_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "energy": round(random.uniform(10, 25), 2),
        "temperature": round(random.uniform(25, 45), 2),
        "humidity": round(random.uniform(35, 75), 2),
        "load": round(random.uniform(0.4, 1.0), 2),
        "source": "simulated"
    }

if __name__ == "__main__":
    while True:
        print(generate_reading("M1"))
        time.sleep(2)