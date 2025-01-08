from sqlmodel import func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import SelectOfScalar

from app.log import logger


async def get_count(db: AsyncSession, q: SelectOfScalar) -> int:
    """
    Get the count of the query.
    Note: This function will cause duplicated join on related tables if the query contains join.
    """
    count_q = q.with_only_columns(func.count()).order_by(None).select_from(q.get_final_froms()[0])
    logger.debug(f"\nCount Query:\n{count_q}")
    iterator = await db.exec(count_q)
    for count in iterator:
        return count
    return 0
