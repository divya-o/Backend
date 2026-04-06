import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecordType(str, enum.Enum):
    income ="income"
    expense ="expense"


class FinancialRecord(Base):
    __tablename__ ="financial_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[float] =mapped_column(Numeric(12, 2), nullable=False)
    type: Mapped[RecordType]= mapped_column(Enum(RecordType), nullable=False)
    
    category: Mapped[str] =mapped_column(String(100), nullable=False, index=True)
    record_date: Mapped[date]= mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None]=mapped_column(Text, nullable=True)

    # Who created this record
    created_by: Mapped[uuid.UUID]= mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_by_user: Mapped["User"]= relationship(  # noqa: F821
        back_populates="records")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<FinancialRecord {self.type} {self.amount} [{self.category}]>"
