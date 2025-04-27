from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, Union

T = TypeVar('T')

@dataclass(frozen=True)
class Success(Generic[T]):
    """Represents a successful result with optional data"""
    data: Optional[T] = None
    success: bool = True
    error: Optional[str] = None

@dataclass(frozen=True)
class Error(Generic[T]):
    """Represents a failed result with error message"""
    error: str
    success: bool = False
    data: Optional[T] = None

# Type alias for union of Success and Error
Result = Union[Success[T], Error[T]]

def success(data: Optional[T] = None) -> Success[T]:
    """Create a successful result"""
    return Success(data=data)

def error(message: str) -> Error[T]:
    """Create an error result"""
    return Error(error=message)
