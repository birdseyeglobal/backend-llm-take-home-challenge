from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.base.api.dependencies import get_session
from app.brand.api.schemas import BrandGetResponse, BrandPostRequest, BrandPostResponse
from app.brand.api.servicer import BrandServicer

router = APIRouter(
    prefix="/brands",
)


@router.post("/")
def create_brand(
    brand: BrandPostRequest, session: Annotated[Session, Depends(get_session)]
) -> BrandPostResponse:
    servicer = BrandServicer()
    return servicer.create_brand(brand, session)


@router.get("/{brand_id}")
def get_brand(
    brand_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> BrandGetResponse:
    servicer = BrandServicer()
    return servicer.get_brand(brand_id, session)
