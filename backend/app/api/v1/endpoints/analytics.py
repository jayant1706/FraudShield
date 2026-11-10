"""
FraudShield Analytics Endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, require_role
from backend.app.models.user import User, UserRole
from backend.app.schemas.analytics import (
    AnalyticsOverview,
    FraudTrendsResponse,
    RiskDistributionResponse,
    TransactionVolumeResponse,
)
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def get_overview(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR))],
    db: Annotated[Session, Depends(get_db)],
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_overview()


@router.get("/fraud-trends", response_model=FraudTrendsResponse)
def get_fraud_trends(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR))],
    db: Annotated[Session, Depends(get_db)],
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_fraud_trends()


@router.get("/risk-distribution", response_model=RiskDistributionResponse)
def get_risk_distribution(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR))],
    db: Annotated[Session, Depends(get_db)],
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_risk_distribution()


@router.get("/transaction-volume", response_model=TransactionVolumeResponse)
def get_transaction_volume(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR))],
    db: Annotated[Session, Depends(get_db)],
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_transaction_volume()
