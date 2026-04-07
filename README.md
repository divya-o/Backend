# finance-backend

A role-based finance management backend built with FastAPI, PostgreSQL, and async SQLAlchemy.

## Project Structure

```bash
finance-backend/
├── app/
│   ├── api/v1/         # API routes
│   ├── core/           # config, security, dependencies
│   ├── db/             # database setup
│   ├── models/         # ORM models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # business logic
│   └── main.py         # app entry point
├── alembic/            # Database migrations
├── seed.py             # Seed data script
├── docker-compose.yml
├── requirements.txt
└── .env
```

- Framework-FastAPI 0.111
- Language-Python 3.11+
-  Database-PostgreSQL 17
- ORM-SQLAlchemy 2.0 (async) 
-  Migrations-Alembic -
-  Auth-JWT via python-jose + bcrypt
-  Validation-Pydantic v2
-  Rate Limiting-slowapi (limits library)
-  Local DB-Docker + docker-compose

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start database (Docker)

```bash
docker-compose up -d
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Seed initial data

```bash
python seed.py
```

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

**API URL**: `http://localhost:8000`  
**Interactive Docs**: `http://localhost:8000/docs`

## Authentication

JWT-based authentication:

- **Access Token**: 30 minutes validity
- **Refresh Token**: 7 days validity

## Roles

| Role      | Permissions                        |
|-----------|------------------------------------|
| Viewer    | Dashboard access only              |
| Analyst   | Read records + Dashboard           |
| Admin     | Full CRUD access (users & records) |

## Core Endpoints

### Auth Endpoints
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /auth/me`

### Users (Admin only)
- `GET /users`
- `POST /users`
- `PATCH /users/{id}`
- `DELETE /users/{id}`

### Financial Records
- `GET /records`
- `POST /records`
- `PATCH /records/{id}`
- `DELETE /records/{id}`

### Dashboard
- `GET /dashboard/summary`

## Data Models

### User
- `id` (UUID)
- `email` (unique)
- `password` (hashed)
- `role` (viewer, analyst, admin)

### FinancialRecord
- `id` (UUID)
- `amount` (Decimal)
- `type` (income / expense)
- `category` (string)
- `record_date` (date)

## Key Design Choices

- Fully asynchronous stack for better performance
- UUIDs as primary keys for security
- Service layer for clean separation of concerns
- Stateless JWT authentication
- Strict ENUM validation for roles and record types

## Running Without Docker

Update your `.env` file with:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/finance_db
```

Then create the database manually and run migrations + seed script.

## future additions

- Cursor-based pagination
- Soft deletes
- Audit logging
- Data export
- Email verification
- Redis-based rate limiting
