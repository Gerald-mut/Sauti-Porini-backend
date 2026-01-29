import os
import time
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

print("Initializing Supabase Client...")
supabase = create_client(URL, KEY)

def trigger_fire(zone_name="Kakamega Forest"):
    print(f"Looking up zone: {zone_name}...")
    res = supabase.table("zones").select("id").eq("name", zone_name).execute()
    
    if not res.data:
        print(f"Zone '{zone_name}' not found. Defaulting to first available zone.")
        res = supabase.table("zones").select("id").limit(1).execute()
        if not res.data:
            print("No zones found. Run setup_db.sql first.")
            return

    zone_id = res.data[0]['id']
    
    print(f"Injecting FAKE FIRE event for Zone ID: {zone_id}...")
    
    payload = {
        "zone_id": zone_id,
        "confidence": "high",
        "lat": 0.30, # Inside Kakamega roughly
        "lon": 34.85,
        "detected_at": datetime.utcnow().isoformat()
    }
    
    supabase.table("fire_events").insert(payload).execute()
    print("SUCCESS: Fake fire event inserted.")
    print("Now run 'python main_agent.py' (or wait for next cycle) to see the ALERT trigger!")

if __name__ == "__main__":
    trigger_fire()
