from supabase import Client
import google.generativeai as genai

class AIAnalyzer:
    def __init__(self, supabase: Client, gemini_key: str):
        self.supabase = supabase
        self.gemini_key = gemini_key
        if gemini_key and gemini_key != "your_google_gemini_key":
            try:
                genai.configure(api_key=gemini_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro') # Using 1.5 as proxy for 3
                self.has_ai = True
            except:
                self.has_ai = False
        else:
            self.has_ai = False

    def generate_and_save_alert(self, zone_id: int, status: str, weather: dict, fires: list):
        if status == "NORMAL":
            return # No alert needed for normal

        print("Generating AI Alert Summary...")
        
        # MOCK FALLBACK if no key
        if not self.has_ai:
            msg_sw = f"HABARI: Hali ya {status} imegunduliwa. Joto: {weather.get('temp')}C."
            msg_en = f"NOTICE: {status} condition detected. Temp: {weather.get('temp')}C."
            if status == "ALERT":
                msg_sw = "HATARI: Moto umegunduliwa msituni! Chukua tahadhari."
                msg_en = "DANGER: Fire detected in the forest! Take caution."
            
            self._save(zone_id, status, msg_en, msg_sw)
            return

        # REAL GEN AI
        prompt = f"""
        Role: Forest Ranger Assistant.
        Task: Write a very short SMS alert (max 160 chars per language) in Swahili and English.
        Context:
        - Zone Status: {status}
        - Weather: Temp {weather.get('temp')}C, Humidity {weather.get('humidity')}%
        - Fire Events: {len(fires)} recent detections.
        
        Output format:
        Swahili: [Message]
        English: [Message]
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            # Basic parsing (naive)
            lines = text.split('\n')
            msg_sw = next((line for line in lines if "Swahili" in line), "Tahadhari ya Moto (AI Generated)").replace("Swahili:", "").strip()
            msg_en = next((line for line in lines if "English" in line), "Fire Alert (AI Generated)").replace("English:", "").strip()
            
            self._save(zone_id, status, msg_en, msg_sw)
            
        except Exception as e:
            print(f"AI Error: {e}")

    def _save(self, zone_id, level, msg_en, msg_sw):
        data = {
            "zone_id": zone_id,
            "risk_level": level,
            "message_en": msg_en,
            "message_sw": msg_sw,
            "created_at": "now()"
        }
        self.supabase.table("alert_history").insert(data).execute()
        print(f"  -> Alert saved to history: {msg_en}")
