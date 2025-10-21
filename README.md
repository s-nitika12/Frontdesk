# Human-in-the-Loop AI Supervisor System — Full Setup & Design Guide

## Overview
This system simulates a human-in-the-loop AI workflow for handling customer queries with automatic AI responses and supervisor intervention when needed. It uses **Python**, **Flask** for backend APIs, **Streamlit** for supervisor UI, **SQLite** via **SQLAlchemy** for database management, and a **LiveKit simulator** for call events.

The workflow:
1. Customer sends a query.
2. AI agent consults the knowledge base (KB).
3. If answer exists, respond automatically.
4. If answer is unknown, escalate to supervisor via Streamlit UI.
5. Supervisor responds → KB is updated → customer notified.

## Repo Structure
```
/  
├─ README.md             # This file  
├─ requirements.txt      # Python dependencies
├─ run_local.sh          # Simple startup script
├─ .env.example          # Environment variables template
├─ backend/              # Flask backend + AI logic + services
│   ├─ app.py
│   ├─ config.py
│   ├─ db.py
│   ├─ models.py
│   ├─ ai_agent.py
│   ├─ livekit_integration.py
│   ├─ services/         # KB, help request, notifications
│   └─ tests/            # Unit tests
├─ ui/                   # Streamlit Supervisor dashboard
│   └─ supervisor_app.py
├─ prompts/              # Templates and sample business info
└─ scripts/              # Data seeding scripts
```  

---

## Step 1: Environment Setup
1. Clone repo and navigate:
```bash
git clone <repo-url>
cd <repo-folder>
```

2. Create Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit if needed (e.g., LiveKit API keys, supervisor TTL, webhook URL)
```

---

## Step 2: Database Initialization
1. Tables are created automatically on backend start using SQLAlchemy `Base.metadata.create_all(bind=engine)`.
2. Optional: Seed demo data (supervisors, customers, KB entries):
```bash
python scripts/seed_data.py
```

---

## Step 3: Running Backend (Flask)
```bash
export FLASK_APP=backend.app  # Windows: set FLASK_APP=backend.app
export FLASK_ENV=development
flask run --port=8000
```
- The backend provides REST API endpoints:
  - `POST /api/call/incoming` → simulate incoming customer query
  - `GET /api/requests` → list help requests
  - `POST /api/requests/<id>/respond` → supervisor submits response
  - `GET/POST /api/kb` → list or add KB entries

- **Timeout Worker**: A background thread checks pending requests and marks them unresolved after TTL.

---

## Step 4: Running Supervisor UI (Streamlit)
```bash
streamlit run ui/supervisor_app.py
```

**Features:**
- **Pending Requests Tab**: View escalated customer questions, submit answers.
- **History Tab**: Track resolved/unresolved requests.
- **Learned Answers Tab**: Search and review KB entries.

**Notes:**
- API base URL can be configured in the sidebar.
- Supervisor ID is optional but tracked in KB updates.

---

## Step 5: AI Agent Workflow
1. `AIAgent.handle_incoming(caller, question)` handles each query.
2. Consults KB via `KBService.find_answer`:
   - If exact/fuzzy match → respond automatically.
   - Else → create `HelpRequest` and notify supervisor.
3. On supervisor response, creates KB entry for future queries and notifies the customer.

**Fuzzy Matching:** Uses `difflib.get_close_matches` to find similar questions. Threshold configurable via `.env`.

---

## Step 6: Notifications
- `NotificationService` handles messages to customers and supervisors.
- Currently logs to console; can be configured to send to webhooks.
- Customer receives notification immediately upon supervisor resolution.

---

## Step 7: Running Tests
```bash
pytest backend/tests
```
- Tests cover help request lifecycle and KB functionality.

---

## Design Notes
1. **Modular Services**: Separate classes for KB, Help Requests, Notifications → easier to swap DB or notification channels.
2. **DB Abstraction**: `DBAdapter` allows switching SQLite → DynamoDB/Firebase.
3. **Supervisor TTL**: Pending requests auto-marked unresolved after TTL; configurable in `.env`.
4. **LiveKit Integration**: Currently a simulator for demo. Real integration replaces simulator in `livekit_integration.py`.
5. **Extensibility**:
   - Use Redis/worker queues for scaling.
   - Add authentication for supervisor UI.
   - Replace difflib with `rapidfuzz` for better fuzzy matching.

---

## Step 8: Quick Simulation Example
```bash
curl -X POST http://localhost:8000/api/call/incoming \
-H "Content-Type: application/json" \
-d '{"caller":{"name":"Jane Doe","phone":"+15550001"},"question":"Do you offer balayage?"}'
```
- AI responds if KB has answer.
- Else creates help request → visible in Streamlit UI → supervisor responds → KB updated.

---

## Tips
- Keep Streamlit and Flask running in separate terminals.
- Seed data for easy testing.
- Check logs for notifications and request flow.
- Adjust `.env` TTL for faster testing of unresolved request handling.

This README guides setup **from UI to backend**, step by step, with design decisions explained for maintainability, scalability, and clarity.

