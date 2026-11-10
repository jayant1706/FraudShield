"""
FraudShield Model Evaluation CLI.
Loads persisted artifacts and performs evaluation audits on test datasets.
"""

from pathlib import Path
import sys
import json
import logging
import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.src.evaluation.metrics import ModelEvaluator
from ml.src.features.preprocessor import FraudDataPreprocessor

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FraudShield.ModelAudit")


def evaluate_persisted_model(
    artifacts_dir: Path = Path("ml/artifacts"),
    test_data_path: Path = Path("ml/data/raw/creditcard.csv"),
) -> None:
    """Loads artifacts and prints full evaluation metrics."""
    model_path = artifacts_dir / "model.joblib"
    prep_path = artifacts_dir / "preprocessor.joblib"
    meta_path = artifacts_dir / "metadata.json"

    if not (model_path.exists() and prep_path.exists()):
        raise FileNotFoundError(f"Missing artifacts in {artifacts_dir}. Run training pipeline first.")

    logger.info("Loading preprocessor and champion model from %s...", artifacts_dir)
    preprocessor = FraudDataPreprocessor.load(prep_path)
    model = joblib.load(model_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    logger.info("Loaded Model: %s (Version: %s)", meta["model_name"], meta["version"])
    df = pd.read_csv(test_data_path)
    X = preprocessor.transform(df)
    y = df["Class"]

    probs = model.predict_proba(X)[:, 1]
    metrics = ModelEvaluator.evaluate(
        y, probs, model_name=meta["model_name"], dataset_split="Audit", threshold=meta["optimal_threshold"]
    )

    print("\n" + "=" * 60)
    print("FRAUDSHIELD MODEL AUDIT REPORT")
    print("=" * 60)
    print(f"Model: {metrics.model_name} (Version: {meta['version']})")
    print(f"Total Evaluated Records: {len(df):,}")
    print(f"PR-AUC (Primary Metric): {metrics.pr_auc:.4f}")
    print(f"ROC-AUC:                 {metrics.roc_auc:.4f}")
    print(f"Precision:               {metrics.precision:.4f}")
    print(f"Recall:                  {metrics.recall:.4f}")
    print(f"F1-Score:                {metrics.f1:.4f}")
    print(f"Decision Threshold:      {metrics.threshold_used:.4f}")
    print("-" * 60)
    print("Confusion Matrix:")
    print(f"  True Positives  (Fraud Caught):  {metrics.true_positives:,}")
    print(f"  False Positives (False Alarms):  {metrics.false_positives:,}")
    print(f"  True Negatives  (Legit Clear):   {metrics.true_negatives:,}")
    print(f"  False Negatives (Fraud Missed):  {metrics.false_negatives:,}")
    print(f"False Positive Rate: {metrics.false_positive_rate:.5f}")
    print(f"False Negative Rate: {metrics.false_negative_rate:.5f}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    evaluate_persisted_model()

