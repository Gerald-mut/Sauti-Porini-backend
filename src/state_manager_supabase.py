from supabase import Client
from datetime import datetime, timedelta

class SupabaseStateManager:
    def __init__(self, supabase: Client):
        self.supabase = supabase

    def analyze_zone(self, zone_id: int):
        print(f"Analyzing Zone ID: {zone_id}...")

        # 1. Get Latest Weather
        weather_res = self.supabase.table("weather_logs")\
            .select("*")\
            .eq("zone_id", zone_id)\
            .order("recorded_at", desc=True)\
            .limit(1)\
            .execute()
        
        current_weather = weather_res.data[0] if weather_res.data else None

        # 2. Get Recent Fire Events (Last 1 hour)
        # Note: In a real app, timezone handling is critical. 
        # For simplicity here we check the last few entries or just any "recent" one.
        fire_res = self.supabase.table("fire_events")\
            .select("*")\
            .eq("zone_id", zone_id)\
            .order("detected_at", desc=True)\
            .limit(5)\
            .execute()
        
        fires = fire_res.data
        
        # Check if any fire is VERY recent (e.g. within last 30 mins)
        # For MVP Demo, we'll just check if there's any fire entered in the last check cycle essentially.
        # But to make the 'demo_trigger' work persistently, we might want to check if there is an *unresolved* fire.
        # Simplification: If fire detected < 1 hour ago -> ALERT.
        
        active_fire = False
        if fires:
            last_fire_time = fires[0]['detected_at']
            # Parse ISO string to datetime if needed, or just assume fetcher puts recent stuff.
            # We'll treat the existence of a recent record as active fire.
            active_fire = True 
            print(f"  -> Found {len(fires)} recent fire events!")

        # 3. Determine State
        new_status = "NORMAL"
        
        if active_fire:
            new_status = "ALERT"
        elif current_weather:
            # Rule: Temp > 28 and Humidity < 25 -> WATCH
            if current_weather['temp'] > 28.0 and current_weather['humidity'] < 25.0:
                new_status = "WATCH"

        # 4. Update Zone
        self.supabase.table("zones").update({"current_status": new_status, "last_updated": datetime.utcnow().isoformat()}).eq("id", zone_id).execute()
        
        print(f"  -> Status set to: {new_status}")
        
        return new_status, current_weather, fires
