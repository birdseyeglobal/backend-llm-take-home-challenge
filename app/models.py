"""
SQLModel database models
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class TestEntry(SQLModel, table=True):
    """Simple test table to verify database connectivity"""
    __tablename__ = "test_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    message: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)


class UserContent(SQLModel, table=True):
    """User-provided content storage"""
    __tablename__ = "user_content"

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(min_length=50, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.now)


class ContentAnalysis(SQLModel, table=True):
    """Analysis results for user content"""
    __tablename__ = "content_analysis"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_content_id: int = Field(foreign_key="user_content.id", unique=True)
    warmth_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    target_demographic: Optional[str] = None
    status: str = Field(default="pending")  # pending, completed, failed
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
