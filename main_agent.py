import time
import os
from src.simple_supabase import SimpleSupabase
from src.fetchers_supabase import SupabaseFetcher
from src.state_manager_supabase import SupabaseStateManager
from src.ai_analyzer import AIAnalyzer

# Simple .env loader to avoid dependencies
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

if not URL or "your_supabase" in URL:
    print("CRITICAL: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Initialize
supabase = SimpleSupabase(URL, KEY)
fetcher = SupabaseFetcher(URL, KEY)
manager = SupabaseStateManager(supabase)
ai = AIAnalyzer(supabase, os.getenv("GEMINI_API_KEY"))

def run_agent():
    print("--- Sauti Porini Agent Running (Requests Mode) ---")
    
    # Get all zones
    zones = supabase.select("zones", "id, name")
    
    if not zones:
        print("No zones found! Did you run setup_db.sql in Supabase?")
        return

    for zone in zones:
        zid = zone['id']
        zname = zone['name']
        print(f"\nProcessing {zname} (ID: {zid})...")
        
        # 1. Fetch & Store
        fetcher.fetch_and_store_data(zid)

        # 2. Analyze State (Gemini 3 Reasoning)
        manager.analyze_zone(zid, zname, ai)

        # 3. AI Alert is now handled inside analyze_zone

    print("\nCycle complete. Waiting 15 minutes...")

if __name__ == "__main__":
    try:
        while True:
            try:
                run_agent()
            except Exception as e:
                print(f"Agent Loop Error: {e}")
            # CHANGED: Sleep for 15 seconds instead of 15 minutes for rapid testing/demo
            time.sleep(15) 
    except KeyboardInterrupt:
        print("\n[STOP] Agent execution stopped by user. Goodbye!")
