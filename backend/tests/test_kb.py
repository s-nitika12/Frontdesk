import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.services.kb_services import KBService
from backend.db import SessionLocal, engine
from backend.models import KnowledgeBaseEntry, Base


def test_kb_create_and_find():
    """Test creating a KB entry and finding it."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Initialize service
    svc = KBService()

    # Create unique KB entry to avoid conflicts with seed data
    unique_question = "What time do you close on Sundays test?"
    unique_answer = "We are closed on Sundays (test answer)"
    
    e = svc.create_entry(unique_question, unique_answer, created_by="test")
    assert e.id is not None, "KB entry ID should not be None"

    # Find KB entry - should find exact match
    found = svc.find_answer(unique_question)
    assert found is not None, "Should find the KB entry"
    assert unique_answer in found["answer_text"], f"Answer text should contain '{unique_answer}', got '{found['answer_text']}'"
    
    print(f"✓ Test passed: Created and found KB entry #{e.id}")
