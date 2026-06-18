"""DataInsight AI — FastAPI application entry point."""


import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select

from app.config import get_settings
from app.database import Base, engine
from app.models.user import User
from app.routers import admin, auth, charts, chat, cleaning, dashboard, datasets, predictions, reports
from app.utils.logging_config import setup_logging
from app.utils.security import get_password_hash

settings = get_settings()
logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_per_minute])


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default admin in development
    if settings.environment == "development":
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == "admin@datainsight.ai"))
            if not result.scalar_one_or_none():
                admin_user = User(
                    email="admin@datainsight.ai",
                    username="admin",
                    hashed_password=get_password_hash("Admin123!"),
                    full_name="System Admin",
                    is_admin=True,
                )
                session.add(admin_user)
                await session.commit()
                logger.info("Default admin created: admin@datainsight.ai / Admin123!")

    yield
    await engine.dispose()


app = FastAPI(
    title="DataInsight AI",
    description="Production-ready AI-powered Data Analysis Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/api/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    return {"status": "healthy", "service": "DataInsight AI", "version": "1.0.0"}


API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(datasets.router, prefix=API_PREFIX)
app.include_router(charts.router, prefix=API_PREFIX)
app.include_router(chat.router, prefix=API_PREFIX)
app.include_router(predictions.router, prefix=API_PREFIX)
app.include_router(cleaning.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)
app.include_router(admin.router, prefix=API_PREFIX)
