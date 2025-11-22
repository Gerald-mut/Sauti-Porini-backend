# Sauti Porini - Backend API

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

## Overview

The **Sauti Porini Backend** serves as the intelligence core for the ForestGuard system. It is a high-performance asynchronous API built with FastAPI that ingests real-time data from multiple streams (Satellite, IoT, USSD), processes them for verification using cryptographic hashing, and stores them in a geospatial database.

## Features

- **Multi-Modal Ingestion:**
  - **Satellite:** Fetches deforestation alerts from Global Forest Watch.
  - **USSD:** Handles callbacks from Africa's Talking for offline citizen reporting.
  - **IoT:** Ingests acoustic sensor data (chainsaw detection) via MQTT/HTTP.
- **The Truth Ledger:** Automatically generates SHA-256 hashes for every incoming report to ensure data immutability and auditability.
- **Geospatial Storage:** Stores all alerts with precise coordinates in Supabase (PostgreSQL).
- **Real-Time Simulation:** Includes modules to simulate IoT sensor arrays and M-PESA donations for hackathon demonstrations.

## Tech Stack

- **Framework:** FastAPI (Python)
- **Server:** Uvicorn
- **Database:** Supabase (PostgreSQL)
- **Integrations:** Africa's Talking (USSD/SMS), Global Forest Watch API
- **Validation:** Pydantic

## Getting Started

### Prerequisites

- Python 3.8+
- A Supabase account and project URL/Key.
- An Africa's Talking Sandbox account (for USSD testing).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/sauti-porini.git](https://github.com/yourusername/sauti-porini.git)
   cd sauti-porini/backend
2. **Create a virtual environment** 
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows: venv\Scripts\activate
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Environment Configuration**
   Create a .env file in the root directory
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   
5. **Running the Server**
  Start the development server with hot-reloading
  ```Bash
  uvicorn main:app --reload
  ```
  The API will be available at http://127.0.0.1:8000.
## 6. **API Endpoints**

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/dashboard-data` | Retrieves aggregated alerts (Satellite, USSD, IoT) for the frontend. |
| `POST` | `/ussd` | Webhook callback for Africa's Talking USSD sessions. |
| `POST` | `/iot-event` | Endpoint for acoustic sensor arrays to push detection events. |


### Author & License

**Owner:** Gerald Muteru

This project is proprietary software. All rights reserved.
Unauthorized copying of this file, via any medium, is strictly prohibited.
