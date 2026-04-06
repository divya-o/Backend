#seed script — run once after migrations to populate the database with--
import asyncio
import random
from datetime import date, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, engine
from app.models.financial_record import FinancialRecord, RecordType
from app.models.user import User, UserRole


SAMPLE_CATEGORIES = {
    RecordType.income: ["salary", "freelance", "investment", "bonus", "rental"],
    RecordType.expense: ["rent", "groceries", "utilities", "transport", "entertainment", "healthcare"],
}

SAMPLE_USERS = [
    {
        "email": "admin@finance.dev",
        "full_name": "Admin User",
        "password": "Admin1234",
        "role": UserRole.admin,
    },
    {
        "email": "analyst@finance.dev",
        "full_name": "Analyst User",
        "password": "Analyst1234",
        "role": UserRole.analyst,
    },
    {
        "email": "viewer@finance.dev",
        "full_name": "Viewer User",
        "password": "Viewer1234",
        "role": UserRole.viewer,
    },
]


async def seed():
    async with AsyncSessionLocal() as db:
        print("Seeding database")

        #create users 
        created_users: list[User] = []
        for u in SAMPLE_USERS:
            existing = await db.execute(select(User).where(User.email == u["email"]))
            if existing.scalar_one_or_none():
                print(f" User {u['email']} already exists — skipping")
                continue
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=hash_password(u["password"]),
                role=u["role"],
            )
            db.add(user)
            created_users.append(user)
            print(f" Created {u['role'].value}: {u['email']}  (password: {u['password']})")

        await db.flush()  # assign IDs

    
        result = await db.execute(select(User).where(User.email == "admin@finance.dev"))
        admin = result.scalar_one_or_none()
        if not admin:
            await db.commit()
            print(" Admin user not found after flush — aborting record seed")
            return

        today = date.today()
        for i in range(20):
            rtype = random.choice(list(RecordType))
            category = random.choice(SAMPLE_CATEGORIES[rtype])
            record_date = today - timedelta(days=random.randint(0, 180))
            amount = round(random.uniform(100, 5000), 2)

            record = FinancialRecord(
                amount=amount,
                type=rtype,
                category=category,
                record_date=record_date,
                notes=f"Sample {rtype.value} record #{i + 1}",
                created_by=admin.id,)
            db.add(record)

        await db.commit()
        print(f"Created 20 sample financial records (owned by admin)")
        print("Seeding complete!\n")
        print("─" * 50)
        print("Test credentials:")
        for u in SAMPLE_USERS:
            print(f"  {u['role'].value:10s} → {u['email']}  /  {u['password']}")
        print("─" * 50)


if __name__ == "__main__":
    asyncio.run(seed())
