from uuid import UUID

from fastapi import HTTPException
from pydantic import HttpUrl

from app.brand.api.schemas import BrandPostRequest, BrandPostResponse, BrandGetResponse
from app.brand.db.models import Brand
from sqlmodel import Session

class BrandServicer:
    def create_brand(self, brand_post_request: BrandPostRequest, session: Session) -> BrandPostResponse:
        brand = Brand(
            url=str(brand_post_request.url) if brand_post_request.url else None,
            docs=brand_post_request.docs,
        )
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return BrandPostResponse(
            id=brand.id,
            url=HttpUrl(brand.url),
            docs=brand.docs,
        )

    def get_brand(self, brand_id: UUID, session: Session) -> BrandGetResponse:
        brand = session.get(Brand, brand_id)
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        return BrandGetResponse(
            url=HttpUrl(brand.url),
            docs=brand.docs,
            id=brand.id,
        )