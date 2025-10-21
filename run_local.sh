#!/usr/bin/env bash
set -e
echo "Starting local demo..."
echo "1) Activate virtualenv and install requirements (if not done)"
echo " python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
echo "2) Start backend:"
echo " flask run --port=8000"
echo "3) Start Streamlit UI in another terminal:"
echo " streamlit run ui/supervisor_app.py"
echo "4) Seed data (once): python scripts/seed_data.py"
echo "To simulate call:"
echo " curl -X POST http://localhost:8000/api/call/incoming
 -H 'Content-Type: application/json' -d '{"caller":{"name":"Jane","phone":"+15550001"},"question":"What are your hours?"}'"