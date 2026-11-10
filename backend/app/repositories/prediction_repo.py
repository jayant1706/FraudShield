"""
FraudShield Prediction Repository.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.prediction import Prediction
from backend.app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: Session):
        super().__init__(Prediction, session)

    def get_by_transaction_id(self, transaction_id: str) -> Optional[Prediction]:
        stmt = select(Prediction).where(Prediction.transaction_id == transaction_id)
        return self.session.execute(stmt).scalars().first()
