from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128))
    phone = Column(String(64), unique=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    requests = relationship("HelpRequest", back_populates="customer")


class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128))
    email = Column(String(128))


class HelpRequestState:
    """Constants representing help request states."""
    PENDING = "pending"
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


class HelpRequest(Base):
    __tablename__ = "help_requests"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    question_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    state = Column(String(32), default=HelpRequestState.PENDING)
    assigned_supervisor_id = Column(Integer, ForeignKey("supervisors.id"), nullable=True)
    response_text = Column(Text, nullable=True)
    response_at = Column(DateTime, nullable=True)
    timeout_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="requests")


class KnowledgeBaseEntry(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    answer_text = Column(Text)
    source_request_id = Column(Integer, nullable=True)
    created_by = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    tags = Column(String(256), nullable=True)
    confidence = Column(String(16), nullable=True)
