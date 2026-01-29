import time
import os
from dotenv import load_dotenv
from supabase import create_client
from src.fetchers_supabase import SupabaseFetcher
from src.state_manager_supabase import SupabaseStateManager
from src.ai_analyzer import AIAnalyzer

# Load env
load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

if not URL or "your_supabase" in URL:
    print("CRITICAL: SUPABASE_URL and SUPABASE_KEY must be set in .env")
    exit(1)

# Initialize
supabase = create_client(URL, KEY)
fetcher = SupabaseFetcher(URL, KEY)
manager = SupabaseStateManager(supabase)
ai = AIAnalyzer(supabase, os.getenv("GEMINI_API_KEY"))

def run_agent():
    print("--- Sauti Porini Agent Running ---")
    
    # Get all zones
    zones_res = supabase.table("zones").select("id, name").execute()
    zones = zones_res.data
    
    if not zones:
        print("No zones found! Did you run setup_db.sql in Supabase?")
        return

    for zone in zones:
        zid = zone['id']
        zname = zone['name']
        print(f"\nProcessing {zname} (ID: {zid})...")
        
        # 1. Fetch & Store
        # fetcher.fetch_and_store_data(zid) 
        # COMMENTED OUT: We move this inside the loop to ensure logic order.
        # Actually proper agent flow: Fetch -> Store -> Analyze.
        # The fetcher stores it.
        fetcher.fetch_and_store_data(zid)

        # 2. Analyze State
        status, weather, fires = manager.analyze_zone(zid)

        # 3. AI Alert if needed
        if status in ["WATCH", "ALERT"]:
            ai.generate_and_save_alert(zid, status, weather, fires)

    print("\nCycle complete. Waiting 15 minutes...")

if __name__ == "__main__":
    while True:
        try:
            run_agent()
        except Exception as e:
            print(f"Agent Loop Error: {e}")
        time.sleep(900)
