"""
FraudShield Exploratory Data Analysis (EDA) Module.
Computes class distribution, fraud vs legitimate transaction dynamics, amount profiles,
correlation structures, and outlier proportions.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FraudDataEDA:
    """Performs rigorous exploratory data analysis on credit card transactions."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def perform_full_eda(self) -> Dict[str, Any]:
        """Computes statistical EDA metrics."""
        total_txns = len(self.df)
        counts = self.df["Class"].value_counts().to_dict()
        n_legit = counts.get(0, 0)
        n_fraud = counts.get(1, 0)
        fraud_rate_pct = (n_fraud / total_txns * 100) if total_txns > 0 else 0.0

        legit_amounts = self.df[self.df["Class"] == 0]["Amount"]
        fraud_amounts = self.df[self.df["Class"] == 1]["Amount"]

        # Transaction amount statistics
        amount_stats = {
            "legitimate": {
                "mean": round(float(legit_amounts.mean()), 2),
                "std": round(float(legit_amounts.std()), 2),
                "median": round(float(legit_amounts.median()), 2),
                "q25": round(float(legit_amounts.quantile(0.25)), 2),
                "q75": round(float(legit_amounts.quantile(0.75)), 2),
                "max": round(float(legit_amounts.max()), 2),
            },
            "fraudulent": {
                "mean": round(float(fraud_amounts.mean()), 2) if len(fraud_amounts) > 0 else 0.0,
                "std": round(float(fraud_amounts.std()), 2) if len(fraud_amounts) > 0 else 0.0,
                "median": round(float(fraud_amounts.median()), 2) if len(fraud_amounts) > 0 else 0.0,
                "q25": round(float(fraud_amounts.quantile(0.25)), 2) if len(fraud_amounts) > 0 else 0.0,
                "q75": round(float(fraud_amounts.quantile(0.75)), 2) if len(fraud_amounts) > 0 else 0.0,
                "max": round(float(fraud_amounts.max()), 2) if len(fraud_amounts) > 0 else 0.0,
            },
        }

        # Target correlations
        corr = self.df.corr()["Class"].drop("Class").to_dict()
        top_positive_corr = sorted([(k, v) for k, v in corr.items() if v > 0], key=lambda x: x[1], reverse=True)[:5]
        top_negative_corr = sorted([(k, v) for k, v in corr.items() if v < 0], key=lambda x: x[1])[:5]

        # Outlier counts via IQR on Amount
        q1 = legit_amounts.quantile(0.25)
        q3 = legit_amounts.quantile(0.75)
        iqr = q3 - q1
        outlier_upper_bound = q3 + 1.5 * iqr
        amount_outliers_count = int((self.df["Amount"] > outlier_upper_bound).sum())

        return {
            "class_distribution": {
                "total_records": total_txns,
                "legitimate_count": n_legit,
                "fraudulent_count": n_fraud,
                "fraud_percentage": round(fraud_rate_pct, 4),
                "class_ratio": f"1:{round(n_legit / max(n_fraud, 1), 1)}",
            },
            "amount_analysis": amount_stats,
            "correlation_analysis": {
                "top_positive_correlated_features": [{"feature": k, "correlation": round(float(v), 4)} for k, v in top_positive_corr],
                "top_negative_correlated_features": [{"feature": k, "correlation": round(float(v), 4)} for k, v in top_negative_corr],
            },
            "outlier_analysis": {
                "amount_iqr_upper_bound": round(float(outlier_upper_bound), 2),
                "amount_outliers_count": amount_outliers_count,
                "amount_outliers_percentage": round(amount_outliers_count / total_txns * 100, 2),
            },
        }

    def save_eda_summary(self, filepath: Path) -> Path:
        """Saves EDA findings to JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        eda_data = self.perform_full_eda()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(eda_data, f, indent=2)
        logger.info("Saved EDA summary report to %s", filepath)
        return filepath

