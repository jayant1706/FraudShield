"""
FraudShield Health and Readiness Probes.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.core.config import settings
from backend.app.ml.loader import model_manager

router = APIRouter(tags=["Health & Probes"])


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(
    db: Annotated[Session, Depends(get_db)],
):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    model_ok = model_manager.is_loaded

    is_ready = db_ok and model_ok
    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "ready": is_ready,
            "database_connected": db_ok,
            "model_loaded": model_ok,
            "champion_version": model_manager.metadata.get("version"),
        },
    )
