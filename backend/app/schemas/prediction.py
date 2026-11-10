"""
FraudShield Prediction Request and Response Schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.prediction import RecommendedAction, RiskLevel


class FeatureAttribution(BaseModel):
    feature: str
    impact: str
    value: Optional[float] = None
    shap_value: Optional[float] = None


class PredictionRequest(BaseModel):
    transaction_id: str = Field(..., description="External unique transaction identifier")
    amount: float = Field(..., gt=0, description="Transaction monetary amount")
    transaction_time: Optional[datetime] = Field(None, description="Timestamp of transaction")
    merchant_category: str = Field("retail", description="Merchant category or MCC")
    device_id: Optional[str] = Field(None, description="Device fingerprint identifier")
    location: Optional[str] = Field(None, description="Geographic location or IP country")
    user_id: Optional[str] = Field(None, description="Associated account or user ID")
    features: Optional[Dict[str, float]] = Field(
        None,
        description="Optional pre-computed PCA feature dictionary (V1 to V28)",
    )


class BatchPredictionRequest(BaseModel):
    transactions: List[PredictionRequest] = Field(..., min_length=1, max_length=1000)


class PredictionResponse(BaseModel):
    prediction_id: str
    transaction_id: str
    fraud_probability: float
    prediction: str  # "LEGITIMATE" or "FRAUD"
    risk_level: RiskLevel
    recommended_action: RecommendedAction
    model_version: str
    inference_latency_ms: float
    rule_triggers: List[str] = []
    explanations: List[FeatureAttribution] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchPredictionResponse(BaseModel):
    total_processed: int
    predictions: List[PredictionResponse]
    summary: Dict[str, Any]

