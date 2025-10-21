from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .config import Config

# Create SQLAlchemy engine
engine = create_engine(
    Config.DB_URL,
    connect_args={"check_same_thread": False} if "sqlite" in Config.DB_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class DBAdapter:
    """Database adapter for managing sessions."""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_session(self) -> Session:
        """Return a new SQLAlchemy session."""
        return self.SessionLocal()


# For SQLite local development or FastAPI-style dependency injection
def get_db() -> Generator[Session, None, None]:
    """Provide a database session and ensure it closes after use."""
    db = DBAdapter().get_session()
    try:
        yield db
    finally:
        db.close()
