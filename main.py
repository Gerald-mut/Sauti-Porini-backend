from fastapi import FastAPI, Form, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from supabase import create_client, Client
import os
from pydantic import BaseModel
import hashlib
import random
from datetime import datetime
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# 1. Config
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Connect to Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 2. Pydantic Models
class IoTEvent(BaseModel):
    sensor_id: str
    lat: float
    lon: float
    sound_type: str
    confidence: float

# 3. Helper Functions
def generate_hash(data_string):
    return hashlib.sha256(data_string.encode()).hexdigest()

def save_report_to_db(phone, location, description):
    print(f"Saving report from {phone}...")
    try:
        # Generate a fake "Transaction ID" to simulate Blockchain logging
        blockchain_tx = "0x" + generate_hash(description + str(datetime.now()))

        #  Generate a random location near Kakamega Forest center
        # Center is approx 0.23, 34.85
        random_lat = 0.23 + random.uniform(-0.02, 0.02)
        random_lon = 34.85 + random.uniform(-0.02, 0.02)

        data = {
            "phone_number": phone,
            "location_text": location,
            "report_details": description,
            "blockchain_proof": blockchain_tx,
            "lat": random_lat, 
            "lon": random_lon 
        }
        supabase.table("ussd_reports").insert(data).execute()
        print("Report saved successfully!")
        print(f"Blockchain Proof: {blockchain_tx}")
    except Exception as e:
        print(f"Error saving to DB: {e}")

# 4. GET Endpoints (Separated)

@app.get("/satellite-alerts")
async def get_satellite_alerts():
    try:
        response = supabase.table("satellite_alerts").select("*").limit(50).execute()
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.get("/ussd")
async def get_ussd_reports():
    try:
        response = supabase.table("ussd_reports").select("*").limit(20).execute()
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.get("/iot-events")
async def get_iot_events():
    try:
        response = supabase.table("iot_alerts").select("*").limit(20).execute()
        return response.data
    except Exception as e:
        print(f"Error: {e}")
        return []

# 5. POST Endpoints

@app.post("/iot-events")
async def receive_iot(event: IoTEvent):
    try:
        # Add timestamp
        data = event.dict()
        data['detected_at'] = datetime.now().isoformat()
        
        supabase.table("iot_alerts").insert(data).execute()
        return {"status": "logged"}
    except Exception as e:
        print(f"Error saving IoT event: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    background_tasks: BackgroundTasks,
    text: str = Form(default=""), 
    phoneNumber: str = Form(default=""),
    sessionId: str = Form(default=""), 
    serviceCode: str = Form(default="")
):
    parts = text.split("*") if text else []
    response = ""

    if text == "":
        # Initial menu
        response = "CON Welcome to Sauti Porini\n"
        response += "1. Report an Incident\n"
        response += "2. Ranger Hotline"
    elif text == "1":
        # Ask for location
        response = "CON Enter Location of Incident:\n"
        response += "(e.g. Near North Gate)"
    elif text.startswith("1*") and len(parts) == 2:
        # Ask for description
        response = "CON Describe what you see:\n"
        response += "(e.g. 3 trucks, red cabin)"
    elif text.startswith("1*") and len(parts) == 3:
        # User has provided all details
        location_input = parts[1]
        description_input = parts[2]
        background_tasks.add_task(save_report_to_db, phoneNumber, location_input, description_input)
        response = "END Thank you. Report received.\n"
        response += "Rangers have been notified."
    elif text == "2":
        response = "END Ranger Hotline: 0800-123-456"
    else:
        response = "END Invalid input. Please try again."

    return response