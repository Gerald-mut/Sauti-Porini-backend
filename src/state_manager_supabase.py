from datetime import datetime
from .simple_supabase import SimpleSupabase

class SupabaseStateManager:
    def __init__(self, supabase: SimpleSupabase):
        self.supabase = supabase

    def analyze_zone(self, zone_id: int, zone_name: str, ai_analyzer):
        """
        Orchestrates the analysis by gathering data and asking Gemini 3 to decide.
        """
        print(f"Analyzing Zone: {zone_name} (ID: {zone_id})...")

        # 1. Get Current Status
        zone_info = self.supabase.select("zones", "current_status", filters={"id": zone_id})
        current_status = zone_info[0]['current_status'] if zone_info else "NORMAL"

        # 2. Get Weather History (Last 3 points for trend)
        weather_history = self.supabase.select(
            table="weather_logs",
            filters={"zone_id": zone_id},
            order="recorded_at.desc",
            limit=3
        )
        
        # 3. Get Recent Fire Events
        fire_events = self.supabase.select(
            table="fire_events",
            filters={"zone_id": zone_id},
            order="detected_at.desc",
            limit=5
        )
        
        # 4. Ask Gemini 3 to Decide
        decision = ai_analyzer.evaluate_risk(zone_name, current_status, weather_history, fire_events)
        
        new_status = decision['new_status']
        print(f"  -> Gemini Decision: {new_status} | {decision['reasoning']}")

        # 5. Update Zone if Changed OR if it's an active ALERT (keep timestamp fresh)
        if new_status != current_status or new_status == "ALERT":
            self.supabase.update(
                table="zones", 
                data={"current_status": new_status, "last_updated": datetime.utcnow().isoformat()},
                filters={"id": zone_id}
            )
            # Log the alert history
            ai_analyzer.save_alert(zone_id, decision)
        
        return new_status
