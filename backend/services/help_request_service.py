from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import HelpRequest, HelpRequestState
from ..db import SessionLocal
from ..config import Config


class HelpRequestService:
    """Service for managing Help Requests."""

    def __init__(self, db_session_factory=SessionLocal):
        self.db_session_factory = db_session_factory

    def create_help_request(self, customer_id: int, question_text: str) -> HelpRequest:
        """Create a new help request for a customer."""
        db: Session = self.db_session_factory()
        try:
            timeout_at = datetime.utcnow() + timedelta(seconds=Config.SUPERVISOR_TTL_SECONDS)
            hr = HelpRequest(
                customer_id=customer_id,
                question_text=question_text,
                state=HelpRequestState.PENDING,
                timeout_at=timeout_at
            )
            db.add(hr)
            db.commit()
            db.refresh(hr)
            return hr
        finally:
            db.close()

    def get_request(self, request_id: int) -> Optional[HelpRequest]:
        """Retrieve a help request by ID."""
        db = self.db_session_factory()
        try:
            return db.query(HelpRequest).filter(HelpRequest.id == request_id).first()
        finally:
            db.close()

    def list_requests(self, state: Optional[str] = None):
        """List all help requests, optionally filtered by state."""
        db = self.db_session_factory()
        try:
            q = db.query(HelpRequest).order_by(HelpRequest.created_at.desc())
            if state:
                q = q.filter(HelpRequest.state == state)
            return q.all()
        finally:
            db.close()

    def resolve_request(self, request_id: int, response_text: str, supervisor_id: Optional[int] = None):
        """Resolve a help request with a supervisor response."""
        db = self.db_session_factory()
        try:
            hr = db.query(HelpRequest).filter(HelpRequest.id == request_id).first()
            if not hr:
                return None
            hr.state = HelpRequestState.RESOLVED
            hr.response_text = response_text
            hr.response_at = datetime.utcnow()
            hr.assigned_supervisor_id = supervisor_id
            db.commit()
            db.refresh(hr)
            return hr
        finally:
            db.close()

    def mark_unresolved(self, request_id: int):
        """Mark a help request as unresolved."""
        db = self.db_session_factory()
        try:
            hr = db.query(HelpRequest).filter(HelpRequest.id == request_id).first()
            if not hr:
                return None
            hr.state = HelpRequestState.UNRESOLVED
            db.commit()
            db.refresh(hr)
            return hr
        finally:
            db.close()

    def check_and_mark_timeouts(self):
        """
        Check all pending requests and mark those that have timed out as unresolved.
        Returns a list of expired requests.
        """
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            pending = db.query(HelpRequest).filter(HelpRequest.state == HelpRequestState.PENDING).all()
            expired = [r for r in pending if r.timeout_at and r.timeout_at < now]
            for r in expired:
                r.state = HelpRequestState.UNRESOLVED
            db.commit()
            return expired
        finally:
            db.close()
