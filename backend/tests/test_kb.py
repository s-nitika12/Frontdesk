from ..services.kb_service import KBService
from ..db import SessionLocal, engine
from ..models import KnowledgeBaseEntry, Base


def test_kb_create_and_find():
    """Test creating a KB entry and finding it."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Initialize service
    svc = KBService()

    # Create KB entry
    e = svc.create_entry("What are your hours?", "We are open 9-7", created_by="test")
    assert e.id is not None, "KB entry ID should not be None"

    # Find KB entry
    found = svc.find_answer("What are your hours?")
    assert found is not None, "Should find the KB entry"
    assert "9-7" in found["answer_text"], "Answer text should contain '9-7'"
