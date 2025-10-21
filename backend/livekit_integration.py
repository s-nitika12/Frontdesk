import json
import requests
from typing import Dict, Any
from .config import Config


class LiveKitWrapper:
    """Wrapper for LiveKit API (placeholder for demo purposes)."""

    def __init__(self, api_key: str = Config.LIVEKIT_API_KEY, api_secret: str = Config.LIVEKIT_API_SECRET):
        self.api_key = api_key
        self.api_secret = api_secret
        # Real LiveKit API integration would go here; for demo we keep it minimal.

    def placeholder(self) -> Dict[str, Any]:
        """Return a placeholder response (used for local testing)."""
        return {"status": "livekit_placeholder"}


class LocalCallSimulator:
    """
    Simulate an incoming call by sending a POST request to the backend API.
    """

    def __init__(self, backend_url: str = f"http://localhost:{Config.FLASK_PORT}/api/call/incoming"):
        self.backend_url = backend_url

    def simulate_call(self, caller: Dict[str, Any], question: str):
        """Simulate a customer call by posting data to the backend."""
        payload = {"caller": caller, "question": question}
        try:
            r = requests.post(self.backend_url, json=payload, timeout=5)
            return r.status_code, r.text
        except Exception as e:
            return 500, str(e)
