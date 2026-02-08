# Sauti Porini: Autonomous Forest Fire Agent

Sauti Porini (Swahili for _Voice of the Wilderness_) is a **Marathon Agent** built for the Gemini 3 Hackathon. It provides autonomous, long-running wildfire monitoring for Kenyan forests by fusing satellite data, climate metrics, and AI reasoning.

##  Gemini 3 Integration

This project utilizes **Gemini 3 Pro (`gemini-3-pro-preview`)** as a core reasoning engine. Unlike standard software, Sauti Porini has no hardcoded risk thresholds. Instead:

- **Extended Context**: It analyzes a time-series window of weather and fire data.
- **Autonomous Decisions**: Gemini 3 decides when to escalate states (NORMAL → WATCH → ALERT).
- **Bilingual Alerts**: Automatically generates situational summaries in English and Swahili.

## Quick Start

### 1. Requirements

```bash
pip install fastapi uvicorn supabase google-genai python-dotenv requests
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Database Setup

Run the `setup_db.sql` script in your Supabase SQL Editor to initialize the `zones`, `weather_logs`, and `alert_history` tables.

### 4. Running the System

You need to run two processes simultaneously:

**Terminal 1 (Backend API):**

```bash
python api.py
```

**Terminal 2 (Autonomous Agent):**

```bash
python main_agent.py
```

## Technology Stack

- **AI**: Google Gemini 3 Pro
- **Backend**: Python (FastAPI)
- **Database**: Supabase (PostgreSQL)
- **Data**: NASA FIRMS (Fire Data), Open-Meteo (ERA5 Climate Data)

## Demo

To simulate a fire and see the AI Agent's response:

1. Ensure the agent is running.
2. Run `python demo_trigger.py`.
3. Check the logs in your Agent terminal to see Gemini 3's reasoning and the generated bilingual alerts.
