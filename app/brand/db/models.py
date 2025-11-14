from uuid import UUID, uuid4

from pydantic import HttpUrl
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

class Brand(SQLModel, table=True):

    __tablename__ = "brand"

    id: UUID = Field(default_factory=uuid4, primary_key=True, description="The unique identifier for the brand")
    url: str = Field(description="The URL of the brand's website")
    docs: list[str] = Field(description="The brand's documentation", sa_type=JSONB)