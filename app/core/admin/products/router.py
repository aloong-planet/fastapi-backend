from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_versionizer import api_version
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.postgres.session import get_session
from app.responses import GeneralResponse, PaginatedParams, PaginationData
from . import schemas
from . import service

router = APIRouter()


@api_version(major=1)
@router.get("/products", response_model=GeneralResponse[PaginationData[schemas.ProductResponse]])
async def get_products(db: AsyncSession = Depends(get_session),
                       name: Optional[str] = Query(None, description="Filter by product name"),
                       code: Optional[str] = Query(None, description="Filter by product code"),
                       p: PaginatedParams = Depends(PaginatedParams)
                       ) -> GeneralResponse[PaginationData[schemas.ProductResponse]]:
    # construct filters dictionary
    filters = {}
    if name:
        filters["name"] = name
    if code:
        filters["code"] = code
    paged_products = await service.get_products(db, p, filters=filters)
    return GeneralResponse(code=0, message="Products retrieved successfully", data=paged_products)


@api_version(major=1)
@router.get("/products/{product_id}", response_model=GeneralResponse[schemas.ProductResponse])
async def get_product(product_id: int,
                      db: AsyncSession = Depends(get_session)) -> GeneralResponse[schemas.ProductResponse]:
    db_product, error = await service.get_product(db, product_id)
    if error:
        return GeneralResponse(code=1, message=error, data="")
    return GeneralResponse(code=0, message="Product retrieved successfully", data=db_product)


@api_version(major=1)
@router.post("/products", response_model=GeneralResponse[schemas.ProductResponse])
async def create_product(product: schemas.ProductCreate,
                         db: AsyncSession = Depends(get_session)) -> GeneralResponse[schemas.ProductResponse]:
    db_product, error = await service.create_product(db, product)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Product created successfully", data=db_product)


@api_version(major=1)
@router.put("/products/{product_id}", response_model=GeneralResponse[schemas.ProductResponse])
async def update_product(product_id: int, product: schemas.ProductUpdate,
                         db: AsyncSession = Depends(get_session)) -> GeneralResponse[schemas.ProductResponse]:
    db_product, error = await service.update_product(db, product_id, product)
    if error:
        return GeneralResponse(code=1, message=error, data=product)
    return GeneralResponse(code=0, message="Product updated successfully", data=db_product)


@api_version(major=1)
@router.delete("/products/{product_id}", response_model=GeneralResponse)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_session)) -> GeneralResponse:
    db_product, error = await service.delete_product(db, product_id)
    if error:
        return GeneralResponse(code=1, message=error, data="")
    return GeneralResponse(code=0, message="Product deleted successfully", data="")
