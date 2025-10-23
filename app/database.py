"""
Database configuration and session management
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling
engine = create_engine(DATABASE_URL, echo=True)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    Automatically handles session lifecycle.
    """
    with Session(engine) as session:
        yield session


def create_db_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)
