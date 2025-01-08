from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.audit.models import Audit
from app.core.auth.models import RUser
from app.log import logger
from app.responses import PaginatedParams, PaginationData
from app.sorting import SortingParams
from app.utils.query import get_count


async def get_audit_logs(db: AsyncSession, p: PaginatedParams, s: SortingParams, filters: dict = None):
    try:
        q = select(Audit)
        if filters:
            for key, value in filters.items():
                if key == "name":
                    _name = getattr(Audit, key)
                    q = q.where(_name.ilike(f"%{value}%"))
                    continue
                q = q.where(getattr(Audit, key) == value)

        total = await get_count(db, q)
        # apply pagination and sorting
        query = s.apply_sorting(q, Audit).offset(p.offset).limit(p.limit)
        audit_logs = (await db.exec(query)).all()

        # construct the response data
        response_data = [audit_log.model_dump() for audit_log in audit_logs]

        return PaginationData(total=total, items=response_data)
    except Exception as e:
        await db.rollback()
        msg = f"Failed to get audit logs: {str(e)}"
        logger.error(msg)
        return PaginationData(total=0, items=[])


async def create_audit_log(db: AsyncSession, username: str, action: str, result: str, detail: str):
    try:
        user_id = (await db.exec(select(RUser.id).where(RUser.email == username))).one()
        if user_id is None:
            logger.error(f"User {username} not found")
            return
        new_audit_log = Audit(username=username,
                              user_id=user_id,
                              audit_time=datetime.utcnow(),
                              action=action,
                              result=result,
                              detail=detail)
        db.add(new_audit_log)
        await db.commit()

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create audit log: {str(e)}")
