"""
FraudShield Dependency Injection Providers.
Authentication, Authorization, Database Sessions, and Model Access.
"""

from typing import Annotated, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.security import decode_access_token
from backend.app.db.session import get_db
from backend.app.ml.loader import ModelArtifactManager, model_manager
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repo import UserRepository

reusable_oauth2 = HTTPBearer(auto_error=True)


def get_current_user(
    token_auth: Annotated[HTTPAuthorizationCredentials, Depends(reusable_oauth2)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validates JWT access token and returns the authenticated User entity."""
    token = token_auth.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


def require_role(*allowed_roles: UserRole):
    """Factory creating an RBAC dependency ensuring the caller has the required role."""
    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        user_role = current_user.role
        allowed_values = [r.value for r in allowed_roles]
        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_values}. Your role: '{user_role}'.",
            )
        return current_user

    return role_checker


def get_model() -> ModelArtifactManager:
    return model_manager
