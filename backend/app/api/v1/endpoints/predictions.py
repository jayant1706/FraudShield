"""
FraudShield Prediction Endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.core.exceptions import ModelInferenceError, ResourceNotFoundError
from backend.app.models.user import User
from backend.app.schemas.prediction import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)
from backend.app.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def predict_transaction(
    payload: PredictionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prediction_service = PredictionService(db)
    try:
        return prediction_service.predict_single(payload)
    except ModelInferenceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/batch", response_model=BatchPredictionResponse, status_code=status.HTTP_200_OK)
def predict_batch_transactions(
    payload: BatchPredictionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prediction_service = PredictionService(db)
    try:
        return prediction_service.predict_batch(payload)
    except ModelInferenceError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction_by_id(
    prediction_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    prediction_service = PredictionService(db)
    try:
        return prediction_service.get_prediction_by_id(prediction_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
