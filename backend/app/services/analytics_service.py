"""
FraudShield Real-Time Analytics and Investigator Dashboard Aggregation Service.
"""

from datetime import datetime
from typing import List
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction, RiskLevel
from backend.app.models.transaction import Transaction, TransactionStatus
from backend.app.schemas.analytics import (
    AnalyticsOverview,
    FraudTrendPoint,
    FraudTrendsResponse,
    RiskDistributionItem,
    RiskDistributionResponse,
    TransactionVolumeResponse,
    VolumePoint,
)


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session

    def get_overview(self) -> AnalyticsOverview:
        # 1. Total transaction metrics
        txn_stats_stmt = select(
            func.count(Transaction.id).label("total_count"),
            func.coalesce(func.sum(Transaction.amount), 0.0).label("total_volume"),
        )
        total_txns, total_volume = self.session.execute(txn_stats_stmt).one()

        # 2. Status counts
        status_counts_stmt = select(Transaction.status, func.count(Transaction.id)).group_by(
            Transaction.status
        )
        status_dict = dict(self.session.execute(status_counts_stmt).all())

        pending_count = status_dict.get(TransactionStatus.PENDING.value, 0)
        flagged_count = status_dict.get(TransactionStatus.FLAGGED.value, 0)
        rejected_count = status_dict.get(TransactionStatus.REJECTED.value, 0)
        approved_count = status_dict.get(TransactionStatus.APPROVED.value, 0)

        # 3. Prediction risk level breakdown
        risk_stmt = select(Prediction.risk_level, func.count(Prediction.id)).group_by(
            Prediction.risk_level
        )
        risk_dict = dict(self.session.execute(risk_stmt).all())

        high_risk_cnt = risk_dict.get(RiskLevel.HIGH.value, 0)
        med_risk_cnt = risk_dict.get(RiskLevel.MEDIUM.value, 0)
        low_risk_cnt = risk_dict.get(RiskLevel.LOW.value, 0)

        # Fraud volume ($)
        fraud_vol_stmt = (
            select(func.coalesce(func.sum(Transaction.amount), 0.0))
            .join(Transaction.prediction)
            .where((Prediction.predicted_class == 1) | (Transaction.status == TransactionStatus.REJECTED.value))
        )
        fraud_dollar_volume = float(self.session.execute(fraud_vol_stmt).scalar() or 0.0)

        fraud_count = high_risk_cnt + rejected_count
        fraud_rate = (fraud_count / total_txns * 100) if total_txns > 0 else 0.0
        legit_count = max(total_txns - fraud_count, 0)

        return AnalyticsOverview(
            total_transactions=total_txns,
            fraudulent_transactions=fraud_count,
            legitimate_transactions=legit_count,
            pending_investigations=pending_count,
            flagged_transactions=flagged_count,
            fraud_rate_percentage=round(fraud_rate, 2),
            total_dollar_volume=round(float(total_volume), 2),
            fraud_dollar_volume=round(fraud_dollar_volume, 2),
            high_risk_count=high_risk_cnt,
            medium_risk_count=med_risk_cnt,
            low_risk_count=low_risk_cnt,
        )

    def get_fraud_trends(self, days: int = 7) -> FraudTrendsResponse:
        stmt = (
            select(
                func.date(Transaction.transaction_time).label("txn_date"),
                func.count(Transaction.id).label("total_vol"),
                func.sum(
                    case((Prediction.predicted_class == 1, 1), else_=0)
                ).label("fraud_cnt"),
                func.coalesce(func.sum(Transaction.amount), 0.0).label("tot_amount"),
                func.coalesce(
                    func.sum(
                        case((Prediction.predicted_class == 1, Transaction.amount), else_=0.0)
                    ),
                    0.0,
                ).label("fraud_amt"),
            )
            .outerjoin(Transaction.prediction)
            .group_by(func.date(Transaction.transaction_time))
            .order_by(func.date(Transaction.transaction_time))
        )
        rows = self.session.execute(stmt).all()

        points: List[FraudTrendPoint] = []
        for r in rows:
            points.append(
                FraudTrendPoint(
                    timestamp=str(r.txn_date or "Today"),
                    total_volume=int(r.total_vol or 0),
                    fraud_count=int(r.fraud_cnt or 0),
                    total_amount=round(float(r.tot_amount or 0.0), 2),
                    fraud_amount=round(float(r.fraud_amt or 0.0), 2),
                )
            )

        if not points:
            points.append(
                FraudTrendPoint(
                    timestamp=datetime.now().strftime("%Y-%m-%d"),
                    total_volume=0,
                    fraud_count=0,
                    total_amount=0.0,
                    fraud_amount=0.0,
                )
            )

        return FraudTrendsResponse(trends=points)

    def get_risk_distribution(self) -> RiskDistributionResponse:
        stmt = select(Prediction.risk_level, func.count(Prediction.id)).group_by(
            Prediction.risk_level
        )
        data = dict(self.session.execute(stmt).all())
        total = sum(data.values())

        items = []
        for level in [RiskLevel.LOW.value, RiskLevel.MEDIUM.value, RiskLevel.HIGH.value]:
            cnt = data.get(level, 0)
            pct = round(cnt / total * 100, 2) if total > 0 else 0.0
            items.append(RiskDistributionItem(risk_level=level, count=cnt, percentage=pct))

        return RiskDistributionResponse(distribution=items)

    def get_transaction_volume(self) -> TransactionVolumeResponse:
        stmt = (
            select(
                func.date(Transaction.transaction_time).label("date_label"),
                func.count(Transaction.id).label("txn_count"),
                func.coalesce(func.sum(Transaction.amount), 0.0).label("dollar_vol"),
            )
            .group_by(func.date(Transaction.transaction_time))
            .order_by(func.date(Transaction.transaction_time))
        )
        rows = self.session.execute(stmt).all()

        v_points = [
            VolumePoint(
                date=str(r.date_label or "Today"),
                transaction_count=int(r.txn_count or 0),
                dollar_volume=round(float(r.dollar_vol or 0.0), 2),
            )
            for r in rows
        ]

        if not v_points:
            v_points.append(
                VolumePoint(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    transaction_count=0,
                    dollar_volume=0.0,
                )
            )

        return TransactionVolumeResponse(volume=v_points)
