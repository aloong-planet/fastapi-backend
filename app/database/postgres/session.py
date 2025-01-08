from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.configs import APP_SETTINGS
from .products_seed import init_products_data
from .seed import init_rbac_data

ENGINE = create_async_engine(APP_SETTINGS.POSTGRES_URI,
                             pool_pre_ping=APP_SETTINGS.POOL_PRE_PING,
                             pool_size=APP_SETTINGS.POOL_SIZE,
                             pool_recycle=APP_SETTINGS.POOL_RECYCLE,
                             pool_timeout=APP_SETTINGS.POOL_TIMEOUT)

ASYNC_SESSION = sessionmaker(ENGINE, class_=AsyncSession, expire_on_commit=False)


class AsyncDatabaseSession:

    async def __aenter__(self):
        self.session = ASYNC_SESSION()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()


async def init_db():
    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncDatabaseSession() as session:
        await init_rbac_data(db_session=session)
        await init_products_data(db_session=session)


async def get_session() -> AsyncSession:
    async with AsyncDatabaseSession() as session:
        yield session
