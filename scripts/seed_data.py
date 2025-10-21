"""
Seed sample supervisors, customers, and KB entries for local demo.
"""

from backend.db import engine, SessionLocal
from backend.models import Base, Supervisor, Customer, KnowledgeBaseEntry


def seed():
    """Create tables and seed initial data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed Supervisor
        if db.query(Supervisor).count() == 0:
            s = Supervisor(name="Alice Supervisor", email="alice@example.com")
            db.add(s)

        # Seed Customer
        if db.query(Customer).count() == 0:
            c = Customer(name="Demo Customer", phone="+15550001")
            db.add(c)

        # Seed Knowledge Base Entry
        if db.query(KnowledgeBaseEntry).count() == 0:
            kb = KnowledgeBaseEntry(
                question_text="What are your hours?",
                answer_text="We are open Mon-Sat 9am-7pm",
                created_by="seed"
            )
            db.add(kb)

        db.commit()
    finally:
        db.close()

    print("Seed complete.")


if __name__ == "__main__":
    seed()
