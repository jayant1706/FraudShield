"""
FraudShield Isolation Forest Anomaly Detection Model.
Complementary unsupervised anomaly detector scoring out-of-distribution transactions.
"""

import logging
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)


class IsolationForestAnomalyDetector:
    """Unsupervised anomaly detector for spotting emerging fraud patterns."""

    def __init__(self, contamination: float = 0.002, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )

    def fit(self, X_train: pd.DataFrame) -> "IsolationForestAnomalyDetector":
        """Fits Isolation Forest on training transactions."""
        logger.info("Fitting Isolation Forest (contamination=%.4f)...", self.contamination)
        self.model.fit(X_train)
        return self

    def predict_anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """
        Computes anomaly score normalized between [0, 1] where 1.0 = highest anomaly.
        Decision function outputs negative values for anomalies, positive for normal.
        """
        raw_scores = self.model.decision_function(X)
        # Normalize: lower raw_score means more anomalous -> invert so higher = higher anomaly
        # Typically raw_score ranges [-0.5, 0.5]
        clipped = np.clip(raw_scores, -0.4, 0.4)
        normalized = (0.4 - clipped) / 0.8  # Inverted into [0, 1]
        return normalized

