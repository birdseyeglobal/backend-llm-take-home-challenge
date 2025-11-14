from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.base.api.dependencies import get_session
from app.brand.api.servicer import BrandServicer
from app.brand.api.schemas import BrandPostRequest, BrandPostResponse, BrandGetResponse
from app.brand.db.models import Brand
from uuid import UUID

router = APIRouter(
    prefix="/brands",
)

@router.post("/", response_model=BrandPostResponse)
def create_brand(brand: BrandPostRequest, session: Session = Depends(get_session)) -> BrandPostResponse:
    servicer = BrandServicer()
    return servicer.create_brand(brand, session)

@router.get("/{brand_id}", response_model=BrandGetResponse)
def get_brand(brand_id: UUID, session: Session = Depends(get_session)) -> BrandGetResponse:
    servicer = BrandServicer()
    return servicer.get_brand(brand_id, session)
