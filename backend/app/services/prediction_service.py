"""
FraudShield Real-Time and Batch Prediction Orchestration Service.
"""

from datetime import datetime, timedelta, timezone
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ResourceNotFoundError
from backend.app.ml.loader import model_manager
from backend.app.models.prediction import Prediction, RecommendedAction, RiskLevel
from backend.app.models.transaction import Transaction, TransactionStatus
from backend.app.repositories.prediction_repo import PredictionRepository
from backend.app.repositories.transaction_repo import TransactionRepository
from backend.app.schemas.prediction import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    FeatureAttribution,
    PredictionRequest,
    PredictionResponse,
)
from backend.app.services.risk_engine import RiskEngine

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, session: Session):
        self.session = session
        self.txn_repo = TransactionRepository(session)
        self.pred_repo = PredictionRepository(session)
        self.risk_engine = RiskEngine()

    def predict_single(self, request: PredictionRequest) -> PredictionResponse:
        """
        Coordinates full inference lifecycle:
        Validation -> ML Inference -> SHAP Explainability -> Risk Rule Engine -> Persistence.
        """
        txn_time = request.transaction_time or datetime.now(timezone.utc)

        # 1. Check or create transaction
        txn = self.txn_repo.get_by_external_id(request.transaction_id)
        if not txn:
            txn = Transaction(
                external_transaction_id=request.transaction_id,
                amount=request.amount,
                transaction_time=txn_time,
                merchant_category=request.merchant_category,
                device_id=request.device_id,
                location=request.location,
                user_id=request.user_id,
                status=TransactionStatus.PENDING.value,
            )
            txn = self.txn_repo.create(txn)

        # 2. Query historical transactions for velocity & spike rules
        observation_window = txn_time - timedelta(hours=24)
        historical_txns = self.txn_repo.get_recent_transactions_by_device_or_user(
            user_id=request.user_id,
            device_id=request.device_id,
            since_time=observation_window,
        )

        # 3. Model Inference (Sync execution on transformed df)
        transformed_df = model_manager.prepare_feature_dataframe(
            amount=request.amount,
            transaction_time=txn_time,
            features_dict=request.features,
        )
        import time
        start_time = time.perf_counter()
        fraud_prob, pred_class, raw_explanations = model_manager._sync_predict(transformed_df)
        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # 4. Risk Engine Evaluation
        risk_result = self.risk_engine.evaluate(
            ml_probability=fraud_prob,
            amount=request.amount,
            transaction_time=txn_time,
            merchant_category=request.merchant_category,
            historical_transactions=historical_txns,
            location=request.location,
            device_id=request.device_id,
        )

        # 5. Update transaction status if flagged
        if risk_result.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
            txn.status = TransactionStatus.FLAGGED.value
            self.session.flush()

        # 6. Persist or update Prediction entity
        prediction_entity = self.pred_repo.get_by_transaction_id(txn.id)
        if not prediction_entity:
            prediction_entity = Prediction(
                transaction_id=txn.id,
                model_version=model_manager.metadata.get("version", "v1.0.0"),
                fraud_probability=risk_result.ml_probability,
                predicted_class=pred_class,
                risk_level=risk_result.risk_level.value,
                recommended_action=risk_result.recommended_action.value,
                explanation=raw_explanations,
                rule_triggers=risk_result.triggered_rules,
                inference_latency_ms=latency_ms,
            )
            prediction_entity = self.pred_repo.create(prediction_entity)
        else:
            prediction_entity.fraud_probability = risk_result.ml_probability
            prediction_entity.predicted_class = pred_class
            prediction_entity.risk_level = risk_result.risk_level.value
            prediction_entity.recommended_action = risk_result.recommended_action.value
            prediction_entity.explanation = raw_explanations
            prediction_entity.rule_triggers = risk_result.triggered_rules
            prediction_entity.inference_latency_ms = latency_ms
            self.session.flush()
            self.session.refresh(prediction_entity)

        # Build feature attribution response
        attributions = [FeatureAttribution(**item) for item in raw_explanations]

        return PredictionResponse(
            prediction_id=prediction_entity.id,
            transaction_id=request.transaction_id,
            fraud_probability=risk_result.ml_probability,
            prediction="FRAUD" if pred_class == 1 else "LEGITIMATE",
            risk_level=risk_result.risk_level,
            recommended_action=risk_result.recommended_action,
            model_version=prediction_entity.model_version,
            inference_latency_ms=latency_ms,
            rule_triggers=risk_result.triggered_rules,
            explanations=attributions,
            created_at=prediction_entity.created_at,
        )

    def predict_batch(self, payload: BatchPredictionRequest) -> BatchPredictionResponse:
        results: List[PredictionResponse] = []
        for txn_req in payload.transactions:
            resp = self.predict_single(txn_req)
            results.append(resp)

        high_risk_count = sum(1 for r in results if r.risk_level == RiskLevel.HIGH)
        fraud_predicted_count = sum(1 for r in results if r.prediction == "FRAUD")

        summary = {
            "total_records": len(results),
            "fraud_predictions": fraud_predicted_count,
            "high_risk_flags": high_risk_count,
            "fraud_rate_pct": round(fraud_predicted_count / len(results) * 100, 2) if results else 0.0,
        }

        return BatchPredictionResponse(
            total_processed=len(results),
            predictions=results,
            summary=summary,
        )

    def get_prediction_by_id(self, prediction_id: str) -> PredictionResponse:
        pred = self.pred_repo.get_by_id(prediction_id)
        if not pred:
            raise ResourceNotFoundError(f"Prediction with ID '{prediction_id}' not found.")

        txn = self.txn_repo.get_by_id(pred.transaction_id)
        ext_txn_id = txn.external_transaction_id if txn else "UNKNOWN"

        raw_exp = pred.explanation if isinstance(pred.explanation, list) else []
        attributions = [FeatureAttribution(**item) for item in raw_exp]

        return PredictionResponse(
            prediction_id=pred.id,
            transaction_id=ext_txn_id,
            fraud_probability=pred.fraud_probability,
            prediction="FRAUD" if pred.predicted_class == 1 else "LEGITIMATE",
            risk_level=RiskLevel(pred.risk_level),
            recommended_action=RecommendedAction(pred.recommended_action),
            model_version=pred.model_version,
            inference_latency_ms=pred.inference_latency_ms,
            rule_triggers=pred.rule_triggers if isinstance(pred.rule_triggers, list) else [],
            explanations=attributions,
            created_at=pred.created_at,
        )
