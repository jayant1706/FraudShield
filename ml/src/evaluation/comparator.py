"""
FraudShield Model Benchmark Comparator.
Compares candidate models on validation split and evaluates the selected champion on holdout test data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from ml.src.evaluation.metrics import EvaluationMetrics, ModelEvaluator

logger = logging.getLogger(__name__)


class ModelComparator:
    """Ranks and compares models strictly using validation PR-AUC."""

    def __init__(self):
        self.validation_results: List[EvaluationMetrics] = []
        self.champion_result: Optional[EvaluationMetrics] = None

    def add_validation_result(self, result: EvaluationMetrics) -> None:
        self.validation_results.append(result)

    def select_champion(self) -> EvaluationMetrics:
        """
        Selects best model based on validation PR-AUC.
        Breaks ties by model expressiveness preference: XGBoost > RandomForest > LogisticRegression.
        """
        if not self.validation_results:
            raise ValueError("No model results registered for comparison.")

        model_priority = {"XGBoost": 3, "RandomForest": 2, "LogisticRegression": 1}
        # Sort descending by PR-AUC, then model priority, then F1
        sorted_results = sorted(
            self.validation_results,
            key=lambda x: (round(x.pr_auc, 4), model_priority.get(x.model_name, 0), round(x.f1, 4)),
            reverse=True,
        )
        champion = sorted_results[0]
        logger.info(
            "Selected Champion: %s (Validation PR-AUC: %.4f, F1: %.4f, Recall: %.4f)",
            champion.model_name,
            champion.pr_auc,
            champion.f1,
            champion.recall,
        )
        return champion

    def generate_comparison_table(self) -> pd.DataFrame:
        """Constructs a clean comparison DataFrame."""
        rows = [res.to_dict() for res in self.validation_results]
        flat_rows = []
        for r in rows:
            flat_rows.append({
                "Model": r["model_name"],
                "PR-AUC": r["pr_auc"],
                "ROC-AUC": r["roc_auc"],
                "F1-Score": r["f1"],
                "Recall": r["recall"],
                "Precision": r["precision"],
                "FPR": r["rates"]["false_positive_rate"],
                "FNR": r["rates"]["false_negative_rate"],
                "Threshold": r["threshold"]["evaluated"],
            })
        return pd.DataFrame(flat_rows).sort_values(by="PR-AUC", ascending=False)

    def save_summary(self, filepath: Path, test_metrics: Optional[EvaluationMetrics] = None) -> Path:
        """Saves comparison report and holdout test verification to JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        summary = {
            "validation_benchmarks": [r.to_dict() for r in self.validation_results],
            "champion_selection": self.select_champion().to_dict(),
            "holdout_test_metrics": test_metrics.to_dict() if test_metrics else None,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        logger.info("Saved comparison summary to %s", filepath)
        return filepath
