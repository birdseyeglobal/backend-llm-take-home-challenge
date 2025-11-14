from uuid import UUID, uuid4

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
