import os
import time
import random
from datetime import datetime
from .simple_supabase import SimpleSupabase

class SupabaseFetcher:
    def __init__(self, url: str, key: str):
        self.supabase = SimpleSupabase(url, key)

    def fetch_and_store_data(self, zone_id: int):
        """
        Fetches external data (mocked for now) and pushes to Supabase.
        """
        print(f"Fetching data for Zone ID: {zone_id}...")
        
        # 1. Fetch Weather (Mock)
        # Randomly vary slightly to show life
        temp = round(random.uniform(20.0, 35.0), 1) 
        humidity = round(random.uniform(15.0, 60.0), 1)
        
        weather_payload = {
            "zone_id": zone_id,
            "temp": temp,
            "humidity": humidity,
            "recorded_at": datetime.utcnow().isoformat()
        }
        
        try:
            self.supabase.insert("weather_logs", weather_payload)
            print(f"  -> Weather logged: {temp}C, {humidity}%")
        except Exception as e:
            print(f"  [ERROR] Writing weather: {e}")

        # 2. Fetch Fire Events (Real API would go here)
        # valid NASA FIRMS logic would query using the zone bounds
        # For this cycle, we assume NO fire unless injected via demo_trigger.py
        # So we do nothing here for fires in the standard cycle to avoid spamming fake fires.
        
        return weather_payload
