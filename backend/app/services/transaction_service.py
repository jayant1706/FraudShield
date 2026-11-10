"""
FraudShield Transaction Lifecycle Management Service.
"""

from datetime import datetime
import logging
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import ConflictError, ResourceNotFoundError
from backend.app.models.transaction import Transaction, TransactionStatus
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.transaction_repo import TransactionRepository
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionStatusUpdate,
)

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.txn_repo = TransactionRepository(session)
        self.audit_repo = AuditRepository(session)

    def ingest_transaction(self, payload: TransactionCreate) -> Transaction:
        existing = self.txn_repo.get_by_external_id(payload.external_transaction_id)
        if existing:
            raise ConflictError(
                f"Transaction with ID '{payload.external_transaction_id}' already exists."
            )

        txn = Transaction(
            external_transaction_id=payload.external_transaction_id,
            amount=payload.amount,
            transaction_time=payload.transaction_time or datetime.now(),
            merchant_category=payload.merchant_category,
            device_id=payload.device_id,
            location=payload.location,
            user_id=payload.user_id,
            status=TransactionStatus.PENDING.value,
        )
        return self.txn_repo.create(txn)

    def get_transaction_by_id(self, txn_id: str) -> TransactionResponse:
        txn = self.txn_repo.get_by_id_with_prediction(txn_id)
        if not txn:
            raise ResourceNotFoundError(f"Transaction with ID '{txn_id}' not found.")
        return TransactionResponse.model_validate(txn)

    def get_transaction_by_external_id(self, ext_id: str) -> TransactionResponse:
        txn = self.txn_repo.get_by_external_id(ext_id)
        if not txn:
            raise ResourceNotFoundError(f"Transaction with ID '{ext_id}' not found.")
        return TransactionResponse.model_validate(txn)

    def list_transactions(
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
    ) -> PaginatedResponse[TransactionResponse]:
        items, total = self.txn_repo.list_filtered(
            page=page,
            page_size=page_size,
            status=status,
            risk_level=risk_level,
            merchant_category=merchant_category,
            search=search,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
        )

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1
        return PaginatedResponse(
            items=[TransactionResponse.model_validate(t) for t in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def update_investigation_status(
        self,
        txn_id: str,
        payload: TransactionStatusUpdate,
        actor_id: Optional[str] = None,
    ) -> TransactionResponse:
        txn = self.txn_repo.get_by_id_with_prediction(txn_id)
        if not txn:
            raise ResourceNotFoundError(f"Transaction '{txn_id}' not found.")

        old_status = txn.status
        txn.status = payload.status.value
        if payload.investigation_notes:
            txn.investigation_notes = payload.investigation_notes

        self.session.flush()
        self.session.refresh(txn)

        self.audit_repo.log_action(
            action="TRANSACTION_STATUS_UPDATED",
            resource_type="TRANSACTION",
            resource_id=txn.id,
            user_id=actor_id,
            details={
                "external_id": txn.external_transaction_id,
                "old_status": old_status,
                "new_status": txn.status,
                "notes": payload.investigation_notes,
            },
        )
        return TransactionResponse.model_validate(txn)
