"""
FraudShield Data Quality and Profiling Module.
Generates comprehensive statistical profiles, distribution checks, and data quality audits.
"""

from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ColumnQualityProfile:
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max_val: Optional[float] = None
    skewness: Optional[float] = None


class DataQualityAuditor:
    """Performs rigorous statistical profiling and data quality checks on transaction datasets."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run_full_audit(self) -> Dict[str, Any]:
        """Runs complete profiling audit and returns structured metrics."""
        total_rows = len(self.df)
        profiles: List[Dict[str, Any]] = []

        for col in self.df.columns:
            series = self.df[col]
            nulls = int(series.isnull().sum())
            null_pct = float(nulls / total_rows * 100) if total_rows > 0 else 0.0
            unique_cnt = int(series.nunique())

            profile_dict: Dict[str, Any] = {
                "name": col,
                "dtype": str(series.dtype),
                "null_count": nulls,
                "null_percentage": round(null_pct, 4),
                "unique_count": unique_cnt,
            }

            if pd.api.types.is_numeric_dtype(series):
                clean_s = series.dropna()
                profile_dict.update({
                    "mean": round(float(clean_s.mean()), 4),
                    "std": round(float(clean_s.std()), 4),
                    "min": round(float(clean_s.min()), 4),
                    "q25": round(float(clean_s.quantile(0.25)), 4),
                    "median": round(float(clean_s.median()), 4),
                    "q75": round(float(clean_s.quantile(0.75)), 4),
                    "max": round(float(clean_s.max()), 4),
                    "skewness": round(float(clean_s.skew()), 4),
                })
            profiles.append(profile_dict)

        # Correlation with target
        correlations: Dict[str, float] = {}
        if "Class" in self.df.columns:
            corr_series = self.df.corr()["Class"].drop("Class")
            correlations = {
                k: round(float(v), 4) for k, v in corr_series.sort_values(ascending=False).to_dict().items()
            }

        # Class imbalance metrics
        class_metrics = {}
        if "Class" in self.df.columns:
            counts = self.df["Class"].value_counts().to_dict()
            class_metrics = {
                "legitimate_count": counts.get(0, 0),
                "fraudulent_count": counts.get(1, 0),
                "fraud_ratio_percentage": round(counts.get(1, 0) / total_rows * 100, 4) if total_rows > 0 else 0.0,
                "imbalance_ratio": f"1:{round(counts.get(0, 0) / max(counts.get(1, 0), 1), 1)}",
            }

        return {
            "dataset_summary": {
                "total_rows": total_rows,
                "total_columns": len(self.df.columns),
                "duplicate_rows": int(self.df.duplicated().sum()),
                "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
            },
            "class_metrics": class_metrics,
            "target_correlations": correlations,
            "column_profiles": profiles,
        }

    def save_audit_report(self, output_path: Path) -> Path:
        """Saves audit results to JSON artifact."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = self.run_full_audit()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Saved data quality audit report to %s", output_path)
        return output_path

