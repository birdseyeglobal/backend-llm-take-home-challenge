from uuid import UUID

from app.brand.api.schemas import BrandPostRequest, BrandPostResponse, BrandGetResponse
from app.brand.db.models import Brand
from sqlmodel import Session

class BrandServicer:
    def create_brand(self, brand_post_request: BrandPostRequest, session: Session) -> BrandPostResponse:
        brand = Brand(url=brand_post_request.url, docs=brand_post_request.docs)
        session.add(brand)
        session.commit()
        session.refresh(brand)
        return BrandPostResponse.model_validate(brand)

    def get_brand(self, brand_id: UUID, session: Session) -> BrandGetResponse:
        brand = session.get(Brand, brand_id)
        return BrandGetResponse.model_validate(brand)