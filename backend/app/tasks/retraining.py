"""
FraudShield Model Retraining Background Task.
Trains candidate models, computes validation metrics, and stages updates in the Model Registry.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import joblib
import numpy as np
import pandas as pd

from backend.app.tasks.celery_app import celery_app
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models.model_version import ModelVersion
from backend.app.models.audit_log import AuditLog
from ml.src.data.ingestion import BenchmarkDataGenerator
from ml.src.features.preprocessor import DataPreprocessor
from ml.src.models.train_xgboost import XGBoostFraudModel
from ml.src.evaluation.metrics import evaluate_classification

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="fraudshield.retrain_model")
def retrain_model_task(
    self,
    dataset_version: str = "latest",
    force_retrain: bool = False,
    n_samples: int = 50000,
) -> Dict[str, Any]:
    """
    Background worker task to retrain fraud detection model on fresh transaction batches.
    """
    logger.info(f"Starting model retraining job: {self.request.id}")
    self.update_state(state="PROCESSING", meta={"progress": 10, "status": "Ingesting training data"})

    # 1. Ingest Data
    gen = BenchmarkDataGenerator(n_samples=n_samples, fraud_ratio=0.00172, random_state=int(datetime.utcnow().timestamp()) % 10000)
    df = gen.generate()
    logger.info(f"Generated {len(df)} records for retraining batch")

    self.update_state(state="PROCESSING", meta={"progress": 30, "status": "Preprocessing features"})

    # 2. Preprocess
    preprocessor = DataPreprocessor(target_col="Class", random_state=42)
    splits = preprocessor.fit_transform(df)

    self.update_state(state="PROCESSING", meta={"progress": 50, "status": "Training candidate XGBoost"})

    # 3. Train Candidate XGBoost
    scale_pos_weight = (len(splits.y_train) - sum(splits.y_train)) / max(sum(splits.y_train), 1)
    candidate_model = XGBoostFraudModel(
        scale_pos_weight=scale_pos_weight,
        max_depth=5,
        n_estimators=100,
        learning_rate=0.08,
    )
    candidate_model.fit(
        splits.X_train,
        splits.y_train,
        eval_set=[(splits.X_val, splits.y_val)],
        verbose=False,
    )

    self.update_state(state="PROCESSING", meta={"progress": 75, "status": "Evaluating validation metrics"})

    # 4. Evaluate Candidate Model
    y_pred_val = candidate_model.predict(splits.X_val)
    y_prob_val = candidate_model.predict_proba(splits.X_val)
    candidate_metrics = evaluate_classification(splits.y_val, y_pred_val, y_prob_val)

    # 5. Model Registry Staging
    new_version_tag = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    artifacts_dir = Path(settings.ARTIFACTS_DIR) / "candidates" / new_version_tag
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifacts_dir / "candidate_model.joblib"
    joblib.dump(candidate_model, model_path)

    # 6. Database Update
    session = SessionLocal()
    try:
        current_active = (
            session.query(ModelVersion)
            .filter(ModelVersion.status == "ACTIVE")
            .first()
        )
        current_pr_auc = current_active.metrics.get("pr_auc", 0.0) if current_active and current_active.metrics else 0.0

        is_superior = candidate_metrics.pr_auc > current_pr_auc
        initial_status = "CANDIDATE" if not (force_retrain and is_superior) else "ACTIVE"

        if initial_status == "ACTIVE" and current_active:
            current_active.status = "DEPRECATED"

        model_version_record = ModelVersion(
            version=new_version_tag,
            model_name="XGBoost Fraud Classifier (Automated Retrain)",
            artifact_path=str(model_path),
            metrics={
                "pr_auc": float(candidate_metrics.pr_auc),
                "roc_auc": float(candidate_metrics.roc_auc),
                "f1": float(candidate_metrics.f1),
                "precision": float(candidate_metrics.precision),
                "recall": float(candidate_metrics.recall),
                "previous_champion_pr_auc": float(current_pr_auc),
                "superior_to_champion": bool(is_superior),
            },
            status=initial_status,
        )
        session.add(model_version_record)

        # Audit Log
        audit = AuditLog(
            action="MODEL_RETRAIN_COMPLETED",
            resource_type="model_version",
            resource_id=new_version_tag,
            details={
                "task_id": self.request.id,
                "metrics": model_version_record.metrics,
                "status": initial_status,
            },
        )
        session.add(audit)
        session.commit()

        logger.info(f"Retraining finished. Registered model {new_version_tag} with status {initial_status}")

        return {
            "task_id": self.request.id,
            "version": new_version_tag,
            "status": initial_status,
            "is_superior": is_superior,
            "metrics": {
                "pr_auc": candidate_metrics.pr_auc,
                "roc_auc": candidate_metrics.roc_auc,
                "f1": candidate_metrics.f1,
                "precision": candidate_metrics.precision,
                "recall": candidate_metrics.recall,
            },
        }
    finally:
        session.close()

