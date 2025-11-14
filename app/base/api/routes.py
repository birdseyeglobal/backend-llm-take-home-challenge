from fastapi import APIRouter

from app.brand.api.routes import router as brand_router

router = APIRouter(
    prefix="/api",
)
router.include_router(brand_router)