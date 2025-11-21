import requests
import time
import random

# Your local or ngrok URL
API_URL = "http://127.0.0.1:8000/iot-event" 

# 3 Sensors fixed in Kakamega
SENSORS = [
    {"id": "S-01", "lat": 0.23, "lon": 34.85},
    {"id": "S-02", "lat": 0.25, "lon": 34.82},
    {"id": "S-03", "lat": 0.21, "lon": 34.87}
]

print("Forest Ears: IoT Network Active...")

while True:
    # Pick a random sensor
    sensor = random.choice(SENSORS)
    
    # 10% chance to hear a chainsaw
    if random.random() < 0.10:
        event = {
            "sensor_id": sensor["id"],
            "lat": sensor["lat"],
            "lon": sensor["lon"],
            "sound_type": "chainsaw",
            "confidence": round(random.uniform(0.8, 0.99), 2)
        }
        try:
            print(f"{sensor['id']} detected CHAINSAW! Sending alert...")
            requests.post(API_URL, json=event)
        except:
            print("Server offline.")
            
    time.sleep(5) # Wait 5 seconds