from decimal import Decimal

from sqlalchemy import case, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecord, RecordType
from app.schemas.dashboard import CategoryTotal, DashboardSummary, MonthlyTrend, RecentRecord


class DashboardService:

    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        #total income / expense / net 
        totals_result =await db.execute(
            select(
                func.sum(
                    case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)
                ).label("total_income"),
                func.sum(
                    case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)
                ).label("total_expense"),
                func.count(FinancialRecord.id).label("total_records"),
            )
        )
        totals =totals_result.one()
        total_income =Decimal(str(totals.total_income or 0))
        total_expense =Decimal(str(totals.total_expense or 0))
        net_balance =total_income - total_expense
        total_records =totals.total_records or 0

        #Category-wise totals
        category_result = await db.execute(
            select(
                FinancialRecord.category,
                func.sum(FinancialRecord.amount).label("total"),
                func.count(FinancialRecord.id).label("count"),
            )
            .group_by(FinancialRecord.category)
            .order_by(func.sum(FinancialRecord.amount).desc()))
        category_totals =[
            CategoryTotal(
                category=row.category,
                total=Decimal(str(row.total)),
                count=row.count,
            )
            for row in category_result.all()
        ]

        #Monthly trends (last 12 months)
        monthly_result =await db.execute(
            select(
                extract("year", FinancialRecord.record_date).label("year"),
                extract("month", FinancialRecord.record_date).label("month"),
                func.sum(
                    case((FinancialRecord.type == RecordType.income, FinancialRecord.amount), else_=0)
                ).label("income"),
                func.sum(
                    case((FinancialRecord.type == RecordType.expense, FinancialRecord.amount), else_=0)
                ).label("expense"),
            )
            .group_by("year", "month")
            .order_by("year", "month")
            .limit(12)
        )
        monthly_trends =[
            MonthlyTrend(
                year=int(row.year),
                month=int(row.month),
                income=Decimal(str(row.income or 0)),
                expense=Decimal(str(row.expense or 0)),
                net=Decimal(str(row.income or 0)) - Decimal(str(row.expense or 0)),
            )
            for row in monthly_result.all()
        ]

        #Recent 10 records
        recent_result =await db.execute(
            select(FinancialRecord)
            .order_by(FinancialRecord.record_date.desc(), FinancialRecord.created_at.desc())
            .limit(10)
        )
        recent_records =[
            RecentRecord(
                id=str(r.id),
                amount=Decimal(str(r.amount)),
                type=r.type.value,
                category=r.category,
                record_date=str(r.record_date),
                notes=r.notes,
            )
            for r in recent_result.scalars().all()
        ]

        return DashboardSummary(
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            total_records=total_records,
            category_totals=category_totals,
            monthly_trends=monthly_trends,
            recent_records=recent_records,
        )
