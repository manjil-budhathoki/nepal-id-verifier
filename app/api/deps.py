from typing import Generator
from app.db.session import SessionLocal

def get_db() -> Generator:
    """
    Creates a fresh database session for each request, 
    and closes it when the request finishes.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()