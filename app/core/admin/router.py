from fastapi import APIRouter

from app.core.admin.products.router import router as p_router

router = APIRouter()

router.include_router(p_router, tags=["Admin - Products"])
