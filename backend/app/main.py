"""
FraudShield Enterprise FastAPI Application Entrypoint.
Modular Monolith ASGI application for financial transaction fraud detection and monitoring.
"""

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Ensure Matplotlib uses a writable directory inside workspace
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent.parent.parent / ".matplotlib_cache"))

from backend.app.api.v1.endpoints import health
from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.exceptions import FraudShieldException
from backend.app.core.logging import setup_logging
from backend.app.db.init_db import init_db
from backend.app.middleware.logging_middleware import AccessLoggingMiddleware
from backend.app.middleware.request_id import RequestIdMiddleware
from backend.app.ml.loader import model_manager
from backend.app.monitoring.metrics import metrics_endpoint

logger = logging.getLogger("FraudShield.Main")

# Global Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application lifecycle: logging, database initialization, and ML artifact loading."""
    # --- Startup ---
    setup_logging()
    logger.info("Initializing FraudShield Application (%s)...", settings.ENVIRONMENT)

    # 1. Initialize DB and Seed initial data (skip in testing to use test fixtures)
    if settings.ENVIRONMENT != "testing":
        try:
            init_db()
        except Exception as e:
            logger.error("Database initialization failed: %s", e)

    # 2. Load Champion ML model artifacts
    try:
        model_manager.load_artifacts()
    except Exception as e:
        logger.error("Could not load ML artifacts: %s. Model must be trained before inference.", e)

    yield

    # --- Shutdown ---
    logger.info("Shutting down FraudShield application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Industry-grade AI-powered financial fraud detection platform. "
        "Provides real-time ML transaction scoring, calibrated probability calculation, "
        "SHAP-based feature attribution, and configurable deterministic risk rule heuristics."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Attach SlowAPI Limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
app.add_middleware(AccessLoggingMiddleware)
app.add_middleware(RequestIdMiddleware)


# Global Exception Handlers
@app.exception_handler(FraudShieldException)
async def custom_exception_handler(request: Request, exc: FraudShieldException):
    req_id = getattr(request.state, "request_id", None)
    logger.warning("Domain exception: %s [ReqID: %s]", exc.message, req_id)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "status_code": status.HTTP_400_BAD_REQUEST,
            "request_id": req_id,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", None)
    logger.warning("Input validation error: %s [ReqID: %s]", exc.errors(), req_id)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Input validation failed. Please check field requirements.",
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "request_id": req_id,
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", None)
    logger.error("Unhandled server exception: %s [ReqID: %s]", exc, req_id, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An internal server error occurred. Please contact system support.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "request_id": req_id,
        },
    )


# Prometheus Telemetry Route
@app.get("/metrics", include_in_schema=False)
def metrics():
    return metrics_endpoint()


# Root endpoint
@app.get("/", tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


# Assemble v1 API Router & Probes
app.include_router(health.router)
app.include_router(api_router, prefix=settings.API_V1_STR)
