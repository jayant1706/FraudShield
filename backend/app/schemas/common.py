"""
FraudShield Common Schemas and Generic Pagination Wrappers.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str
    success: bool = True
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    request_id: Optional[str] = None
    details: Optional[dict] = None

