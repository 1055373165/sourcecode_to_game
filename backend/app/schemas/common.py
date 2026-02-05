"""
Common Pydantic schemas
"""
from pydantic import BaseModel
from typing import Generic, TypeVar, List, Any

DataT = TypeVar('DataT')


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response"""
    items: List[DataT]
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    message: str
    details: Any = None
