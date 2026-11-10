"""
FraudShield API v1 Root Router Assembly.
"""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    analytics,
    auth,
    health,
    models,
    predictions,
    transactions,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(predictions.router)
api_router.include_router(transactions.router)
api_router.include_router(analytics.router)
api_router.include_router(models.router)

