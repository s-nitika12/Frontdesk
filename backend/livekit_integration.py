import json
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .config import Config

try:
    from livekit import api
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    logging.warning("LiveKit SDK not installed. Voice features will be limited.")

logger = logging.getLogger("livekit")


class LiveKitWrapper:
    """Wrapper for LiveKit API with real room and token management."""

    def __init__(self, api_key: str = Config.LIVEKIT_API_KEY, api_secret: str = Config.LIVEKIT_API_SECRET):
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""
        self.url = Config.LIVEKIT_URL if hasattr(Config, 'LIVEKIT_URL') else "ws://localhost:7880"
        
        logger.info(f"LiveKit Init - API Key: {self.api_key[:10] if self.api_key else 'None'}..., Has Secret: {bool(self.api_secret)}")
        
        if not LIVEKIT_AVAILABLE:
            logger.warning("LiveKit SDK not available. Install with: pip install livekit")
            self.client = None
        elif not self.api_key or not self.api_secret:
            logger.warning("LiveKit credentials not configured. Set LIVEKIT_API_KEY and LIVEKIT_API_SECRET in .env")
            self.client = None
        else:
            # For Flask (sync context), we'll create client on-demand
            # This avoids the event loop issue during initialization
            self.client = "configured"  # Flag to indicate credentials are set
            logger.info("LiveKit credentials loaded successfully")

    def create_room(self, room_name: str, empty_timeout: int = 300, max_participants: int = 10) -> Dict[str, Any]:
        """Create a LiveKit room (simplified - room is auto-created when participant joins)."""
        logger.info(f"create_room called - client: {self.client}, api_key: {bool(self.api_key)}, api_secret: {bool(self.api_secret)}")
        
        if not self.client or not self.api_key or not self.api_secret:
            logger.error(f"LiveKit not configured - client={self.client}, has_key={bool(self.api_key)}, has_secret={bool(self.api_secret)}")
            return {"error": "LiveKit not configured", "status": "disabled"}
        
        # In LiveKit, rooms are automatically created when the first participant joins
        # So we just need to generate a token for this room
        logger.info(f"Room '{room_name}' will be auto-created on first participant join")
        return {
            "status": "success",
            "room_name": room_name,
            "message": "Room will be created automatically when first participant joins",
            "configured": True
        }

    def generate_token(
        self,
        room_name: str,
        participant_identity: str,
        participant_name: Optional[str] = None,
        ttl_seconds: int = 3600
    ) -> Optional[str]:
        """Generate access token for a participant to join a room."""
        if not LIVEKIT_AVAILABLE or not self.api_key or not self.api_secret:
            logger.error("Cannot generate token: LiveKit not properly configured")
            return None
        
        try:
            from livekit import api as lk_api
            
            token = lk_api.AccessToken(self.api_key, self.api_secret)
            token.with_identity(participant_identity)
            token.with_name(participant_name or participant_identity)
            token.with_grants(
                lk_api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            token.with_ttl(timedelta(seconds=ttl_seconds))
            
            return token.to_jwt()
        except Exception as e:
            logger.error(f"Failed to generate token: {e}")
            return None

    def list_rooms(self) -> Dict[str, Any]:
        """List all active rooms (simplified version)."""
        if not self.client or not self.api_key or not self.api_secret:
            return {"error": "LiveKit not configured", "rooms": []}
        
        # For Flask sync context, we can't easily list rooms without async
        # Return a helpful message instead
        return {
            "status": "info",
            "message": "Room listing requires async context. Use LiveKit dashboard to view active rooms.",
            "dashboard_url": "https://cloud.livekit.io/",
            "rooms": []
        }

    def delete_room(self, room_name: str) -> Dict[str, Any]:
        """Delete a room (simplified version)."""
        if not self.client or not self.api_key or not self.api_secret:
            return {"error": "LiveKit not configured"}
        
        # For Flask sync context, recommend using dashboard
        return {
            "status": "info",
            "message": "Room deletion requires async context. Use LiveKit dashboard to delete rooms.",
            "dashboard_url": "https://cloud.livekit.io/",
            "room_name": room_name
        }

    def placeholder(self) -> Dict[str, Any]:
        """Return a placeholder response (used for local testing)."""
        configured = bool(self.client) and bool(self.api_key) and bool(self.api_secret)
        logger.info(f"Placeholder check - client: {self.client}, api_key: {bool(self.api_key)}, api_secret: {bool(self.api_secret)}, configured: {configured}")
        return {
            "status": "livekit_placeholder",
            "configured": configured,
            "sdk_available": LIVEKIT_AVAILABLE
        }


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
