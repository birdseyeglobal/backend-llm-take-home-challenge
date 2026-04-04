from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class BrandPostRequest(BaseModel):
    url: HttpUrl | None
    docs: list[str] | None


class BrandResponse(BaseModel):
    id: UUID
    url: HttpUrl | None
    docs: list[str] | None


class BrandPostResponse(BrandResponse):
    pass


class BrandGetResponse(BrandResponse):
    pass


class VoiceGenerateRequest(BaseModel):
    writing_samples: list[str]


class VoiceProfileResponse(BaseModel):
    id: UUID
    brand_id: UUID
    version: int
    warmth: float = Field(ge=0.0, le=1.0)
    seriousness: float = Field(ge=0.0, le=1.0)
    technicality: float = Field(ge=0.0, le=1.0)
    formality: float = Field(ge=0.0, le=1.0)
    playfulness: float = Field(ge=0.0, le=1.0)
    target_demographic: str
    style_guide: list[str]
    writing_example: str
    created_at: datetime

    model_config = {"from_attributes": True}


class VoiceProfileLLMResult(BaseModel):
    warmth: float = Field(ge=0.0, le=1.0)
    seriousness: float = Field(ge=0.0, le=1.0)
    technicality: float = Field(ge=0.0, le=1.0)
    formality: float = Field(ge=0.0, le=1.0)
    playfulness: float = Field(ge=0.0, le=1.0)
    target_demographic: str
    style_guide: list[str]
    writing_example: str
