import logging
import requests
from typing import Dict, Any
from ..config import Config

# Configure logger
logger = logging.getLogger("notification")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class NotificationService:
    """Handles customer and supervisor notifications."""

    def __init__(self):
        self.webhook = Config.NOTIFICATION_WEBHOOK_URL

    def notify_customer(self, caller: Dict[str, str], message: str):
        """Notify the customer via webhook or log (simulation)."""
        payload = {
            "to": caller.get("phone"),
            "name": caller.get("name"),
            "message": message
        }
        log = f"[NOTIFY:CUSTOMER] to={payload['to']} message={message}"
        logger.info(log)

        if self.webhook:
            try:
                requests.post(self.webhook, json=payload, timeout=3)
            except Exception as e:
                logger.error(f"[NOTIFY] webhook failed: {e}")

    def notify_supervisor(self, help_request):
        """Notify supervisor when escalation is needed."""
        content = f"Hey, I need help answering: '{help_request.question_text}' (request_id={help_request.id})"
        log = f"[NOTIFY:SUPERVISOR] {content}"
        logger.info(log)

        if self.webhook:
            try:
                requests.post(self.webhook, json={"message": content}, timeout=3)
            except Exception as e:
                logger.error(f"[NOTIFY] webhook failed: {e}")
