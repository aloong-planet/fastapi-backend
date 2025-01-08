from fastapi import APIRouter

from app.core.admin.router import router as admin_router
from app.core.audit.router import router as audit_router
from app.core.auth.rbac.router import router as rbac_router
from app.core.auth.router import router as auth_router

api_router = APIRouter()

api_router.include_router(audit_router, prefix="/audit", tags=["Audit"])

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(rbac_router, prefix="/auth", tags=["RBAC"])

api_router.include_router(admin_router, prefix="/admin")
