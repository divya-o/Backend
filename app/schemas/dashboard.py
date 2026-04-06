from decimal import Decimal

from pydantic import BaseModel


class CategoryTotal(BaseModel):
    category: str
    total: Decimal
    count: int

class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal
class RecentRecord(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    amount: Decimal
    type: str
    category: str
    record_date: str
    notes: str | None




class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_balance: Decimal
    total_records: int
    category_totals: list[CategoryTotal]
    monthly_trends: list[MonthlyTrend]
    recent_records: list[RecentRecord]
