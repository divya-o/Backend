import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.financial_record import RecordCreate, RecordFilter, RecordUpdate


class RecordService:

    @staticmethod
    async def get_by_id(db: AsyncSession, record_id: uuid.UUID) -> FinancialRecord:
        result =await db.execute(
            select(FinancialRecord).where(FinancialRecord.id == record_id)
        )
        record =result.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Financial record not found",
            )
        return record

    @staticmethod
    async def create(
        db: AsyncSession, data: RecordCreate, created_by: uuid.UUID) -> FinancialRecord:
        record =FinancialRecord(
            amount=data.amount,
            type=data.type,
            category=data.category,
            record_date=data.record_date,
            notes=data.notes,
            created_by=created_by,
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        return record

    @staticmethod
    async def update(
        db: AsyncSession, record_id: uuid.UUID, data: RecordUpdate   ) -> FinancialRecord:
        record =await RecordService.get_by_id(db, record_id)
        update_data =data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        await db.flush()
        await db.refresh(record)
        return record

    @staticmethod
    async def delete(db: AsyncSession, record_id: uuid.UUID) -> None:
        record = await RecordService.get_by_id(db, record_id)
        await db.delete(record)
        await db.flush()

    @staticmethod
    async def list_records(
        db: AsyncSession, filters: RecordFilter) -> tuple[int, list[FinancialRecord]]:
        query = select(FinancialRecord)

        # Apply filters
        if filters.type is not None:
            query = query.where(FinancialRecord.type == filters.type)
        if filters.category is not None:
            query = query.where(
                FinancialRecord.category == filters.category.strip().lower())
        if filters.date_from is not None:
            query = query.where(FinancialRecord.record_date >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(FinancialRecord.record_date <= filters.date_to)

        #count total before pagination
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery()))
        total = count_result.scalar_one()

     
        offset = (filters.page - 1) * filters.page_size
        result = await db.execute(
            query.order_by(FinancialRecord.record_date.desc())
            .offset(offset)
            .limit(filters.page_size))

        records = result.scalars().all()

        return total, list(records)
