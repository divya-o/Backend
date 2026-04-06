import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, RequireAdmin, require_roles
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.financial_record import RecordType
from app.models.user import UserRole
from app.schemas.financial_record import (
    RecordCreate,
    RecordFilter,
    RecordListResponse,
    RecordResponse,
    RecordUpdate,
)
from app.services.record_service import RecordService

router = APIRouter(prefix="/records", tags=["Financial Records"])

# Analyst + Admin can read; Admin only can write
_can_read = Depends(require_roles(UserRole.analyst, UserRole.admin))
_can_write = RequireAdmin


@router.get("", response_model=RecordListResponse, dependencies=[_can_read])
@limiter.limit("60/minute")
async def list_records(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    type: RecordType | None = Query(None),
    category: str | None = Query(None),
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    date_to: str | None = Query(None, description="YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    
    from datetime import date

    def parse_date(s: str | None):
        return date.fromisoformat(s) if s else None

    filters = RecordFilter(
        type=type,
        category=category,
        date_from=parse_date(date_from),
        date_to=parse_date(date_to),
        page=page,
        page_size=page_size,
    )
    total, records = await RecordService.list_records(db, filters)
    return RecordListResponse(
        total=total, page=page, page_size=page_size, records=records
    )


@router.post("", response_model=RecordResponse, status_code=201, dependencies=[_can_write])
@limiter.limit("30/minute")
async def create_record(
    request: Request,
    data: RecordCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new financial record. **Admin only.**"""
    record = await RecordService.create(db, data, created_by=current_user.id)
    return record


@router.get("/{record_id}", response_model=RecordResponse, dependencies=[_can_read])
async def get_record(
    record_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single financial record. Analyst and Admin only"""
    return await RecordService.get_by_id(db, record_id)


@router.patch("/{record_id}", response_model=RecordResponse, dependencies=[_can_write])
async def update_record(
    record_id: uuid.UUID,
    data: RecordUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a financial record. **Admin only**"""
    return await RecordService.update(db, record_id, data)


@router.delete("/{record_id}", status_code=204, dependencies=[_can_write])
async def delete_record(
    record_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a financial record. **Admin only**"""
    await RecordService.delete(db, record_id)
