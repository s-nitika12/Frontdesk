import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # LiveKit credentials
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")
    LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")

    # Supervisor configuration
    SUPERVISOR_TTL_SECONDS = int(os.getenv("SUPERVISOR_TTL_SECONDS", "1800"))

    # Optional notification webhook
    NOTIFICATION_WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK_URL", "")

    # Flask server configuration
    FLASK_PORT = int(os.getenv("FLASK_PORT", "8000"))

    # Database configuration
    DB_URL = os.getenv("DB_URL", "sqlite:///./local.db")

    # Knowledge Base (similarity threshold)
    KB_FUZZY_THRESHOLD = float(os.getenv("KB_FUZZY_THRESHOLD", "0.6"))
