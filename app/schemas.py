"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel, Field
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    message: str


class TestResponse(BaseModel):
    message: str
    timestamp: datetime
    data: dict


class TestEntryCreate(BaseModel):
    message: str


class TestEntryResponse(BaseModel):
    id: int
    message: str
    created_at: datetime
    status: str


class UserContentCreate(BaseModel):
    content: str = Field(min_length=50, max_length=1000)


class UserContentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    status: str


class AnalyzeContentRequest(BaseModel):
    content_id: int = Field(gt=0)


class AnalysisStatusResponse(BaseModel):
    content_id: int
    status: str
    message: str


class AnalysisResponse(BaseModel):
    content_id: int
    warmth_score: float | None
    target_demographic: str | None
    status: str
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
