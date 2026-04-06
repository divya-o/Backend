from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
@limiter.limit("30/minute")
async def get_dashboard_summary(
    request: Request,
    current_user: CurrentUser,  # all roles can view the dashboard
    db: Annotated[AsyncSession, Depends(get_db)],
):

    return await DashboardService.get_summary(db)
