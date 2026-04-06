import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import RequireAdmin, CurrentUser
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("", response_model=UserListResponse, dependencies=[RequireAdmin])
@limiter.limit("30/minute")
async def list_users(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    role: UserRole | None = Query(None, description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all users. Admin only."""
    total, users = await UserService.list_users(db, role, is_active, page, page_size)
    return UserListResponse(total=total, users=users)


@router.post("", response_model=UserResponse, status_code=201, dependencies=[RequireAdmin])
@limiter.limit("20/minute")
async def create_user(
    request: Request,
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new user (admin can assign any role). Admin only."""
    user = await UserService.create(db, data)
    return user


@router.get("/{user_id}", response_model=UserResponse, dependencies=[RequireAdmin])
async def get_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific user by ID. Admin only."""
    return await UserService.get_by_id(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse, dependencies=[RequireAdmin])
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a user's role or status. Admin only."""
    return await UserService.update(db, user_id, data)


@router.delete("/{user_id}", status_code=204, dependencies=[RequireAdmin])
async def delete_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a user. Admin only. Cannot delete yourself."""
    from fastapi import HTTPException, status
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )
    await UserService.delete(db, user_id)
