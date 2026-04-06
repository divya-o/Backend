import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.financial_record import RecordType

#request
class RecordCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    type: RecordType
    category: str = Field(..., min_length=1, max_length=100)
    record_date: date
    notes: str | None = Field(None, max_length=1000)

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: str) -> str:
        return v.strip().lower()


class RecordUpdate(BaseModel):
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    type: RecordType | None = None
    category: str | None = Field(None, min_length=1, max_length=100)
    record_date: date | None = None
    notes: str | None = None

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: str | None) -> str | None:
        return v.strip().lower() if v else v


#filter

class RecordFilter(BaseModel):
    type: RecordType | None = None
    category: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


#responesee

class RecordResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    amount: Decimal
    type: RecordType
    category: str
    record_date: date
    notes: str | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    records: list[RecordResponse]
