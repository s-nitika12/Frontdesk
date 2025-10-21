"""
AI Agent logic: prompt composition, KB consultation, and decision to respond or request help.
This module is intentionally simple and deterministic for the coding assignment.
"""

import json
import os
from typing import Dict, Any
from .config import Config
from .services.kb_service import KBService
from .services.help_request_service import HelpRequestService
from .services.notification_service import NotificationService
from .db import SessionLocal
from .models import Customer

# Correct file path handling
PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "salon_business_info.json")
RESPONSE_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "response_template.txt")


class AIAgent:
    """Simple deterministic AI Agent for handling customer interactions."""

    def __init__(self, db_session_factory=SessionLocal):
        self.kb = KBService(db_session_factory)
        self.help_svc = HelpRequestService(db_session_factory)
        self.notifier = NotificationService()

        # Load static business info and response template
        with open(PROMPTS_PATH, "r") as f:
            self.business_info = json.load(f)

        with open(RESPONSE_TEMPLATE_PATH, "r") as f:
            self.response_template = f.read()

    def handle_incoming(self, caller: Dict[str, str], question: str) -> Dict[str, Any]:
        """
        Main entry point:
        - Consult the Knowledge Base (KB)
        - Respond if a match is found
        - Otherwise, create a help request and notify a supervisor
        Returns a dictionary with the action taken.
        """

        # 1️⃣ Consult KB
        match = self.kb.find_answer(question)
        if match:
            answer = match["answer_text"]
            self.notifier.notify_customer(caller, answer)
            return {"action": "responded", "answer": answer}

        # 2️⃣ Create or get customer
        db = SessionLocal()
        try:
            customer = db.query(Customer).filter(Customer.phone == caller.get("phone")).first()
            if not customer:
                customer = Customer(name=caller.get("name"), phone=caller.get("phone"))
                db.add(customer)
                db.commit()
                db.refresh(customer)
        finally:
            db.close()

        # 3️⃣ Create help request
        hr = self.help_svc.create_help_request(customer.id, question)

        # 4️⃣ Notify supervisor
        self.notifier.notify_supervisor(hr)

        return {"action": "escalated", "request_id": hr.id}
