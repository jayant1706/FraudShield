"""
FraudShield Transaction Endpoints.
"""

from datetime import datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db, require_role
from backend.app.core.exceptions import ConflictError, ResourceNotFoundError
from backend.app.models.user import User, UserRole
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionStatusUpdate,
)
from backend.app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    txn_service = TransactionService(db)
    try:
        created = txn_service.ingest_transaction(payload)
        return txn_service.get_transaction_by_id(created.id)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("", response_model=PaginatedResponse[TransactionResponse])
def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    merchant_category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    txn_service = TransactionService(db)
    user_id_scope = current_user.id if current_user.role == UserRole.USER.value else None

    return txn_service.list_transactions(
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
        user_id=user_id_scope,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    txn_service = TransactionService(db)
    try:
        return txn_service.get_transaction_by_id(transaction_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{transaction_id}/status", response_model=TransactionResponse)
def update_transaction_status(
    transaction_id: str,
    payload: TransactionStatusUpdate,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.INVESTIGATOR))],
    db: Annotated[Session, Depends(get_db)],
):
    txn_service = TransactionService(db)
    try:
        return txn_service.update_investigation_status(
            transaction_id, payload, actor_id=current_user.id
        )
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
