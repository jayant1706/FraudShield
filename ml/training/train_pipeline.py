"""
FraudShield End-to-End Machine Learning Training Pipeline.
Orchestrates data ingestion, quality audits, leak-free preprocessing, multi-model training,
PR-AUC benchmarking, SHAP explainer calibration, and artifact persistence.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
from typing import Dict, Any

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import joblib
import numpy as np
import pandas as pd

from ml.src.data.ingestion import DataIngestionService
from ml.src.data.quality import DataQualityAuditor
from ml.src.evaluation.comparator import ModelComparator
from ml.src.evaluation.metrics import ModelEvaluator
from ml.src.explainability.shap_explainer import FraudSHAPExplainer
from ml.src.features.preprocessor import FraudDataPreprocessor
from ml.src.models.train_baseline import BaselineModelTrainer
from ml.src.models.train_isolation_forest import IsolationForestAnomalyDetector
from ml.src.models.train_xgboost import XGBoostModelTrainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FraudShield.TrainPipeline")

ARTIFACTS_DIR = Path("ml/artifacts")


def run_training_pipeline(
    raw_data_path: Path = Path("ml/data/raw/creditcard.csv"),
    output_dir: Path = ARTIFACTS_DIR,
    model_version: str = "v1.0.0",
) -> Dict[str, Any]:
    """Executes complete ML training and benchmarking workflow."""
    start_time = datetime.now(timezone.utc)
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Starting FraudShield ML Pipeline (Version: %s)...", model_version)

    # 1. Ingestion & Validation
    ingestion_service = DataIngestionService(raw_data_path)
    df = ingestion_service.load_dataset()
    val_report = ingestion_service.validate_schema(df)
    logger.info("Data Validation: %s (%d records, %d frauds)", 
                "PASSED" if val_report.is_valid else "FAILED", 
                val_report.total_records, 
                val_report.class_distribution.get(1, 0))

    # 2. Data Quality Audit
    auditor = DataQualityAuditor(df)
    quality_report_path = output_dir / "data_quality_report.json"
    auditor.save_audit_report(quality_report_path)

    # 3. Stratified Partitioning & Preprocessing
    preprocessor = FraudDataPreprocessor(use_robust_scaler=True)
    splits = preprocessor.prepare_stratified_splits(df, test_size=0.15, val_size=0.15, random_state=42)
    preprocessor_path = output_dir / "preprocessor.joblib"
    preprocessor.save(preprocessor_path)

    # 4. Multi-Model Training & Validation Benchmarking
    comparator = ModelComparator()

    # A. Logistic Regression
    logger.info("--- Training Candidate 1: Logistic Regression ---")
    lr_model = BaselineModelTrainer.train_logistic_regression(splits.X_train, splits.y_train)
    lr_val_probs = lr_model.predict_proba(splits.X_val)[:, 1]
    lr_metrics = ModelEvaluator.evaluate(
        splits.y_val, lr_val_probs, model_name="LogisticRegression", dataset_split="Validation"
    )
    comparator.add_validation_result(lr_metrics)
    logger.info("Logistic Regression -> Val PR-AUC: %.4f | F1: %.4f | Recall: %.4f", lr_metrics.pr_auc, lr_metrics.f1, lr_metrics.recall)

    # B. Random Forest
    logger.info("--- Training Candidate 2: Random Forest ---")
    rf_model = BaselineModelTrainer.train_random_forest(splits.X_train, splits.y_train, n_estimators=100, max_depth=10)
    rf_val_probs = rf_model.predict_proba(splits.X_val)[:, 1]
    rf_metrics = ModelEvaluator.evaluate(
        splits.y_val, rf_val_probs, model_name="RandomForest", dataset_split="Validation"
    )
    comparator.add_validation_result(rf_metrics)
    logger.info("Random Forest -> Val PR-AUC: %.4f | F1: %.4f | Recall: %.4f", rf_metrics.pr_auc, rf_metrics.f1, rf_metrics.recall)

    # C. XGBoost
    logger.info("--- Training Candidate 3: XGBoost Classifier ---")
    xgb_model = XGBoostModelTrainer.train(
        splits.X_train, splits.y_train, X_val=splits.X_val, y_val=splits.y_val, n_estimators=150, max_depth=5, learning_rate=0.08
    )
    xgb_val_probs = xgb_model.predict_proba(splits.X_val)[:, 1]
    xgb_metrics = ModelEvaluator.evaluate(
        splits.y_val, xgb_val_probs, model_name="XGBoost", dataset_split="Validation"
    )
    comparator.add_validation_result(xgb_metrics)
    logger.info("XGBoost -> Val PR-AUC: %.4f | F1: %.4f | Recall: %.4f", xgb_metrics.pr_auc, xgb_metrics.f1, xgb_metrics.recall)

    # D. Isolation Forest (Complementary Anomaly Detector)
    logger.info("--- Fitting Complementary Anomaly Detector: Isolation Forest ---")
    iso_forest = IsolationForestAnomalyDetector(contamination=0.002, random_state=42)
    iso_forest.fit(splits.X_train)
    iso_scores = iso_forest.predict_anomaly_score(splits.X_val)
    iso_metrics = ModelEvaluator.evaluate(
        splits.y_val, iso_scores, model_name="IsolationForest_Anomaly", dataset_split="Validation"
    )
    logger.info("Isolation Forest -> Val PR-AUC: %.4f | F1: %.4f", iso_metrics.pr_auc, iso_metrics.f1)

    # 5. Champion Selection & Holdout Test Evaluation
    champion_eval = comparator.select_champion()
    model_map = {
        "LogisticRegression": lr_model,
        "RandomForest": rf_model,
        "XGBoost": xgb_model,
    }
    champion_model = model_map[champion_eval.model_name]

    # Evaluate champion once on holdout test set
    test_probs = champion_model.predict_proba(splits.X_test)[:, 1]
    test_metrics = ModelEvaluator.evaluate(
        splits.y_test,
        test_probs,
        model_name=champion_eval.model_name,
        dataset_split="Holdout_Test",
        threshold=champion_eval.optimal_threshold,
    )
    logger.info(
        "Champion (%s) Holdout Test Performance -> PR-AUC: %.4f | ROC-AUC: %.4f | F1: %.4f | Recall: %.4f | Precision: %.4f",
        champion_eval.model_name,
        test_metrics.pr_auc,
        test_metrics.roc_auc,
        test_metrics.f1,
        test_metrics.recall,
        test_metrics.precision,
    )

    # 6. Save Comparison Summary
    summary_path = output_dir / "evaluation_summary.json"
    comparator.save_summary(summary_path, test_metrics=test_metrics)

    # 7. Configure & Save SHAP Explainer
    logger.info("Configuring SHAP Explainer with representative background sample...")
    # Use 100 random samples from training set as background distribution
    bg_sample = splits.X_train.sample(n=min(100, len(splits.X_train)), random_state=42)
    shap_explainer = FraudSHAPExplainer(champion_model, background_sample=bg_sample)
    explainer_path = output_dir / "shap_explainer.joblib"
    shap_explainer.save(explainer_path)

    # 8. Persist Champion Model Artifacts & Metadata
    model_artifact_path = output_dir / "model.joblib"
    joblib.dump(champion_model, model_artifact_path)
    logger.info("Saved Champion model to %s", model_artifact_path)

    # Save Isolation Forest artifact
    joblib.dump(iso_forest, output_dir / "isolation_forest.joblib")

    # Save Feature schema & metadata
    feature_names = list(splits.X_train.columns)
    metadata = {
        "version": model_version,
        "model_name": champion_eval.model_name,
        "artifact_file": "model.joblib",
        "preprocessor_file": "preprocessor.joblib",
        "explainer_file": "shap_explainer.joblib",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "input_features": feature_names,
        "num_features": len(feature_names),
        "validation_metrics": champion_eval.to_dict(),
        "test_metrics": test_metrics.to_dict(),
        "optimal_threshold": champion_eval.optimal_threshold,
        "comparison_table": comparator.generate_comparison_table().to_dict(orient="records"),
        "dataset_info": {
            "total_records": len(df),
            "train_records": len(splits.X_train),
            "val_records": len(splits.X_val),
            "test_records": len(splits.X_test),
            "fraud_count": int(df["Class"].sum()),
        },
    }

    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved model metadata to %s", metadata_path)

    total_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info("FraudShield ML Pipeline finished successfully in %.2f seconds.", total_duration)

    return metadata


if __name__ == "__main__":
    run_training_pipeline()

