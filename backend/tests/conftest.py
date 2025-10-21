# Optional pytest fixtures (minimal)
import pytest

# Example fixture for DB session
from backend.db import SessionLocal

@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
