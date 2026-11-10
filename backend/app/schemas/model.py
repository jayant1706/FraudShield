"""
FraudShield Model Management and Governance Schemas.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict

from backend.app.models.model_version import ModelStatus


class ModelInfoResponse(BaseModel):
    version: str
    model_name: str
    artifact_path: str
    status: ModelStatus
    trained_at: Optional[str] = None
    input_features: List[str]
    num_features: int
    optimal_threshold: float


class ModelMetricsResponse(BaseModel):
    version: str
    model_name: str
    status: ModelStatus
    metrics: Dict[str, Any]
    confusion_matrix: Dict[str, int]
    comparison_table: Optional[List[Dict[str, Any]]] = None


class ModelVersionResponse(BaseModel):
    id: str
    version: str
    model_name: str
    artifact_path: str
    metrics: Dict[str, Any]
    status: ModelStatus
    approved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetrainRequest(BaseModel):
    dataset_version: Optional[str] = "latest"
    force_retrain: bool = False

