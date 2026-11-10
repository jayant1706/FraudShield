"""
Unit Tests for FraudShield Machine Learning Pipeline.
Tests data ingestion, schema validation, preprocessing, evaluation metrics, and SHAP explainability.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from ml.src.data.ingestion import DataIngestionService, EXPECTED_COLUMNS
from ml.src.data.quality import DataQualityAuditor
from ml.src.features.preprocessor import FraudDataPreprocessor, FEATURE_COLUMNS
from ml.src.evaluation.metrics import ModelEvaluator
from ml.src.evaluation.comparator import ModelComparator
from ml.src.explainability.shap_explainer import FraudSHAPExplainer
from ml.src.models.train_baseline import BaselineModelTrainer


@pytest.fixture
def sample_raw_dataframe() -> pd.DataFrame:
    """Creates a deterministic synthetic test DataFrame."""
    rng = np.random.default_rng(42)
    n_samples = 500
    n_fraud = 10
    n_legit = n_samples - n_fraud

    time = rng.uniform(0, 172800, size=n_samples)
    v_data = rng.normal(0, 1, size=(n_samples, 28))
    # inject signal
    v_data[:n_fraud, 13] -= 5.0  # V14
    amount = rng.lognormal(2.5, 1.0, size=n_samples)
    labels = np.array([1] * n_fraud + [0] * n_legit)

    data = np.column_stack([time, v_data, amount, labels])
    df = pd.DataFrame(data, columns=EXPECTED_COLUMNS)
    df["Class"] = df["Class"].astype(int)
    return df


def test_data_ingestion_and_validation(sample_raw_dataframe, tmp_path):
    csv_path = tmp_path / "test_creditcard.csv"
    sample_raw_dataframe.to_csv(csv_path, index=False)

    service = DataIngestionService(csv_path)
    df = service.load_dataset()
    report = service.validate_schema(df)

    assert report.is_valid is True
    assert report.total_records == 500
    assert report.total_columns == 31
    assert report.invalid_class_values == 0
    assert report.negative_amounts == 0
    assert report.class_distribution[1] == 10
    assert report.class_distribution[0] == 490


def test_data_quality_auditor(sample_raw_dataframe, tmp_path):
    auditor = DataQualityAuditor(sample_raw_dataframe)
    report = auditor.run_full_audit()

    assert report["dataset_summary"]["total_rows"] == 500
    assert report["class_metrics"]["fraudulent_count"] == 10
    assert report["class_metrics"]["legitimate_count"] == 490
    assert "V14" in report["target_correlations"]
    assert len(report["column_profiles"]) == 31


def test_preprocessor_pipeline(sample_raw_dataframe):
    preprocessor = FraudDataPreprocessor(use_robust_scaler=True)
    splits = preprocessor.prepare_stratified_splits(
        sample_raw_dataframe, test_size=0.2, val_size=0.2, random_state=42
    )

    assert list(splits.X_train.columns) == FEATURE_COLUMNS
    assert len(splits.X_train) == 300
    assert len(splits.X_val) == 100
    assert len(splits.X_test) == 100
    # Stratification check
    assert splits.y_train.sum() > 0
    assert splits.y_val.sum() > 0
    assert splits.y_test.sum() > 0

    # Ensure no NaN values
    assert not splits.X_train.isnull().any().any()
    assert not splits.X_val.isnull().any().any()
    assert not splits.X_test.isnull().any().any()


def test_model_evaluator_metrics():
    y_true = np.array([0, 0, 0, 0, 1, 1, 0, 1, 0, 0])
    y_probs = np.array([0.1, 0.2, 0.05, 0.3, 0.85, 0.9, 0.2, 0.7, 0.15, 0.4])

    metrics = ModelEvaluator.evaluate(
        y_true, y_probs, model_name="TestModel", dataset_split="Validation", threshold=0.5
    )

    assert metrics.model_name == "TestModel"
    assert metrics.pr_auc > 0.8
    assert metrics.roc_auc > 0.8
    assert metrics.true_positives == 3
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.recall == 1.0
    assert metrics.precision == 1.0
    assert metrics.f1 == 1.0


def test_model_comparator():
    comparator = ModelComparator()
    y_true = np.array([0, 0, 1, 1])

    m1 = ModelEvaluator.evaluate(y_true, np.array([0.1, 0.2, 0.7, 0.8]), model_name="HighPRAUC")
    m2 = ModelEvaluator.evaluate(y_true, np.array([0.4, 0.5, 0.51, 0.52]), model_name="LowPRAUC")

    comparator.add_validation_result(m1)
    comparator.add_validation_result(m2)

    champion = comparator.select_champion()
    assert champion.model_name == "HighPRAUC"
    table = comparator.generate_comparison_table()
    assert len(table) == 2
    assert table.iloc[0]["Model"] == "HighPRAUC"


def test_shap_explainer(sample_raw_dataframe):
    preprocessor = FraudDataPreprocessor(use_robust_scaler=True)
    splits = preprocessor.prepare_stratified_splits(
        sample_raw_dataframe, test_size=0.2, val_size=0.2, random_state=42
    )

    model = BaselineModelTrainer.train_logistic_regression(splits.X_train, splits.y_train)
    explainer = FraudSHAPExplainer(model, background_sample=splits.X_train.iloc[:50])

    instance = splits.X_val.iloc[[0]]
    explanations = explainer.explain_instance(instance, top_k=5)

    assert len(explanations) == 5
    for exp in explanations:
        d = exp.to_dict()
        assert "feature" in d
        assert "value" in d
        assert "shap_value" in d
        assert "impact" in d

