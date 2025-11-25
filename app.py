import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# 1. Setup & Config
st.set_page_config(page_title="Sauti Porini", layout="wide")
load_dotenv()

# 2. Connect to Supabase
@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.stop()

# 3. Fetch Data
def get_data():
    # Fetch Satellite Alerts
    alerts_response = supabase.table("satellite_alerts").select("*").execute()
    alerts_df = pd.DataFrame(alerts_response.data)
    
    # Fetch USSD Reports 
    ussd_response = supabase.table("ussd_reports").select("*").execute()
    ussd_df = pd.DataFrame(ussd_response.data)
    
    return alerts_df, ussd_df

alerts_df, ussd_df = get_data()

# 4. Layout - Header
st.title("Sauti Porini Kenya: Command Center")
st.markdown("Real-time monitoring of **Kakamega Forest** combining satellite intelligence and community reporting.")

col1, col2, col3 = st.columns(3)
col1.metric("Satellite Alerts (Last 14 Days)", len(alerts_df))
col2.metric("Community Reports (Today)", len(ussd_df))
col3.metric("Active Rangers", "4")

# 5. Map Construction
# Center on Kakamega Forest
m = folium.Map(location=[0.23, 34.85], zoom_start=12)

# Layer 1: Satellite Alerts (Red Circles)
if not alerts_df.empty:
    for _, row in alerts_df.iterrows():
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=300,
            color="#FF4B4B",
            fill=True,
            fill_color="#FF4B4B",
            fill_opacity=0.6,
            tooltip=f"<b>Satellite Alert</b><br>Date: {row['alert_date']}<br>Confidence: {row['confidence_level']}"
        ).add_to(m)

# Layer 2: USSD Reports (Blue Pins) - Will appear later
if not ussd_df.empty:
    for _, row in ussd_df.iterrows():
        folium.Marker(
            location=[0.23, 34.85], # Demo Hack: All USSD reports pin to center for now
            popup=f"Report: {row['report_details']}",
            icon=folium.Icon(color="blue", icon="user")
        ).add_to(m)

# 6. Display Map
st_folium(m, width="100%", height=500)

# 7. Data Tables (for debugging/demo)
st.caption("Live Data Feed")
st.dataframe(alerts_df)