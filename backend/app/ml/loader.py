"""
FraudShield Model Loader and Real-Time Inference Engine.
Loads model artifacts at application startup and runs non-blocking inference on thread pools.
"""

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd

from backend.app.core.config import settings
from backend.app.core.exceptions import ModelInferenceError
from ml.src.explainability.shap_explainer import FraudSHAPExplainer
from ml.src.features.preprocessor import FraudDataPreprocessor

logger = logging.getLogger(__name__)


class ModelArtifactManager:
    """Manages hot-reloading and thread-safe inference for production ML artifacts."""

    def __init__(self, artifacts_dir: Path = settings.ARTIFACTS_DIR):
        self.artifacts_dir = artifacts_dir
        self.model: Optional[Any] = None
        self.preprocessor: Optional[FraudDataPreprocessor] = None
        self.explainer: Optional[FraudSHAPExplainer] = None
        self.metadata: Dict[str, Any] = {}
        self.is_loaded: bool = False
        self._lock = asyncio.Lock()

    def load_artifacts(self) -> None:
        """Loads serialized model, preprocessor, SHAP explainer, and metadata from disk."""
        model_path = self.artifacts_dir / "model.joblib"
        prep_path = self.artifacts_dir / "preprocessor.joblib"
        explainer_path = self.artifacts_dir / "shap_explainer.joblib"
        meta_path = self.artifacts_dir / "metadata.json"

        if not (model_path.exists() and prep_path.exists()):
            raise FileNotFoundError(
                f"Missing critical model artifacts in {self.artifacts_dir}. Run training pipeline first."
            )

        logger.info("Loading FraudShield ML artifacts from %s...", self.artifacts_dir)
        self.model = joblib.load(model_path)
        self.preprocessor = FraudDataPreprocessor.load(prep_path)

        if explainer_path.exists():
            try:
                self.explainer = FraudSHAPExplainer.load(explainer_path)
            except Exception as e:
                logger.warning("Could not load SHAP explainer artifact (%s). Initializing fresh instance.", e)
                self.explainer = FraudSHAPExplainer(self.model)
        else:
            self.explainer = FraudSHAPExplainer(self.model)

        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "version": settings.CHAMPION_MODEL_VERSION,
                "model_name": type(self.model).__name__,
                "optimal_threshold": 0.5,
                "input_features": [f"V{i}" for i in range(1, 29)] + ["scaled_amount", "scaled_time"],
            }

        self.is_loaded = True
        logger.info(
            "Successfully loaded Champion model: %s (Version: %s)",
            self.metadata.get("model_name"),
            self.metadata.get("version"),
        )

    def prepare_feature_dataframe(
        self,
        amount: float,
        transaction_time: Optional[datetime] = None,
        features_dict: Optional[Dict[str, float]] = None,
    ) -> pd.DataFrame:
        """Constructs a single-row DataFrame aligned with the model's feature schema."""
        t_time = transaction_time or datetime.now(timezone.utc)
        # Convert timestamp to seconds-of-day or epoch offset
        seconds_val = float((t_time.hour * 3600) + (t_time.minute * 60) + t_time.second)

        row_dict: Dict[str, float] = {"Time": seconds_val}
        # Populate V1 - V28 from input dictionary or use 0.0 default
        features_dict = features_dict or {}
        for i in range(1, 29):
            col_name = f"V{i}"
            row_dict[col_name] = float(features_dict.get(col_name, 0.0))

        row_dict["Amount"] = float(amount)
        df = pd.DataFrame([row_dict])
        return self.preprocessor.transform(df)

    def _sync_predict(
        self,
        transformed_df: pd.DataFrame,
    ) -> Tuple[float, int, List[Dict[str, Any]]]:
        """Synchronous CPU-bound inference and explanation execution."""
        if not self.is_loaded or self.model is None:
            raise ModelInferenceError("ML model is not loaded in memory.")

        # 1. Compute probability
        probs = self.model.predict_proba(transformed_df)
        fraud_prob = float(probs[0, 1])

        # 2. Predicted class based on calibrated threshold
        optimal_thresh = float(self.metadata.get("optimal_threshold", 0.5))
        predicted_class = 1 if fraud_prob >= optimal_thresh else 0

        # 3. Compute SHAP explanations
        explanations = []
        if self.explainer is not None:
            raw_explanations = self.explainer.explain_instance(transformed_df, top_k=5)
            explanations = [e.to_dict() for e in raw_explanations]

        return fraud_prob, predicted_class, explanations

    async def predict_async(
        self,
        amount: float,
        transaction_time: Optional[datetime] = None,
        features_dict: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, int, List[Dict[str, Any]], float]:
        """
        Executes model inference on a worker thread to keep the asyncio loop non-blocking.
        Returns: (fraud_probability, predicted_class, explanations, latency_ms)
        """
        start_time = time.perf_counter()
        transformed_df = self.prepare_feature_dataframe(amount, transaction_time, features_dict)

        try:
            fraud_prob, pred_class, explanations = await asyncio.to_thread(
                self._sync_predict, transformed_df
            )
        except Exception as e:
            logger.error("Inference execution failed: %s", e)
            raise ModelInferenceError(f"Model prediction failed: {str(e)}")

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return fraud_prob, pred_class, explanations, latency_ms

    async def reload(self) -> None:
        """Thread-safe hot-reload of model artifacts."""
        async with self._lock:
            await asyncio.to_thread(self.load_artifacts)


# Global singleton instance
model_manager = ModelArtifactManager()

