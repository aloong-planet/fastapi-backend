import csv
import os

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.admin.models import Products
from app.core.auth.models import HashValidation
from app.log import logger
from app.utils.checksum import calculate_file_hash

PRODUCTS_FILE = f'{os.getcwd()}/app/database/postgres/seed/products.csv'


async def init_products(db_session: AsyncSession) -> None:
    with open(PRODUCTS_FILE) as f:
        products_data = csv.DictReader(f)
        logger.debug(f"Products_data: {products_data}")
        for product in products_data:
            await add_or_update_product(db_session=db_session, product=product)


async def add_or_update_product(db_session: AsyncSession, product) -> None:
    """
    Add or update product.
    Fields:
        name: str
        code: str
    """
    check_product_existed_statement = select(Products).where(Products.code == product['Code'])
    product_records = await db_session.exec(check_product_existed_statement)
    db_product = product_records.first()

    if db_product:
        db_product.name = product['Name']
    else:
        db_product = Products(name=product['Name'],
                              code=product['Code'])
        db_session.add(db_product)

    await db_session.commit()
    await db_session.refresh(db_product)


async def init_products_data(db_session: AsyncSession) -> None:
    try:
        # check hash
        hash_validation_statement = select(HashValidation).where(HashValidation.name == 'products_init')
        hash_validation_records = await db_session.exec(hash_validation_statement)
        products_hash = hash_validation_records.first()

        current_hash = calculate_file_hash(PRODUCTS_FILE)
        if products_hash and products_hash.hash == current_hash:
            logger.debug('Products already initialized')
            return
        else:
            logger.debug('Products need to be initialized')
            await init_products(db_session)

            if products_hash:
                products_hash.hash = current_hash
            else:
                products_hash = HashValidation(name='products_init',
                                               type="initial",
                                               hash=current_hash)
                db_session.add(products_hash)
            await db_session.commit()

    except Exception as e:
        logger.error(f'Failed to init products: {str(e)}')
        await db_session.rollback()
    finally:
        await db_session.close()
