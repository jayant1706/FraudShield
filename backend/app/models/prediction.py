"""
FraudShield Prediction ORM Model and Risk Assessment Enumerations.
"""

from datetime import datetime, timezone
from enum import Enum
import uuid
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendedAction(str, Enum):
    ALLOW = "ALLOW"
    FLAG_FOR_REVIEW = "FLAG_FOR_REVIEW"
    BLOCK = "BLOCK"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    transaction_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("transactions.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fraud_probability: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    predicted_class: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(
        String(20), default=RiskLevel.LOW.value, nullable=False, index=True
    )
    recommended_action: Mapped[str] = mapped_column(
        String(50), default=RecommendedAction.ALLOW.value, nullable=False
    )
    explanation: Mapped[dict | list] = mapped_column(JSON, default=list, nullable=False)
    rule_triggers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    inference_latency_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    transaction = relationship("Transaction", back_populates="prediction")

