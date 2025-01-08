from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_versionizer import api_version
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.postgres.session import get_session
from app.responses import GeneralResponse, PaginationData, PaginatedParams
from app.sorting import SortingParams
from . import schemas
from . import service

router = APIRouter()


@api_version(major=1)
@router.get("/audit_logs",
            response_model=GeneralResponse[PaginationData[schemas.AuditResponse]],
            summary="Get audit logs.")
async def get_audit_logs(db: AsyncSession = Depends(get_session),
                         username: Optional[str] = Query(None, description="Filter by user name"),
                         action: Optional[str] = Query(None, description="Filter by action type"),
                         result: Optional[str] = Query(None, description="Filter by result"),
                         p: PaginatedParams = Depends(PaginatedParams),
                         s: SortingParams = Depends(SortingParams)
                         ) -> GeneralResponse[PaginationData[schemas.AuditResponse]]:
    # construct filters dictionary
    filters = {}
    if username:
        filters["username"] = username
    if action:
        filters["action"] = action
    if result:
        filters["result"] = result

    paged_audit_logs = await service.get_audit_logs(db, p, s, filters=filters)
    return GeneralResponse(code=0, message="Audit records retrieved successfully", data=paged_audit_logs)
