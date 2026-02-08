import os
import time
from datetime import datetime
from src.simple_supabase import SimpleSupabase

# Simple .env loader
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

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

if not URL:
    print("Error: Missing SUPABASE_URL/KEY in .env")
    exit(1)

print("Initializing Supabase Client...")
supabase = SimpleSupabase(URL, KEY)

def trigger_fire(zone_name="Kakamega Forest"):
    print(f"Looking up zone: {zone_name}...")
    zones = supabase.select("zones", "id", {"name": zone_name}, limit=1)
    
    if not zones:
        print(f"Zone '{zone_name}' not found. Defaulting to first available zone.")
        zones = supabase.select("zones", "id", limit=1)
        if not zones:
            print("No zones found. Run setup_db.sql first.")
            return

    zone_id = zones[0]['id']
    
    print(f"Injecting FAKE FIRE event for Zone ID: {zone_id}...")
    
    payload = {
        "zone_id": zone_id,
        "confidence": "high",
        "lat": 0.30, # Inside Kakamega roughly
        "lon": 34.85,
        "detected_at": datetime.utcnow().isoformat()
    }
    
    supabase.insert("fire_events", payload)
    print("SUCCESS: Fake fire event inserted.")
    print("Now run 'python main_agent.py' (or wait for next cycle) to see the ALERT trigger!")

if __name__ == "__main__":
    trigger_fire()
