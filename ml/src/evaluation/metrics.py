"""
FraudShield Model Evaluation and Metrics Suite.
Calculates PR-AUC, ROC-AUC, F1, Recall, Precision, FPR, FNR, and Confusion Matrix.
Includes cost-sensitive threshold optimization for imbalanced fraud distributions.
"""

from dataclasses import dataclass
import json
import logging
from typing import Any, Dict, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logger = logging.getLogger(__name__)


@dataclass
class EvaluationMetrics:
    model_name: str
    dataset_split: str
    pr_auc: float
    roc_auc: float
    precision: float
    recall: float
    f1: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    false_positive_rate: float
    false_negative_rate: float
    optimal_threshold: float
    threshold_used: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "dataset_split": self.dataset_split,
            "pr_auc": round(self.pr_auc, 4),
            "roc_auc": round(self.roc_auc, 4),
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "confusion_matrix": {
                "tp": self.true_positives,
                "fp": self.false_positives,
                "tn": self.true_negatives,
                "fn": self.false_negatives,
            },
            "rates": {
                "false_positive_rate": round(self.false_positive_rate, 5),
                "false_negative_rate": round(self.false_negative_rate, 5),
            },
            "threshold": {
                "optimal": round(self.optimal_threshold, 4),
                "evaluated": round(self.threshold_used, 4),
            },
        }


class ModelEvaluator:
    """Computes comprehensive evaluation metrics tailored for extreme class imbalance."""

    @staticmethod
    def find_optimal_threshold_f1(y_true: np.ndarray, y_probs: np.ndarray) -> float:
        """Finds decision threshold that maximizes F1 score on validation set."""
        precisions, recalls, thresholds = precision_recall_curve(y_true, y_probs)
        # Avoid division by zero
        f1_scores = np.where(
            (precisions + recalls) > 0,
            2 * (precisions * recalls) / (precisions + recalls),
            0.0,
        )
        # thresholds is 1 element shorter than precision/recall
        if len(thresholds) == 0:
            return 0.5
        best_idx = np.argmax(f1_scores[: len(thresholds)])
        best_threshold = float(thresholds[best_idx])
        return min(max(best_threshold, 0.05), 0.95)

    @staticmethod
    def evaluate(
        y_true: np.ndarray,
        y_probs: np.ndarray,
        model_name: str = "CandidateModel",
        dataset_split: str = "Validation",
        threshold: Optional[float] = None,
    ) -> EvaluationMetrics:
        """
        Calculates all key imbalanced classification metrics.
        If threshold is None, optimal F1 threshold is computed and used.
        """
        y_true_arr = np.asarray(y_true).astype(int)
        y_probs_arr = np.asarray(y_probs).astype(float)

        # PR-AUC (Average Precision) and ROC-AUC
        pr_auc = float(average_precision_score(y_true_arr, y_probs_arr))
        try:
            roc_auc = float(roc_auc_score(y_true_arr, y_probs_arr))
        except ValueError:
            roc_auc = 0.5

        optimal_thresh = ModelEvaluator.find_optimal_threshold_f1(y_true_arr, y_probs_arr)
        eval_thresh = threshold if threshold is not None else optimal_thresh

        y_pred = (y_probs_arr >= eval_thresh).astype(int)

        prec = float(precision_score(y_true_arr, y_pred, zero_division=0))
        rec = float(recall_score(y_true_arr, y_pred, zero_division=0))
        f1 = float(f1_score(y_true_arr, y_pred, zero_division=0))

        tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred, labels=[0, 1]).ravel()

        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        return EvaluationMetrics(
            model_name=model_name,
            dataset_split=dataset_split,
            pr_auc=pr_auc,
            roc_auc=roc_auc,
            precision=prec,
            recall=rec,
            f1=f1,
            true_positives=int(tp),
            false_positives=int(fp),
            true_negatives=int(tn),
            false_negatives=int(fn),
            false_positive_rate=fpr,
            false_negative_rate=fnr,
            optimal_threshold=optimal_thresh,
            threshold_used=eval_thresh,
        )

