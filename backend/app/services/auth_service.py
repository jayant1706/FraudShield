"""
FraudShield Authentication and Authorization Service.
"""

from datetime import timedelta
import logging
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import AuthenticationError, ConflictError, ResourceNotFoundError
from backend.app.core.security import create_access_token, get_password_hash, verify_password
from backend.app.models.user import User, UserRole
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.schemas.auth import Token, UserCreate, UserLogin, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)

    def register_user(self, payload: UserCreate, actor_id: Optional[str] = None) -> UserResponse:
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictError(f"User with email '{payload.email}' already exists.")

        # Security Policy: Public registration cannot self-grant ADMIN role
        requested_role = payload.role.value if payload.role else UserRole.INVESTIGATOR.value
        assigned_role = requested_role if requested_role != UserRole.ADMIN.value else UserRole.INVESTIGATOR.value

        user = User(
            email=payload.email.lower().strip(),
            full_name=payload.full_name.strip(),
            password_hash=get_password_hash(payload.password),
            role=assigned_role,
            is_active=True,
        )
        created_user = self.user_repo.create(user)

        self.audit_repo.log_action(
            action="USER_REGISTERED",
            resource_type="USER",
            resource_id=created_user.id,
            user_id=actor_id or created_user.id,
            details={"email": created_user.email, "role": created_user.role},
        )
        return UserResponse.model_validate(created_user)

    def authenticate(self, payload: UserLogin, ip_address: Optional[str] = None) -> Token:
        user = self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("User account is inactive. Please contact an administrator.")

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token_str = create_access_token(
            subject=user.id,
            role=user.role,
            expires_delta=expires_delta,
        )

        self.audit_repo.log_action(
            action="USER_LOGIN_SUCCESS",
            resource_type="USER",
            resource_id=user.id,
            user_id=user.id,
            ip_address=ip_address,
            details={"email": user.email},
        )

        return Token(
            access_token=token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user),
        )

    def get_current_user_profile(self, user_id: str) -> UserResponse:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User not found.")
        return UserResponse.model_validate(user)
