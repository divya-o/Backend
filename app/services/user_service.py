import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result =await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        # Check duplicate email
        existing =await UserService.get_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",)
        user = User(
            email =data.email.lower(),
            full_name=data.full_name,
            hashed_password=  hash_password(data.password),
            role =data.role,
        )
        db.add(user)
        await db.flush() 
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> User:
        user= await UserService.get_by_id(db, user_id)
        update_data= data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete(db: AsyncSession, user_id: uuid.UUID) -> None:
        user =await UserService.get_by_id(db, user_id)
        await db.delete(user)
        await db.flush()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        role: UserRole | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,) -> tuple[int, list[User]]:
        query= select(User)
        if role is not None:
            query= query.where(User.role == role)
        if is_active is not None:
            query =query.where(User.is_active == is_active)

        #ttotal count
        count_result= await db.execute(select(func.count()).select_from(query.subquery()))
        total =count_result.scalar_one()

        #paginated resultss
        offset= (page - 1) * page_size
        result =await db.execute(query.offset(offset).limit(page_size).order_by(User.created_at.desc()))
        users= result.scalars().all()

        return total, list(users)

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User:
        user =await UserService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",)
        return user

    @staticmethod
    async def change_password(
        db: AsyncSession, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",)
        user.hashed_password = hash_password(new_password)
        await db.flush()
