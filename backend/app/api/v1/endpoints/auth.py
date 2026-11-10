"""
FraudShield Authentication Endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user, get_db
from backend.app.core.exceptions import AuthenticationError, ConflictError
from backend.app.models.user import User
from backend.app.schemas.auth import Token, UserCreate, UserLogin, UserResponse
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    auth_service = AuthService(db)
    try:
        return auth_service.register_user(payload)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=Token)
def login(
    payload: UserLogin,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    try:
        return auth_service.authenticate(payload, ip_address=ip_address)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return UserResponse.model_validate(current_user)
