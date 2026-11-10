"""
FraudShield XGBoost Gradient Boosting Model Training Module.
Trains cost-sensitive, gradient-boosted decision trees optimized for PR-AUC.
"""

import logging
from typing import Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class XGBoostModelTrainer:
    """Trains tuned XGBoost classifier with scale_pos_weight optimization."""

    @staticmethod
    def train(
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        n_estimators: int = 150,
        max_depth: int = 5,
        learning_rate: float = 0.08,
        random_state: int = 42,
    ) -> Any:
        """
        Trains XGBoost Classifier with automated scale_pos_weight calculation.
        """
        try:
            from xgboost import XGBClassifier
        except ImportError:
            raise ImportError("xgboost package is required to train XGBoostModelTrainer.")

        n_neg = int((y_train == 0).sum())
        n_pos = int((y_train == 1).sum())
        scale_pos_weight = float(n_neg / max(n_pos, 1))

        logger.info(
            "Training XGBoost (trees=%d, depth=%d, lr=%.3f, scale_pos_weight=%.2f)...",
            n_estimators,
            max_depth,
            learning_rate,
            scale_pos_weight,
        )

        model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            scale_pos_weight=scale_pos_weight,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="aucpr",
            random_state=random_state,
            n_jobs=-1,
        )

        if X_val is not None and y_val is not None:
            model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
        else:
            model.fit(X_train, y_train, verbose=False)

        return model
