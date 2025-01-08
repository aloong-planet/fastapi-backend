from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.admin.models import Products
from app.log import logger
from app.responses import PaginatedParams, PaginationData
from app.utils.query import get_count
from .schemas import (ProductCreate,
                      ProductUpdate,
                      ProductResponse)


async def get_products(db: AsyncSession, p: PaginatedParams, filters: dict = None) -> PaginationData[ProductResponse]:
    try:
        query = select(Products)
        if filters:
            for key, value in filters.items():
                if key == "name":
                    _name = getattr(Products, key)
                    query = query.where(_name.ilike(f"%{value}%"))
                    continue
                query = query.where(getattr(Products, key) == value)
        total = await get_count(db, query)
        paged_query = query.offset(p.offset).limit(p.limit)
        paged_products = (await db.exec(paged_query)).all()
        return PaginationData(total=total, items=paged_products)
    except Exception as e:
        await db.rollback()
        msg = f"Failed to get products: {str(e)}"
        logger.error(msg)
        return PaginationData(total=0, items=[])


async def get_product(db: AsyncSession, product_id: int):
    try:
        db_product = (await db.exec(select(Products).where(Products.id == product_id))).first()
        if db_product is None:
            raise Exception("Product not found")

        return db_product, None
    except Exception as e:
        await db.rollback()
        return None, f"Failed to get product: {str(e)}"


async def create_product(db: AsyncSession, product: ProductCreate):
    try:
        new_product = Products(**product.model_dump())
        db.add(new_product)
        await db.commit()
        return new_product, None
    except Exception as e:
        await db.rollback()
        return None, f"Failed to create product: {str(e)}"


async def update_product(db: AsyncSession, product_id: int, product: ProductUpdate):
    try:
        db_product = (await db.exec(select(Products).where(Products.id == product_id))).first()
        if db_product is None:
            raise Exception("Product not found")

        for key, value in product.model_dump(exclude_unset=True).items():
            setattr(db_product, key, value)

        db.add(db_product)
        await db.commit()
        return db_product, None

    except Exception as e:
        await db.rollback()
        return None, f"Failed to update product: {str(e)}"


async def delete_product(db: AsyncSession, product_id: int):
    try:
        db_product = (await db.exec(select(Products).where(Products.id == product_id))).first()
        if db_product is None:
            raise Exception("Product not found")

        await db.delete(db_product)
        await db.commit()
        return None, None
    except Exception as e:
        await db.rollback()
        return None, f"Failed to delete product: {str(e)}"
