"""
FraudShield Transaction Schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from backend.app.models.transaction import TransactionStatus
from backend.app.schemas.prediction import PredictionResponse


class TransactionCreate(BaseModel):
    external_transaction_id: str = Field(..., min_length=3, max_length=100)
    amount: float = Field(..., gt=0)
    transaction_time: Optional[datetime] = None
    merchant_category: str = Field(..., min_length=2, max_length=100)
    device_id: Optional[str] = None
    location: Optional[str] = None
    user_id: Optional[str] = None


class TransactionStatusUpdate(BaseModel):
    status: TransactionStatus
    investigation_notes: Optional[str] = Field(None, max_length=2000)


class TransactionResponse(BaseModel):
    id: str
    external_transaction_id: str
    user_id: Optional[str] = None
    amount: float
    transaction_time: datetime
    merchant_category: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    status: TransactionStatus
    investigation_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    prediction: Optional[PredictionResponse] = None

    model_config = ConfigDict(from_attributes=True)

