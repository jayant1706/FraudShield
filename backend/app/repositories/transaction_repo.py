"""
FraudShield Transaction Repository with Dynamic Filtering and Joined Predictions.
"""

from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from backend.app.models.prediction import Prediction
from backend.app.models.transaction import Transaction, TransactionStatus
from backend.app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: Session):
        super().__init__(Transaction, session)

    def get_by_external_id(self, external_id: str) -> Optional[Transaction]:
        stmt = (
            select(Transaction)
            .options(joinedload(Transaction.prediction))
            .where(Transaction.external_transaction_id == external_id)
        )
        return self.session.execute(stmt).scalars().first()

    def get_by_id_with_prediction(self, id: str) -> Optional[Transaction]:
        stmt = (
            select(Transaction)
            .options(joinedload(Transaction.prediction))
            .where(Transaction.id == id)
        )
        return self.session.execute(stmt).scalars().first()

    def list_filtered(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        merchant_category: Optional[str] = None,
        search: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
    ) -> Tuple[List[Transaction], int]:
        stmt = select(Transaction).options(joinedload(Transaction.prediction))

        if risk_level:
            stmt = stmt.join(Transaction.prediction).where(Prediction.risk_level == risk_level)

        if status:
            stmt = stmt.where(Transaction.status == status)
        if merchant_category:
            stmt = stmt.where(Transaction.merchant_category == merchant_category)
        if min_amount is not None:
            stmt = stmt.where(Transaction.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Transaction.amount <= max_amount)
        if start_date:
            stmt = stmt.where(Transaction.transaction_time >= start_date)
        if end_date:
            stmt = stmt.where(Transaction.transaction_time <= end_date)
        if user_id:
            stmt = stmt.where(Transaction.user_id == user_id)
        if search:
            stmt = stmt.where(
                Transaction.external_transaction_id.ilike(f"%{search}%")
                | Transaction.merchant_category.ilike(f"%{search}%")
                | Transaction.location.ilike(f"%{search}%")
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total_count = self.session.execute(count_stmt).scalar() or 0

        # Apply sorting and pagination
        stmt = stmt.order_by(Transaction.transaction_time.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        items = list(self.session.execute(stmt).scalars().all())
        return items, total_count

    def get_recent_transactions_by_device_or_user(
        self,
        user_id: Optional[str],
        device_id: Optional[str],
        since_time: datetime,
    ) -> List[Transaction]:
        stmt = select(Transaction).where(Transaction.transaction_time >= since_time)
        conditions = []
        if user_id:
            conditions.append(Transaction.user_id == user_id)
        if device_id:
            conditions.append(Transaction.device_id == device_id)

        if not conditions:
            return []

        stmt = stmt.where(or_(*conditions)).order_by(Transaction.transaction_time.desc())
        return list(self.session.execute(stmt).scalars().all())
