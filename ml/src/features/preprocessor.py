"""
FraudShield Feature Preprocessing and Transformation Pipeline.
Implements leak-free scaling, stratified partitioning, and serialization.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler, StandardScaler

logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [f"V{i}" for i in range(1, 29)] + ["scaled_amount", "scaled_time"]


@dataclass
class ProcessedSplits:
    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series


class FraudDataPreprocessor:
    """
    Transforms raw transaction data into standardized feature matrices.
    Applies RobustScaler to 'Amount' and 'Time' to handle heavy-tailed outliers gracefully.
    Guarantees no data leakage by fitting exclusively on the training partition.
    """

    def __init__(self, use_robust_scaler: bool = True):
        self.use_robust_scaler = use_robust_scaler
        self.amount_scaler = RobustScaler() if use_robust_scaler else StandardScaler()
        self.time_scaler = RobustScaler() if use_robust_scaler else StandardScaler()
        self.is_fitted = False

    def fit(self, df: pd.DataFrame) -> "FraudDataPreprocessor":
        """Fits scalers on the training DataFrame."""
        logger.info("Fitting feature scalers on training split...")
        self.amount_scaler.fit(df[["Amount"]])
        self.time_scaler.fit(df[["Time"]])
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms DataFrame into the model-ready feature representation."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before calling transform.")

        df_copy = df.copy()
        df_copy["scaled_amount"] = self.amount_scaler.transform(df_copy[["Amount"]])
        df_copy["scaled_time"] = self.time_scaler.transform(df_copy[["Time"]])

        # Assemble features in exact canonical ordering
        v_cols = [f"V{i}" for i in range(1, 29)]
        ordered_cols = v_cols + ["scaled_amount", "scaled_time"]
        return df_copy[ordered_cols]

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fits scalers and transforms the training DataFrame."""
        return self.fit(df).transform(df)

    def prepare_stratified_splits(
        self,
        df: pd.DataFrame,
        test_size: float = 0.15,
        val_size: float = 0.15,
        random_state: int = 42,
    ) -> ProcessedSplits:
        """
        Creates leak-free, stratified train/validation/test partitions.
        Scalers are fitted strictly on train data and applied to val and test.
        """
        logger.info(
            "Creating stratified splits (test=%.2f, val=%.2f, seed=%d)...",
            test_size,
            val_size,
            random_state,
        )

        y = df["Class"]
        X_raw = df.drop(columns=["Class"])

        # Split train+val vs test
        X_train_val, X_test_raw, y_train_val, y_test = train_test_split(
            X_raw, y, test_size=test_size, stratify=y, random_state=random_state
        )

        # Split train vs val
        relative_val_size = val_size / (1.0 - test_size)
        X_train_raw, X_val_raw, y_train, y_val = train_test_split(
            X_train_val,
            y_train_val,
            test_size=relative_val_size,
            stratify=y_train_val,
            random_state=random_state,
        )

        # Fit exclusively on training data
        self.fit(X_train_raw)

        # Transform each partition
        X_train = self.transform(X_train_raw)
        X_val = self.transform(X_val_raw)
        X_test = self.transform(X_test_raw)

        logger.info(
            "Split counts -> Train: %d (Frauds: %d), Val: %d (Frauds: %d), Test: %d (Frauds: %d)",
            len(X_train), int(y_train.sum()),
            len(X_val), int(y_val.sum()),
            len(X_test), int(y_test.sum()),
        )

        return ProcessedSplits(
            X_train=X_train,
            X_val=X_val,
            X_test=X_test,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
        )

    def save(self, filepath: Path) -> Path:
        """Serializes the fitted preprocessor."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, filepath)
        logger.info("Saved preprocessor artifact to %s", filepath)
        return filepath

    @classmethod
    def load(cls, filepath: Path) -> "FraudDataPreprocessor":
        """Loads a preprocessor instance from disk."""
        if not filepath.exists():
            raise FileNotFoundError(f"Preprocessor file not found at {filepath}")
        return joblib.load(filepath)

