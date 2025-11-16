from fastapi import FastAPI, Form, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 1. Config
load_dotenv()
app = FastAPI()

# Connect to Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 2. Helper Function to Save to DB
def save_report_to_db(phone, location, description):
    print(f"Saving report from {phone}...")
    try:
        data = {
            "phone_number": phone,
            "location_text": location,
            "report_details": description
        }
        supabase.table("ussd_reports").insert(data).execute()
        print("Report saved successfully!")
    except Exception as e:
        print(f"Error saving to DB: {e}")

# 3. The USSD Endpoint
# Africa's Talking sends form fields: sessionId, serviceCode, phoneNumber, text
@app.post("/ussd", response_class=PlainTextResponse)
async def ussd_callback(
    background_tasks: BackgroundTasks,
    text: str = Form(default=""), 
    phoneNumber: str = Form(default=""),
    sessionId: str = Form(default=""), 
    serviceCode: str = Form(default="")
):
    # Split the user's input text by '*' to track their path
    # Example: "1*Near River*Big trucks" -> ['1', 'Near River', 'Big trucks']
    parts = text.split("*") if text else []
    
    response = ""

    # --- LEVEL 0: Main Menu ---
    if text == "":
        response = "CON Welcome to ForestGuard Kenya\n"
        response += "1. Report Illegal Logging\n"
        response += "2. Contact Ranger"

    # --- LEVEL 1: Location Input ---
    elif text == "1":
        response = "CON Enter Location of Incident:\n"
        response += "(e.g. Near Kakamega North Gate)"

    # --- LEVEL 2: Description Input ---
    # User has entered "1" then "Location"
    elif len(parts) == 2 and parts[0] == "1":
        response = "CON Describe what you see:\n"
        response += "(e.g. 3 trucks, red cabin)"

    # --- LEVEL 3: Final Step (Save) ---
    # User has entered "1" -> "Location" -> "Description"
    elif len(parts) == 3 and parts[0] == "1":
        location_input = parts[1]
        description_input = parts[2]

        # Save to DB in the background so the user gets a fast reply
        background_tasks.add_task(save_report_to_db, phoneNumber, location_input, description_input)
        
        response = "END Thank you. Report received.\n"
        response += "Rangers have been notified."

    # --- Exit Option ---
    elif text == "2":
        response = "END Ranger Hotline: 0800-123-456"

    else:
        response = "END Invalid input. Please try again."

    return response