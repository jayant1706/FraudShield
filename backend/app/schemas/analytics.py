"""
FraudShield Analytics and Dashboard Reporting Schemas.
"""

from typing import Any, Dict, List
from pydantic import BaseModel


class AnalyticsOverview(BaseModel):
    total_transactions: int
    fraudulent_transactions: int
    legitimate_transactions: int
    pending_investigations: int
    flagged_transactions: int
    fraud_rate_percentage: float
    total_dollar_volume: float
    fraud_dollar_volume: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class FraudTrendPoint(BaseModel):
    timestamp: str
    total_volume: int
    fraud_count: int
    total_amount: float
    fraud_amount: float


class FraudTrendsResponse(BaseModel):
    trends: List[FraudTrendPoint]


class RiskDistributionItem(BaseModel):
    risk_level: str
    count: int
    percentage: float


class RiskDistributionResponse(BaseModel):
    distribution: List[RiskDistributionItem]


class VolumePoint(BaseModel):
    date: str
    transaction_count: int
    dollar_volume: float


class TransactionVolumeResponse(BaseModel):
    volume: List[VolumePoint]

