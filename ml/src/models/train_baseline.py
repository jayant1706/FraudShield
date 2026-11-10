"""
FraudShield Baseline Model Training Module.
Trains and optimizes Logistic Regression and Random Forest models on stratified training data.
"""

import logging
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


class BaselineModelTrainer:
    """Trains linear and ensemble bagging baselines with class imbalance handling."""

    @staticmethod
    def train_logistic_regression(
        X_train: pd.DataFrame,
        y_train: pd.Series,
        random_state: int = 42,
    ) -> LogisticRegression:
        """
        Trains Logistic Regression using balanced class weights to penalize fraud misclassification.
        """
        logger.info("Training Logistic Regression baseline (class_weight='balanced')...")
        model = LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=1.0,
            solver="lbfgs",
            random_state=random_state,
        )
        model.fit(X_train, y_train)
        return model

    @staticmethod
    def train_random_forest(
        X_train: pd.DataFrame,
        y_train: pd.Series,
        n_estimators: int = 100,
        max_depth: int = 10,
        random_state: int = 42,
    ) -> RandomForestClassifier:
        """
        Trains Random Forest with balanced sub-sample class weighting.
        """
        logger.info(
            "Training Random Forest baseline (trees=%d, max_depth=%d)...",
            n_estimators,
            max_depth,
        )
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        )
        model.fit(X_train, y_train)
        return model

