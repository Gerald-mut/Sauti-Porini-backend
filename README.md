# Sauti Porini (Supabase Edition)

Sauti Porini wildfire monitoring system integrated with Supabase.

## 1. Setup

### Prerequisites

- Python 3.9+
- A Supabase project (Free Tier is fine)
- Google Gemini API Key (Optional)

### Installation

```bash
pip install supabase google-generativeai python-dotenv
```

### Database Initialization

1.  Go to your **Supabase Dashboard** -> **SQL Editor**.
2.  Open `setup_db.sql` from this project.
3.  Copy and Paste the content into the editor and click **Run**.
    - This creates tables: `zones`, `weather_logs`, `fire_events`, `alert_history`.
    - It seeds "Kakamega Forest".

### Configuration

1.  Open `.env`.
2.  Fill in your keys:
    ```env
    SUPABASE_URL=https://xyz.supabase.co
    SUPABASE_KEY=eyJh... (Your 'anon' public key)
    GEMINI_API_KEY=AIza...
    ```

## 2. Usage

### Start the Agent

To start the persistent monitoring loop:

```bash
python main_agent.py
```

- It will fetch mock weather data and push to Supabase.
- It checks for fires.
- It updates the Zone Status (`NORMAL` by default).

### Trigger a Demo Alert

To prove the system works, force a "Fire Detected" state:

1.  Keep `main_agent.py` running (or run it after this step).
2.  Open a new terminal.
3.  Run:
    ```bash
    python demo_trigger.py
    ```
4.  Watch the `main_agent.py` logs. It will detect the "Fire", switch state to `ALERT`, and generate an AI warning in `alert_history`.

## 3. Architecture

- `src/fetchers_supabase.py`: Writes raw data to `weather_logs` / `fire_events`.
- `src/state_manager_supabase.py`: Reads DB, decides state, updates `zones`.
- `src/ai_analyzer.py`: Reads trigger, calls Gemini, writes to `alert_history`.
