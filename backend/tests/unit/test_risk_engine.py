"""
Unit Tests for FraudShield Risk Rule Engine.
"""

from datetime import datetime, timezone
import pytest

from backend.app.models.prediction import RecommendedAction, RiskLevel
from backend.app.models.transaction import Transaction
from backend.app.services.risk_engine import RiskEngine


def test_risk_engine_low_risk_transaction():
    engine = RiskEngine()
    now = datetime(2026, 11, 8, 14, 0, 0, tzinfo=timezone.utc)  # Afternoon 2 PM

    result = engine.evaluate(
        ml_probability=0.08,
        amount=45.50,
        transaction_time=now,
        merchant_category="grocery",
    )

    assert result.risk_level == RiskLevel.LOW
    assert result.recommended_action == RecommendedAction.ALLOW
    assert len(result.triggered_rules) == 0
    assert result.ml_probability == 0.08


def test_risk_engine_high_amount_rule():
    engine = RiskEngine()
    now = datetime(2026, 11, 8, 14, 0, 0, tzinfo=timezone.utc)

    result = engine.evaluate(
        ml_probability=0.15,
        amount=3500.0,  # Exceeds $2,500 threshold
        transaction_time=now,
        merchant_category="electronics",
    )

    assert "UNUSUALLY_HIGH_TRANSACTION_AMOUNT" in result.triggered_rules
    assert result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]


def test_risk_engine_unusual_timing_rule():
    engine = RiskEngine()
    midnight_time = datetime(2026, 11, 8, 2, 30, 0, tzinfo=timezone.utc)  # 2:30 AM

    result = engine.evaluate(
        ml_probability=0.20,
        amount=120.0,
        transaction_time=midnight_time,
        merchant_category="retail",
    )

    assert "UNUSUAL_TRANSACTION_TIMING" in result.triggered_rules


def test_risk_engine_high_risk_merchant_rule():
    engine = RiskEngine()
    now = datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc)

    result = engine.evaluate(
        ml_probability=0.10,
        amount=50.0,
        transaction_time=now,
        merchant_category="crypto",
    )

    assert "HIGH_RISK_MERCHANT_CATEGORY" in result.triggered_rules


def test_risk_engine_historical_amount_spike():
    engine = RiskEngine()
    now = datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc)

    historical = [
        Transaction(amount=20.0, external_transaction_id="TX1", merchant_category="groceries"),
        Transaction(amount=30.0, external_transaction_id="TX2", merchant_category="groceries"),
        Transaction(amount=25.0, external_transaction_id="TX3", merchant_category="groceries"),
    ]

    result = engine.evaluate(
        ml_probability=0.10,
        amount=500.0,  # Average is 25, 500 is 20x spike
        transaction_time=now,
        merchant_category="groceries",
        historical_transactions=historical,
    )

    assert "SIGNIFICANT_HISTORICAL_AMOUNT_SPIKE" in result.triggered_rules


def test_risk_engine_high_ml_probability_flags_for_review():
    engine = RiskEngine()
    now = datetime(2026, 11, 8, 12, 0, 0, tzinfo=timezone.utc)

    result = engine.evaluate(
        ml_probability=0.88,
        amount=15.0,
        transaction_time=now,
        merchant_category="grocery",
    )

    assert result.risk_level == RiskLevel.HIGH
    assert result.recommended_action == RecommendedAction.FLAG_FOR_REVIEW

