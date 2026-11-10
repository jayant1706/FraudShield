"""
FraudShield Data Ingestion and Validation Module.
Handles loading, schema validation, anomaly checking, and synthetic benchmark generation.
"""

from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS: List[str] = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]


@dataclass
class ValidationReport:
    total_records: int
    total_columns: int
    missing_values: Dict[str, int]
    duplicate_records: int
    invalid_class_values: int
    negative_amounts: int
    class_distribution: Dict[int, int]
    fraud_percentage: float
    is_valid: bool
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records,
            "total_columns": self.total_columns,
            "missing_values_count": sum(self.missing_values.values()),
            "duplicate_records": self.duplicate_records,
            "invalid_class_values": self.invalid_class_values,
            "negative_amounts": self.negative_amounts,
            "class_distribution": self.class_distribution,
            "fraud_percentage": round(self.fraud_percentage, 4),
            "is_valid": self.is_valid,
            "warnings": self.warnings,
        }


class DataIngestionService:
    """Manages dataset ingestion, schema validation, and synthetic benchmark generation."""

    def __init__(self, raw_data_path: Optional[Path] = None):
        self.raw_data_path = raw_data_path or Path("ml/data/raw/creditcard.csv")

    def load_dataset(self, file_path: Optional[Path] = None) -> pd.DataFrame:
        """Loads transaction dataset from CSV file."""
        target_path = file_path or self.raw_data_path
        if not target_path.exists():
            logger.warning("Dataset not found at %s. Generating realistic benchmark dataset...", target_path)
            self.generate_benchmark_dataset(target_path)

        logger.info("Loading dataset from %s", target_path)
        df = pd.read_csv(target_path)
        return df

    def validate_schema(self, df: pd.DataFrame) -> ValidationReport:
        """
        Validates column names, data types, nulls, duplicates, and out-of-range values.
        """
        warnings: List[str] = []
        missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns in dataset: {missing_cols}")

        extra_cols = set(df.columns) - set(EXPECTED_COLUMNS)
        if extra_cols:
            warnings.append(f"Extra columns detected: {extra_cols}")

        missing_values = df.isnull().sum().to_dict()
        duplicate_records = int(df.duplicated().sum())
        if duplicate_records > 0:
            warnings.append(f"Detected {duplicate_records} duplicate records in dataset.")

        invalid_classes = int((~df["Class"].isin([0, 1])).sum())
        if invalid_classes > 0:
            warnings.append(f"Detected {invalid_classes} records with invalid Class label.")

        negative_amounts = int((df["Amount"] < 0).sum())
        if negative_amounts > 0:
            warnings.append(f"Detected {negative_amounts} records with negative Amount.")

        class_dist = df["Class"].value_counts().to_dict()
        total_records = len(df)
        fraud_count = class_dist.get(1, 0)
        fraud_pct = (fraud_count / total_records * 100) if total_records > 0 else 0.0

        is_valid = (
            len(missing_cols) == 0
            and invalid_classes == 0
            and negative_amounts == 0
            and total_records > 0
        )

        report = ValidationReport(
            total_records=total_records,
            total_columns=len(df.columns),
            missing_values=missing_values,
            duplicate_records=duplicate_records,
            invalid_class_values=invalid_classes,
            negative_amounts=negative_amounts,
            class_distribution=class_dist,
            fraud_percentage=fraud_pct,
            is_valid=is_valid,
            warnings=warnings,
        )
        return report

    def generate_benchmark_dataset(
        self,
        output_path: Path,
        n_samples: int = 100_000,
        fraud_rate: float = 0.00172,
        random_state: int = 42,
    ) -> pd.DataFrame:
        """
        Generates realistic synthetic credit card transaction benchmark matching Kaggle distributions.
        - Time: 0 to 172,800 seconds (48 hours)
        - V1 - V28: Gaussian PCA components with fraud signature deviations on key features (V14, V12, V10, V4)
        - Amount: Log-normal distribution
        - Class: 0 (Legitimate), 1 (Fraudulent)
        """
        logger.info("Synthesizing realistic benchmark dataset with %d records (fraud_rate=%.4f)...", n_samples, fraud_rate)
        rng = np.random.default_rng(random_state)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        n_fraud = int(n_samples * fraud_rate)
        n_legit = n_samples - n_fraud

        # 1. Time: uniformly distributed over 48 hours (172800 seconds)
        time_legit = np.sort(rng.uniform(0, 172800, size=n_legit))
        time_fraud = np.sort(rng.uniform(0, 172800, size=n_fraud))

        # 2. V1 to V28: PCA features
        # In Kaggle dataset, V14, V12, V10, V17 are heavily negatively correlated with fraud,
        # while V4, V11 are positively correlated with fraud.
        v_legit = rng.normal(0, 1.0, size=(n_legit, 28))
        v_fraud = rng.normal(0, 1.2, size=(n_fraud, 28))

        # Inject realistic fraud signatures
        # V14 index 13, V12 index 11, V10 index 9, V4 index 3, V11 index 10
        v_fraud[:, 13] -= rng.normal(6.5, 1.5, size=n_fraud)  # V14
        v_fraud[:, 11] -= rng.normal(5.0, 1.2, size=n_fraud)  # V12
        v_fraud[:, 9] -= rng.normal(4.8, 1.2, size=n_fraud)   # V10
        v_fraud[:, 3] += rng.normal(4.2, 1.3, size=n_fraud)   # V4
        v_fraud[:, 10] += rng.normal(3.8, 1.2, size=n_fraud)  # V11
        v_fraud[:, 16] -= rng.normal(5.2, 1.4, size=n_fraud)  # V17

        # 3. Amount: log-normal distribution
        # Fraud amounts are often concentrated around typical stolen card test or ticket amounts
        amount_legit = np.round(rng.lognormal(mean=2.8, sigma=1.4, size=n_legit), 2)
        amount_fraud = np.round(rng.lognormal(mean=3.5, sigma=1.8, size=n_fraud), 2)

        data_legit = np.column_stack([time_legit, v_legit, amount_legit, np.zeros(n_legit, dtype=int)])
        data_fraud = np.column_stack([time_fraud, v_fraud, amount_fraud, np.ones(n_fraud, dtype=int)])

        combined = np.vstack([data_legit, data_fraud])
        # Shuffle records to interleave
        shuffle_idx = rng.permutation(len(combined))
        combined = combined[shuffle_idx]

        df = pd.DataFrame(combined, columns=EXPECTED_COLUMNS)
        df["Class"] = df["Class"].astype(int)
        df["Time"] = df["Time"].astype(float)
        df["Amount"] = df["Amount"].astype(float)

        df.to_csv(output_path, index=False)
        logger.info("Successfully saved benchmark dataset to %s (%d records, %d frauds)", output_path, len(df), n_fraud)
        return df


if __name__ == "__main__":
    service = DataIngestionService()
    dataset = service.load_dataset()
    report = service.validate_schema(dataset)
    print(json.dumps(report.to_dict(), indent=2))

