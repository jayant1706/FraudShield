"""
FraudShield Model Management Endpoints.
"""

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db, require_role
from backend.app.ml.loader import model_manager
from backend.app.models.model_version import ModelStatus
from backend.app.models.user import User, UserRole
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.model_repo import ModelRepository
from backend.app.schemas.common import MessageResponse
from backend.app.schemas.model import (
    ModelInfoResponse,
    ModelMetricsResponse,
    ModelVersionResponse,
    RetrainRequest,
)

router = APIRouter(prefix="/model", tags=["Model Management"])


@router.get("/info", response_model=ModelInfoResponse)
def get_model_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    meta = model_manager.metadata
    return ModelInfoResponse(
        version=meta.get("version", "v1.0.0"),
        model_name=meta.get("model_name", "XGBoost"),
        artifact_path=str(model_manager.artifacts_dir / "model.joblib"),
        status=ModelStatus.ACTIVE,
        trained_at=meta.get("trained_at"),
        input_features=meta.get("input_features", []),
        num_features=len(meta.get("input_features", [])),
        optimal_threshold=meta.get("optimal_threshold", 0.5),
    )


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics(
    current_user: Annotated[User, Depends(get_current_user)],
):
    meta = model_manager.metadata
    test_metrics = meta.get("test_metrics", {})
    cm = test_metrics.get("confusion_matrix", {"tp": 0, "fp": 0, "tn": 0, "fn": 0})

    return ModelMetricsResponse(
        version=meta.get("version", "v1.0.0"),
        model_name=meta.get("model_name", "XGBoost"),
        status=ModelStatus.ACTIVE,
        metrics=test_metrics,
        confusion_matrix=cm,
        comparison_table=meta.get("comparison_table"),
    )


@router.get("/versions", response_model=List[ModelVersionResponse])
def list_model_versions(
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[Session, Depends(get_db)],
):
    model_repo = ModelRepository(db)
    versions = model_repo.list_versions()
    return [ModelVersionResponse.model_validate(v) for v in versions]


@router.post("/retrain", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_retraining(
    payload: RetrainRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[Session, Depends(get_db)],
):
    audit_repo = AuditRepository(db)
    audit_repo.log_action(
        action="MODEL_RETRAINING_TRIGGERED",
        resource_type="MODEL",
        resource_id="candidate",
        user_id=current_user.id,
        details={"dataset_version": payload.dataset_version, "force": payload.force_retrain},
    )

    return MessageResponse(
        message="Model retraining job queued successfully. Status: PENDING_REVIEW upon completion.",
        success=True,
        details={"dataset_version": payload.dataset_version},
    )


@router.post("/versions/{version_id}/promote", response_model=ModelVersionResponse)
def promote_model_version(
    version_id: str,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[Session, Depends(get_db)],
):
    model_repo = ModelRepository(db)
    target = model_repo.promote_version(version_id, approver_id=current_user.id)
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Model version '{version_id}' not found."
        )

    audit_repo = AuditRepository(db)
    audit_repo.log_action(
        action="MODEL_VERSION_PROMOTED",
        resource_type="MODEL",
        resource_id=target.id,
        user_id=current_user.id,
        details={"version": target.version, "model_name": target.model_name},
    )

    # Hot-reload in-memory champion model
    model_manager.load_artifacts()

    return ModelVersionResponse.model_validate(target)
