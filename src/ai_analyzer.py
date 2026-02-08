from .simple_supabase import SimpleSupabase
from google import genai
import json

class AIAnalyzer:
    def __init__(self, supabase: SimpleSupabase, gemini_key: str):
        self.supabase = supabase
        self.gemini_key = gemini_key
        self.model_name = "gemini-3-pro-preview"
        if gemini_key and gemini_key != "your_google_gemini_key":
            try:
                self.client = genai.Client(api_key=gemini_key)
                self.has_ai = True
            except:
                self.has_ai = False
        else:
            self.has_ai = False

    def evaluate_risk(self, zone_name: str, current_status: str, weather_history: list, fire_events: list):
        """
        Uses Gemini 3 Pro to analyze temporal patterns and decide the zone status.
        Returns: {
            "new_status": "NORMAL" | "WATCH" | "ALERT",
            "reasoning": "...",
            "message_en": "...",
            "message_sw": "..."
        }
        """
        if not self.has_ai:
            return self._fallback_logic(current_status, weather_history, fire_events)

        print(f"  [Gemini 3] Reasoning on {len(weather_history)} weather points & {len(fire_events)} fires...")

        # Construct Context
        context = {
            "zone": zone_name,
            "current_status": current_status,
            "weather_history": weather_history, # List of {temp, humidity, time}
            "fire_detections": fire_events,   # List of {lat, lon, confidence, time}
            "rule": "High Temp (>30C) + Low Humidity (<20%) = Fire Risk. Actual Fire = ALERT."
        }
        
        prompt = f"""
        Role: Intelligent Forest Monitoring Agent (Sauti Porini).
        Task: Analyze the environmental data history and decide the Zone Status.
        
        Input Context:
        {json.dumps(context, indent=2, default=str)}
        
        Instructions:
        1. Contextual Reasoning: Look at the trend in weather history. active fires immediately escalate to ALERT.
        2. Escalation: 
           - If Fires Detected -> ALERT.
           - If Temp is rising (>28C) and Humidity dropping (<25%) consistently -> WATCH.
           - Otherwise -> NORMAL.
        3. Output: Return a JSON object ONLY.
           {{
             "new_status": "NORMAL" | "WATCH" | "ALERT",
             "reasoning": "Brief explanation of why (referencing trends)",
             "message_en": "Short SMS alert (max 160 chars).",
             "message_sw": "Short SMS alert in Swahili (max 160 chars)."
           }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name, 
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return json.loads(response.text)
        except Exception as e:
            # print(f"  [Gemini 3 Error] {e}") # Silenced for demo
            return self._fallback_logic(current_status, weather_history, fire_events)

    def _fallback_logic(self, current_status, weather_history, fire_events):
        # Basic heuristic fallback
        new_status = "NORMAL"
        last_weather = weather_history[0] if weather_history else {"temp": 25, "humidity": 50}
        
        if fire_events:
            new_status = "ALERT"
        elif last_weather['temp'] > 28 and last_weather['humidity'] < 25:
            new_status = "WATCH"
            
        return {
            "new_status": new_status,
            "reasoning": "Fallback logic: Threshold check.",
            "message_en": f"Status: {new_status}. Temp: {last_weather['temp']}C",
            "message_sw": f"Hali: {new_status}. Joto: {last_weather['temp']}C"
        }

    def save_alert(self, zone_id, decision_data):
        # Only save meaningful alerts or status changes
        if decision_data['new_status'] == "NORMAL":
            return

        data = {
            "zone_id": zone_id,
            "risk_level": decision_data['new_status'],
            "message_en": decision_data['message_en'],
            "message_sw": decision_data['message_sw'],
            "created_at": "now()"
        }
        self.supabase.insert("alert_history", data)
        print(f"  -> Alert Logged: {decision_data['new_status']}")
