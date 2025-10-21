from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from ..models import KnowledgeBaseEntry
from ..db import SessionLocal
from ..config import Config
import difflib


class KBService:
    """Knowledge Base service with CRUD and fuzzy search."""

    def __init__(self, db_session_factory=SessionLocal):
        self.db_session_factory = db_session_factory
        self.threshold = Config.KB_FUZZY_THRESHOLD

    def create_entry(
        self,
        question_text: str,
        answer_text: str,
        source_request_id: int = None,
        created_by: str = None,
        tags: str = None,
        confidence: str = None
    ) -> KnowledgeBaseEntry:
        """Create a new Knowledge Base entry."""
        db: Session = self.db_session_factory()
        try:
            entry = KnowledgeBaseEntry(
                question_text=question_text,
                answer_text=answer_text,
                source_request_id=source_request_id,
                created_by=created_by,
                tags=tags,
                confidence=confidence
            )
            db.add(entry)
            db.commit()
            db.refresh(entry)
            return entry
        finally:
            db.close()

    def list_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List KB entries, ordered by most recent."""
        db = self.db_session_factory()
        try:
            rows = (
                db.query(KnowledgeBaseEntry)
                .order_by(KnowledgeBaseEntry.created_at.desc())
                .limit(limit)
                .all()
            )
            return [self._row_to_dict(r) for r in rows]
        finally:
            db.close()

    def _row_to_dict(self, row: KnowledgeBaseEntry) -> Dict[str, Any]:
        """Convert a KnowledgeBaseEntry row to a dictionary."""
        return {
            "id": row.id,
            "question_text": row.question_text,
            "answer_text": row.answer_text,
            "source_request_id": row.source_request_id,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat(),
            "version": row.version,
            "tags": row.tags,
            "confidence": row.confidence
        }

    def find_answer(self, question_text: str) -> Optional[Dict[str, Any]]:
        """
        Find an answer from the KB.
        - Exact match first
        - Then fuzzy match using difflib
        """
        db = self.db_session_factory()
        try:
            # Exact match
            exact = db.query(KnowledgeBaseEntry).filter(
                KnowledgeBaseEntry.question_text == question_text
            ).first()
            if exact:
                return self._row_to_dict(exact)

            # Fuzzy match
            all_qs = [q.question_text for q in db.query(KnowledgeBaseEntry).all()]
            if not all_qs:
                return None

            matches = difflib.get_close_matches(question_text, all_qs, n=1, cutoff=self.threshold)
            if matches:
                row = db.query(KnowledgeBaseEntry).filter(
                    KnowledgeBaseEntry.question_text == matches[0]
                ).first()
                return self._row_to_dict(row)

            return None
        finally:
            db.close()
