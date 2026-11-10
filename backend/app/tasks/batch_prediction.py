"""
FraudShield Async Batch Prediction Task.
High-throughput asynchronous bulk transaction inference and persistence.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any

import numpy as np
import pandas as pd

from backend.app.tasks.celery_app import celery_app
from backend.app.ml.loader import model_loader
from backend.app.services.risk_engine import risk_engine
from backend.app.db.session import SessionLocal
from backend.app.models.transaction import Transaction
from backend.app.models.prediction import Prediction
from backend.app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="fraudshield.batch_predict")
def batch_predict_task(
    self,
    transactions_data: List[Dict[str, Any]],
    user_id: str = "system",
) -> Dict[str, Any]:
    """
    Process high-volume bulk transaction batch asynchronously.
    """
    start_time = time.time()
    total_records = len(transactions_data)
    logger.info(f"Starting batch prediction task {self.request.id} for {total_records} transactions")

    if total_records == 0:
        return {"status": "SUCCESS", "total_processed": 0, "predictions": []}

    self.update_state(state="PROCESSING", meta={"progress": 20, "status": "Formatting feature vectors"})

    # Extract features for vectorized batch inference
    feature_names = model_loader.feature_names
    records_matrix = []
    for item in transactions_data:
        feats = item.get("features", {})
        row = [
            feats.get("Time", 0.0),
            *[feats.get(f"V{i}", 0.0) for i in range(1, 29)],
            float(item.get("amount", 0.0)),
        ]
        records_matrix.append(row)

    feature_df = pd.DataFrame(records_matrix, columns=feature_names)

    self.update_state(state="PROCESSING", meta={"progress": 50, "status": "Running batch ML inference"})

    probabilities = model_loader.predict_proba_batch(feature_df)
    predictions_binary = (probabilities >= model_loader.optimal_threshold).astype(int)

    self.update_state(state="PROCESSING", meta={"progress": 75, "status": "Persisting transactions & predictions"})

    session = SessionLocal()
    fraud_count = 0
    high_risk_count = 0
    saved_ids = []

    try:
        for idx, item in enumerate(transactions_data):
            prob = float(probabilities[idx])
            pred_class = int(predictions_binary[idx])

            # Evaluate heuristic risk engine
            risk_assessment = risk_engine.evaluate(
                amount=float(item.get("amount", 0.0)),
                ml_probability=prob,
                user_id=item.get("user_id"),
                merchant_category=item.get("merchant_category"),
                location=item.get("location"),
                device_id=item.get("device_id"),
            )

            if pred_class == 1:
                fraud_count += 1
            if risk_assessment.risk_level == "HIGH":
                high_risk_count += 1

            # Persist transaction
            db_txn = Transaction(
                external_transaction_id=item.get("transaction_id", f"TXN_BATCH_{idx}_{int(time.time())}"),
                amount=float(item.get("amount", 0.0)),
                merchant_category=item.get("merchant_category", "retail"),
                device_id=item.get("device_id"),
                location=item.get("location"),
                user_id=item.get("user_id"),
                status="FLAGGED" if risk_assessment.risk_level == "HIGH" else "PENDING",
            )
            session.add(db_txn)
            session.flush()

            # Persist prediction
            db_pred = Prediction(
                transaction_id=db_txn.id,
                fraud_probability=prob,
                predicted_class=pred_class,
                risk_level=risk_assessment.risk_level,
                recommended_action=risk_assessment.recommended_action,
                model_version=model_loader.model_version,
                inference_latency_ms=0.5,
                rule_triggers=risk_assessment.rule_triggers,
                explanation=[{"feature": "Batch Scoring", "impact": "neutral"}],
            )
            session.add(db_pred)
            saved_ids.append(db_txn.id)

        # Audit Log
        audit = AuditLog(
            user_id=user_id,
            action="BATCH_INFERENCE_PROCESSED",
            resource_type="batch_job",
            resource_id=self.request.id,
            details={
                "total_records": total_records,
                "fraud_count": fraud_count,
                "high_risk_count": high_risk_count,
            },
        )
        session.add(audit)
        session.commit()

        elapsed = time.time() - start_time
        logger.info(f"Batch task {self.request.id} processed {total_records} records in {elapsed:.2f}s")

        return {
            "task_id": self.request.id,
            "status": "COMPLETED",
            "total_processed": total_records,
            "fraud_predictions": fraud_count,
            "high_risk_flags": high_risk_count,
            "fraud_rate_pct": round((fraud_count / max(total_records, 1)) * 100, 3),
            "execution_time_seconds": round(elapsed, 3),
            "throughput_tx_per_sec": round(total_records / max(elapsed, 0.001), 1),
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to process batch task: {e}", exc_info=True)
        raise e
    finally:
        session.close()

