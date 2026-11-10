"""
FraudShield Deterministic Risk Rule Engine.
Combines machine learning probability with heuristic business rules into an explainable risk tier.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.config import settings
from backend.app.models.prediction import RecommendedAction, RiskLevel
from backend.app.models.transaction import Transaction

logger = logging.getLogger(__name__)


@dataclass
class RiskEvaluationResult:
    ml_probability: float
    risk_level: RiskLevel
    recommended_action: RecommendedAction
    triggered_rules: List[str]
    rule_score: float
    explanation_notes: List[str] = field(default_factory=list)


class RiskEngine:
    """
    Configurable hybrid risk assessment engine.
    Separates statistical ML probability from deterministic business policy rules.
    Guarantees transactions are not automatically blocked solely based on unvalidated predictions.
    """

    def __init__(
        self,
        low_threshold: float = settings.RISK_THRESHOLD_LOW,
        high_threshold: float = settings.RISK_THRESHOLD_HIGH,
        amount_spike_multiplier: float = settings.AMOUNT_SPIKE_MULTIPLIER,
        velocity_count_threshold: int = settings.VELOCITY_TXN_COUNT_THRESHOLD,
    ):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.amount_spike_multiplier = amount_spike_multiplier
        self.velocity_count_threshold = velocity_count_threshold

    def evaluate(
        self,
        ml_probability: float,
        amount: float,
        transaction_time: datetime,
        merchant_category: str,
        historical_transactions: Optional[List[Transaction]] = None,
        location: Optional[str] = None,
        device_id: Optional[str] = None,
    ) -> RiskEvaluationResult:
        """Evaluates business rules alongside the ML probability score."""
        triggered_rules: List[str] = []
        explanation_notes: List[str] = []
        rule_score = 0.0

        # Rule 1: High Absolute Transaction Amount (> $2,500)
        if amount >= 2500.0:
            triggered_rules.append("UNUSUALLY_HIGH_TRANSACTION_AMOUNT")
            rule_score += 0.35
            explanation_notes.append(f"Transaction amount (${amount:,.2f}) exceeds high-value threshold.")

        # Rule 2: Deviation from Historical Average
        if historical_transactions and len(historical_transactions) >= 3:
            past_amounts = [t.amount for t in historical_transactions]
            avg_amount = sum(past_amounts) / len(past_amounts)
            if amount > (avg_amount * self.amount_spike_multiplier):
                triggered_rules.append("SIGNIFICANT_HISTORICAL_AMOUNT_SPIKE")
                rule_score += 0.30
                explanation_notes.append(
                    f"Amount is {amount / avg_amount:.1f}x higher than the user's historical average (${avg_amount:,.2f})."
                )

        # Rule 3: Velocity Spike (Multiple transactions in short window)
        if historical_transactions:
            recent_count = len(historical_transactions)
            if recent_count >= self.velocity_count_threshold:
                triggered_rules.append("HIGH_VELOCITY_RAPID_TRANSACTIONS")
                rule_score += 0.35
                explanation_notes.append(
                    f"Account initiated {recent_count} transactions in the active observation window."
                )

        # Rule 4: Unusual Transaction Timing (Midnight hours 1:00 AM - 5:00 AM)
        txn_hour = transaction_time.hour
        if 1 <= txn_hour <= 4:
            triggered_rules.append("UNUSUAL_TRANSACTION_TIMING")
            rule_score += 0.15
            explanation_notes.append(f"Transaction occurred during off-peak night hours ({txn_hour:02d}:00 UTC).")

        # Rule 5: High-Risk Merchant Category
        high_risk_categories = {"gambling", "crypto", "wire_transfer", "cash_advance", "luxury_jewelry"}
        if merchant_category.lower().strip() in high_risk_categories:
            triggered_rules.append("HIGH_RISK_MERCHANT_CATEGORY")
            rule_score += 0.25
            explanation_notes.append(f"Merchant category '{merchant_category}' is classified as elevated risk.")

        # Cap rule score at 1.0
        rule_score = min(rule_score, 1.0)

        # --- Combined Risk Resolution ---
        # Keep ML probability separate from the composite decision logic
        if ml_probability >= self.high_threshold or rule_score >= 0.70:
            risk_level = RiskLevel.HIGH
            # Safety safeguard: Never auto-block solely on ML; flag for review unless severe rule combination
            recommended_action = RecommendedAction.FLAG_FOR_REVIEW
        elif ml_probability >= self.low_threshold or rule_score >= 0.35:
            risk_level = RiskLevel.MEDIUM
            recommended_action = RecommendedAction.FLAG_FOR_REVIEW
        else:
            risk_level = RiskLevel.LOW
            recommended_action = RecommendedAction.ALLOW

        return RiskEvaluationResult(
            ml_probability=round(ml_probability, 4),
            risk_level=risk_level,
            recommended_action=recommended_action,
            triggered_rules=triggered_rules,
            rule_score=round(rule_score, 4),
            explanation_notes=explanation_notes,
        )

