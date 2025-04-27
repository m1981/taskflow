from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, Union

T = TypeVar('T')

class Result(Generic[T]):
    """Base class for Result types"""
    @staticmethod
    def success(data: Optional[T] = None) -> 'Success[T]':
        return Success(data=data)

    @staticmethod
    def error(message: str) -> 'Error[T]':
        return Error(error=message)

@dataclass(frozen=True)
class Success(Result[T]):
    """Represents a successful result with optional data"""
    data: Optional[T] = None
    success: bool = True
    error: Optional[str] = None

@dataclass(frozen=True)
class Error(Result[T]):
    """Represents a failed result with error message"""
    error: str
    success: bool = False
    data: Optional[T] = None

# Type alias for convenience
ResultType = Union[Success[T], Error[T]]
