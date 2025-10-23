import os
import sys
import tempfile

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.db import engine, SessionLocal
from backend.models import Base, Customer
from backend.services.help_request_service import HelpRequestService


def setup_module(module):
    """Ensure database tables exist before running tests."""
    Base.metadata.create_all(bind=engine)


def test_create_help_request_and_resolve():
    """Test creating a help request and resolving it."""
    db = SessionLocal()
    try:
        # Create a test customer
        cust = Customer(name="Test User", phone="+1000000")
        db.add(cust)
        db.commit()
        db.refresh(cust)

        # Create help request
        svc = HelpRequestService()
        hr = svc.create_help_request(cust.id, "How late are you open?")
        assert hr.id is not None, "HelpRequest ID should not be None"

        # Resolve the request
        svc.resolve_request(hr.id, "We are open 9-7", supervisor_id=1)
        r = svc.get_request(hr.id)
        assert r.state == "resolved", f"Expected state 'resolved', got '{r.state}'"

    finally:
        db.close()
