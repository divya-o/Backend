from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1 import auth, dashboard, records, users
from app.core.config import settings
from app.core.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:Alembic handles migrations
    yield
    # Shutdown: dispose the engine
    from app.db.session import engine
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
## Finance Dashboard API

A role-based finance management backend with:

-  **JWT Authentication** (access + refresh tokens)
- **Role-Based Access Control** (Viewer / Analyst / Admin)
- **Financial Records** CRUD with filtering
- **Dashboard Analytics** (totals, trends, categories)
- **Rate Limiting** per IP address

### Roles
| Role     | Dashboard | Records (Read) | Records (Write) | User Management |
|----------|-----------|----------------|-----------------|-----------------|
| Viewer   | GOOD        |BAD             | BAD              | BAD              |
| Analyst  | GOOD        | GOOD              | BAD              | BAD              |
| Admin    | GOOD        | GOOD              | GOOD              | GOOD              |
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

#Rate limiter 
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

#CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#Global exception handler 
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Try again later"},
    )


#Health check 
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


#Routers
PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)

app.include_router(users.router, prefix=PREFIX)

app.include_router(records.router, prefix=PREFIX)

app.include_router(dashboard.router, prefix=PREFIX)
