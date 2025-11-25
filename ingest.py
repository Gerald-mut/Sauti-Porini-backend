import os
import datetime
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

def run_ingest():
    # 1. Setup Supabase
    load_dotenv()
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    GFW_API_KEY = os.environ.get("GFW_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: .env file missing keys.")
        return

    if not GFW_API_KEY:
        print("Error: GFW_API_KEY not found in .env file.")
        return

    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Connection error: {e}")
        return

    # 2. Define Date Range 
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=14)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')

    # 3. Define the "Bounding Box" for Kakamega Forest as a Polygon
    # Note: GeoJSON uses [longitude, latitude] order!
    MIN_LAT = 0.0
    MAX_LAT = 0.5
    MIN_LON = 34.4
    MAX_LON = 35.0

    # Create a polygon geometry (counter-clockwise)
    geometry = {
        "type": "Polygon",
        "coordinates": [[
            [MIN_LON, MIN_LAT],  # bottom-left
            [MAX_LON, MIN_LAT],  # bottom-right
            [MAX_LON, MAX_LAT],  # top-right
            [MIN_LON, MAX_LAT],  # top-left
            [MIN_LON, MIN_LAT]   # close the polygon
        ]]
    }

    # 4.SQL Query
    # Note: Use "results" table and the actual field names from the dataset
    sql_query = (
        f"SELECT latitude, longitude, "
        f"gfw_integrated_alerts__date as alert_date, "
        f"gfw_integrated_alerts__confidence as confidence "
        f"FROM results "
        f"WHERE gfw_integrated_alerts__date >= '{start_date}' "
        f"AND gfw_integrated_alerts__date <= '{end_date}' "
        f"LIMIT 500"
    )

    # 5. The Request
    url = "https://data-api.globalforestwatch.org/dataset/gfw_integrated_alerts/latest/query/json"
    
    headers = {
        "x-api-key": GFW_API_KEY,
        "Content-Type": "application/json"
    }

    # POST body with both SQL and geometry
    payload = {
        "sql": sql_query,
        "geometry": geometry
    }

    print(f"Fetching alerts for box [{MIN_LAT}, {MIN_LON}] to [{MAX_LAT}, {MAX_LON}]...")
    print(f"Date range: {start_date} to {end_date}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        alerts_to_insert = []
        if 'data' in data:
            print(f"Total alerts received: {len(data['data'])}")
            for alert in data['data']:
                # Only keep high confidence
                conf = alert.get('confidence', 'nominal')
                if conf in ['high', 'highest']:
                    alerts_to_insert.append({
                        "alert_date": alert['alert_date'],
                        "lat": alert['latitude'],
                        "lon": alert['longitude'],
                        "confidence_level": conf
                    })

        if alerts_to_insert:
            print(f"Found {len(alerts_to_insert)} high-confidence alerts.")
            # Save to Supabase
            result = supabase.table('satellite_alerts').insert(alerts_to_insert, returning='minimal').execute()
            print("Saved to DB.")
        else:
            print("Success! But no high-confidence alerts found in this area/time.")

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    run_ingest()