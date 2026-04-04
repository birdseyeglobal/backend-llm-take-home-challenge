from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Brand(SQLModel, table=True):
    __tablename__ = "brand"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="The unique identifier for the brand",
    )
    url: str | None = Field(description="The URL of the brand's website", nullable=True)
    docs: list[str] | None = Field(
        description="The brand's documentation", sa_type=JSONB, nullable=True
    )


class VoiceProfile(SQLModel, table=True):
    __tablename__ = "voice_profile"
    __table_args__ = (UniqueConstraint("brand_id", "version"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    brand_id: UUID = Field(foreign_key="brand.id", ondelete="CASCADE")
    version: int = Field(default=1)
    warmth: float
    seriousness: float
    technicality: float
    formality: float
    playfulness: float
    target_demographic: str
    style_guide: list[str] = Field(sa_type=JSONB)
    writing_example: str
    llm_model: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
