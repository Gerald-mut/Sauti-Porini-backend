from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.simple_supabase import SimpleSupabase
import os

# Manual .env load
def load_env_file():
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env_file()

app = FastAPI(title="Sauti Porini Backend")

# Enable CORS for React Frontend (running on different port usually)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
if not URL:
    raise RuntimeError("SUPABASE_URL not set in .env")

supabase = SimpleSupabase(URL, KEY)

@app.get("/")
def read_root():
    return {"status": "Sauti Porini Backend Operational"}

@app.get("/satellite-alerts")
def get_satellite_alerts():
    """
    Returns fire events from Supabase formatted as satellite alerts.
    """
    try:
        # Fetch recent fire events
        # We fetch columns needed + map them
        fires = supabase.select("fire_events", "*", order="detected_at.desc", limit=200)
        
        results = []
        for fire in fires:
            # Map Supabase DB columns to Frontend API Contract
            results.append({
                "id": str(fire["id"]),
                "lat": fire["lat"],
                "lon": fire["lon"],
                "alert_date": fire["detected_at"].split("T")[0], # simplified date
                "confidence_level": fire.get("confidence", "nominal")
            })
        return results
    except Exception as e:
        print(f"Error fetching fires: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ussd")
def get_ussd_reports():
    """
    Returns citizen reports.
    NOTE: Using 'fire_events' as mock source if 'ussd_reports' table doesn't exist
    since we haven't created that table in the schema yet.
    """
    try:
        # In a real scenario, this would query a 'ussd_reports' table.
        # For MVP, we return an empty list or mock data if requested, 
        # but to satisfy the contract let's return a static example if no table exists
        # or just return empty list.
        return [
             {
                "id": "mock_rep_1",
                "lat": 0.32,
                "lon": 34.80,
                "received_at": "2023-10-27T10:00:00Z",
                "phone_number": "+254700000000",
                "report_details": "Suspicious smoke seen near river",
                "location_text": "Kakamega Mock Location",
                "blockchain_proof": "0x123abc..."
             }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/iot-events")
def get_iot_events():
    """
    Returns acoustic sensor triggers.
    """
    # Static mock for MVP
    return [
        {
        "id": "sensor_mock_99",
        "lat": 0.31,
        "lon": 34.82,
        "detected_at": "2023-10-27T11:30:00Z",
        "sensor_id": "SN-MOCK-01",
        "sound_type": "chainsaw"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 allows external access, port 8000 matches frontend config
    uvicorn.run(app, host="0.0.0.0", port=8000)
