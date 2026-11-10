"""
FraudShield Data Drift & Statistical Distribution Monitoring Task.
Computes feature drift against training reference distributions to detect concept/data drift.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from backend.app.tasks.celery_app import celery_app
from backend.app.core.config import settings
from backend.app.db.session import SessionLocal
from backend.app.models.transaction import Transaction
from backend.app.models.prediction import Prediction
from backend.app.models.audit_log import AuditLog
from ml.src.data.ingestion import BenchmarkDataGenerator

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="fraudshield.monitor_drift")
def monitor_data_drift_task(
    self,
    p_value_threshold: float = 0.05,
    drift_share_threshold: float = 0.30,
) -> Dict[str, Any]:
    """
    Evaluate feature distribution drift between current production transactions and training baseline.
    """
    logger.info(f"Running automated data drift analysis job {self.request.id}")

    # 1. Load Reference Training Distribution
    # Generate reference baseline from generator
    ref_gen = BenchmarkDataGenerator(n_samples=5000, random_state=42)
    ref_df = ref_gen.generate()

    # 2. Extract Recent Production Transactions
    session = SessionLocal()
    try:
        recent_txns = (
            session.query(Transaction)
            .order_by(Transaction.created_at.desc())
            .limit(1000)
            .all()
        )

        if len(recent_txns) < 50:
            logger.info("Insufficient production transactions for statistical drift test (minimum 50 required)")
            return {
                "status": "SKIPPED",
                "message": f"Only {len(recent_txns)} transactions present; 50 required for significance.",
                "drift_detected": False,
            }

        curr_amounts = [t.amount for t in recent_txns]

        # 3. Statistical Kolmogorov-Smirnov Test for Amount
        ks_stat, ks_pval = ks_2samp(ref_df["Amount"].values, curr_amounts)
        amount_drifted = ks_pval < p_value_threshold

        feature_drift_results: Dict[str, Any] = {
            "Amount": {
                "ks_statistic": float(ks_stat),
                "p_value": float(ks_pval),
                "drift_detected": bool(amount_drifted),
                "reference_mean": float(np.mean(ref_df["Amount"].values)),
                "current_mean": float(np.mean(curr_amounts)),
            }
        }

        drifted_count = 1 if amount_drifted else 0
        total_features_evaluated = 1
        drift_share = drifted_count / total_features_evaluated
        overall_dataset_drift = drift_share >= drift_share_threshold

        drift_report = {
            "task_id": self.request.id,
            "timestamp": datetime.utcnow().isoformat(),
            "reference_sample_size": len(ref_df),
            "production_sample_size": len(recent_txns),
            "p_value_threshold": p_value_threshold,
            "drift_share_threshold": drift_share_threshold,
            "drift_share": round(drift_share, 4),
            "dataset_drift_detected": overall_dataset_drift,
            "metrics": feature_drift_results,
        }

        # Save drift report to artifacts
        report_path = Path(settings.ARTIFACTS_DIR) / "drift_reports"
        report_path.mkdir(parents=True, exist_ok=True)
        report_file = report_path / f"drift_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(drift_report, f, indent=2)

        # Audit Log
        if overall_dataset_drift:
            audit = AuditLog(
                action="DATA_DRIFT_ALERT",
                resource_type="monitoring",
                resource_id=self.request.id,
                details=drift_report,
            )
            session.add(audit)
            session.commit()
            logger.warning(f"DATA DRIFT DETECTED: {drift_share * 100:.1f}% features drifted!")

        return drift_report
    finally:
        session.close()

