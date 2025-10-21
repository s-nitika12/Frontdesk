"""
Initialize backend core modules before anything else runs.
Ensures that db.py, models.py, and Base.metadata.create_all() run first.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

print("Initializing backend database and models...")

try:
    from backend.db import engine
    from backend.models import Base

    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
except Exception as e:
    print("Error initializing backend:", e)
    sys.exit(1)

print("Backend initialization completed successfully.")