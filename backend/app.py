from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from datetime import datetime
import threading
import time
import logging
import os

from .config import Config
from .db import engine, SessionLocal
from .models import (
    Base,
    Customer,
    Supervisor,
    HelpRequest,
    KnowledgeBaseEntry,
    HelpRequestState,
)
from .services.kb_services import KBService
from .services.help_request_service import HelpRequestService
from .services.notification_service import NotificationService
from .ai_agent import AIAgent
from .livekit_integration import LiveKitWrapper

# Create database tables if not exist
Base.metadata.create_all(bind=engine)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

# Initialize core services
kb_service = KBService()
help_service = HelpRequestService()
notifier = NotificationService()
agent = AIAgent()
livekit = LiveKitWrapper()


def timeout_worker():
    """Background worker to check and mark timed-out help requests."""
    while True:
        try:
            expired = help_service.check_and_mark_timeouts()
            for r in expired:
                db = SessionLocal()
                try:
                    cust = db.query(Customer).filter(Customer.id == r.customer_id).first()
                    if cust:
                        notifier.notify_customer(
                            {"name": cust.name, "phone": cust.phone},
                            "Sorry, we couldn't resolve your question in time. We'll follow up soon.",
                        )
                finally:
                    db.close()
            time.sleep(10)
        except Exception as e:
            logger.exception("timeout_worker error")
            time.sleep(5)


# Start background worker thread
worker = threading.Thread(target=timeout_worker, daemon=True)
worker.start()


@app.route("/api/call/incoming", methods=["POST"])
def incoming_call():
    """Handles incoming customer questions."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "bad payload"}), 400

    caller = data.get("caller", {})
    question = data.get("question", "")

    if not caller.get("phone") or not question:
        return jsonify({"error": "missing fields"}), 400

    result = agent.handle_incoming(caller, question)
    return jsonify(result)


@app.route("/api/requests", methods=["GET"])
def list_requests():
    """List help requests by state."""
    state = request.args.get("state")
    rows = help_service.list_requests(state=state)

    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "customer_id": r.customer_id,
            "question_text": r.question_text,
            "created_at": r.created_at.isoformat(),
            "state": r.state,
            "response_text": r.response_text,
        })
    return jsonify(out)


@app.route("/api/requests/<int:request_id>", methods=["GET"])
def get_request(request_id):
    """Get a specific help request."""
    r = help_service.get_request(request_id)
    if not r:
        abort(404)

    return jsonify({
        "id": r.id,
        "customer_id": r.customer_id,
        "question_text": r.question_text,
        "created_at": r.created_at.isoformat(),
        "state": r.state,
        "response_text": r.response_text,
    })


@app.route("/api/requests/<int:request_id>/respond", methods=["POST"])
def respond_request(request_id):
    """Supervisor responds to a help request."""
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "bad payload"}), 400

    answer = payload.get("answer")
    supervisor_id = payload.get("supervisor_id")

    if not answer:
        return jsonify({"error": "missing answer"}), 400

    hr = help_service.resolve_request(request_id, answer, supervisor_id)
    if not hr:
        return jsonify({"error": "request not found"}), 404

    # Create KB entry
    kb = kb_service.create_entry(
        hr.question_text,
        answer,
        source_request_id=hr.id,
        created_by=f"supervisor:{supervisor_id}",
    )

    # Notify customer
    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.id == hr.customer_id).first()
        if cust:
            notifier.notify_customer({"name": cust.name, "phone": cust.phone}, answer)
    finally:
        db.close()

    return jsonify({"status": "ok", "kb_id": kb.id})


@app.route("/api/kb", methods=["GET", "POST"])
def kb_routes():
    """Knowledge Base routes."""
    if request.method == "GET":
        entries = kb_service.list_entries()
        return jsonify(entries)

    data = request.get_json()
    if not data:
        return jsonify({"error": "bad payload"}), 400

    q = data.get("question_text")
    a = data.get("answer_text")
    created_by = data.get("created_by")

    kb = kb_service.create_entry(q, a, created_by=created_by)
    return jsonify({"status": "ok", "id": kb.id})


@app.route("/api/simulate/timeout", methods=["POST"])
def simulate_timeout():
    """Simulate timeout for testing."""
    expired = help_service.check_and_mark_timeouts()
    return jsonify({"expired": [r.id for r in expired]})


# ============== Voice AI Endpoints ==============

@app.route("/api/voice/room/create", methods=["POST"])
def create_voice_room():
    """Create a LiveKit room for voice conversation."""
    data = request.get_json() or {}
    room_name = data.get("room_name", f"room_{int(time.time())}")
    
    result = livekit.create_room(room_name)
    return jsonify(result)


@app.route("/api/voice/token", methods=["POST"])
def generate_voice_token():
    """Generate access token for joining a voice room."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "bad payload"}), 400
    
    room_name = data.get("room_name")
    participant_id = data.get("participant_id")
    participant_name = data.get("participant_name")
    
    if not room_name or not participant_id:
        return jsonify({"error": "missing room_name or participant_id"}), 400
    
    token = livekit.generate_token(room_name, participant_id, participant_name)
    
    if token:
        return jsonify({"token": token, "url": livekit.url})
    else:
        return jsonify({"error": "failed to generate token"}), 500


@app.route("/api/voice/rooms", methods=["GET"])
def list_voice_rooms():
    """List all active voice rooms."""
    result = livekit.list_rooms()
    return jsonify(result)


@app.route("/api/voice/room/<room_name>", methods=["DELETE"])
def delete_voice_room(room_name):
    """Delete a voice room."""
    result = livekit.delete_room(room_name)
    return jsonify(result)


@app.route("/api/voice/status", methods=["GET"])
def voice_status():
    """Get voice AI system status."""
    status = livekit.placeholder()
    return jsonify(status)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "kb": "active",
            "help_requests": "active",
            "notifications": "active",
            "voice_ai": "configured" if livekit.client else "not_configured"
        }
    })


if __name__ == "__main__":
    # Allow running via: python -m backend.app
    port = getattr(Config, "FLASK_PORT", 5000)
    logger.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)
