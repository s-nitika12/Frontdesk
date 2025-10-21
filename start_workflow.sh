#!/usr/bin/env bash
#
# start_workflow.sh
# --------------------------------------------
# Human-in-the-Loop AI Supervisor Automation Script
# Runs setup, backend, UI, and local simulation stepwise
# --------------------------------------------

set -e  # stop if any command fails

# ---- Colors ----
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Human-in-the-Loop AI Supervisor Workflow...${NC}"

# ---- Step 1: Create and activate virtual environment ----
echo -e "\n${YELLOW}Step 1/6: Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "${GREEN}Virtual environment created.${NC}"
fi

# shellcheck source=/dev/null
echo -e "${GREEN}Virtual environment activated.${NC}"

# ---- Step 2: Install dependencies ----
echo -e "\n${YELLOW}Step 2/6: Installing required dependencies...${NC}"
pip install --upgrade pip >/dev/null
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed successfully.${NC}"

# ---- Step 3: Environment setup ----
echo -e "\n${YELLOW}Step 3/6: Setting environment variables...${NC}"
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${GREEN}.env file created from template.${NC}"
fi
export $(grep -v '^#' .env | xargs)

# ---- Step 4: Seed database ----
echo -e "\n${YELLOW}Step 4/6: Seeding sample data (supervisors, customers, KB)...${NC}"
python init_backend.py
python -m scripts.seed_data
#python scripts/seed_data.py
echo -e "${GREEN}Database seeded successfully.${NC}"

# ---- Step 5: Start backend (Flask API) ----
echo -e "\n${YELLOW}Step 5/6: Starting Flask backend server...${NC}"
nohup flask run --port=${FLASK_PORT:-8000} > logs_backend.txt 2>&1 &
BACKEND_PID=$!
sleep 3
echo -e "${GREEN}Backend running (PID $BACKEND_PID). Logs → logs_backend.txt${NC}"

# ---- Step 6: Start Streamlit UI ----
echo -e "\n${YELLOW}Step 6/6: Launching Streamlit Supervisor UI...${NC}"
nohup streamlit run ui/supervisor_app.py > logs_ui.txt 2>&1 &
UI_PID=$!
sleep 3
echo -e "${GREEN}Supervisor UI running (PID $UI_PID). Logs → logs_ui.txt${NC}"

# ---- Summary ----
echo -e "\n${BLUE}✅ All components started successfully!${NC}"
echo -e "${YELLOW}Access Summary:${NC}"
echo -e "  - Backend API:  ${GREEN}http://localhost:${FLASK_PORT:-8000}${NC}"
echo -e "  - Streamlit UI: ${GREEN}http://localhost:8501${NC}"
echo -e "  - API Docs:     See README.md for curl examples"

# ---- Simulation example ----
echo -e "\n${YELLOW}To simulate a customer call, run:${NC}"
echo -e "curl -X POST http://localhost:${FLASK_PORT:-8000}/api/call/incoming \\"
echo -e "     -H 'Content-Type: application/json' \\"
echo -e "     -d '{\"caller\": {\"name\": \"Jane Doe\", \"phone\": \"+15550001\"}, \"question\": \"Do you offer balayage?\"}'"

# ---- Cleanup instructions ----
echo -e "\n${BLUE}To stop all running services:${NC}"
echo -e "kill ${BACKEND_PID} ${UI_PID} || true"
echo -e "${YELLOW}Logs are stored in logs_backend.txt and logs_ui.txt${NC}"