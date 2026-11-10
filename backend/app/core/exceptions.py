"""
FraudShield Custom Exception Hierarchy and Centralized Error Handling.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class FraudShieldException(Exception):
    """Base exception for all domain errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(FraudShieldException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(FraudShieldException):
    """Raised when user lacks required role/permissions."""
    pass


class ResourceNotFoundError(FraudShieldException):
    """Raised when a requested resource does not exist."""
    pass


class ConflictError(FraudShieldException):
    """Raised when a resource already exists or conflicts."""
    pass


class ValidationError(FraudShieldException):
    """Raised when business validation fails."""
    pass


class ModelInferenceError(FraudShieldException):
    """Raised when ML model prediction fails."""
    pass

