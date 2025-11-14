from uuid import UUID

from pydantic import BaseModel, HttpUrl


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
