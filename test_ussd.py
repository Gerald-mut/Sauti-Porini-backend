import requests

# URL of your local FastAPI backend
url = "http://127.0.0.1:8000/ussd"

# 1. Simulate "Dialing" (*384#)
print("--- Step 1: Dialing ---")
payload = {"text": "", "phoneNumber": "+254700000000", "sessionId": "12345", "serviceCode": "*384#"}
response = requests.post(url, data=payload)
print(f"Server says:\n{response.text}\n")

# 2. Simulate Selecting "1" (Report)
print("--- Step 2: User sends '1' ---")
payload["text"] = "1"
response = requests.post(url, data=payload)
print(f"Server says:\n{response.text}\n")

# 3. Simulate Entering Location
print("--- Step 3: User enters Location ---")
payload["text"] = "1*Near Dark Cave"
response = requests.post(url, data=payload)
print(f"Server says:\n{response.text}\n")

# 4. Simulate Entering Description (Final)
print("--- Step 4: User enters Details ---")
payload["text"] = "1*Near Dark Cave*Two men with axes"
response = requests.post(url, data=payload)
print(f"Server says:\n{response.text}\n")