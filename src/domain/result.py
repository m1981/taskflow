from dataclasses import dataclass
from typing import Optional, Generic, TypeVar

T = TypeVar('T')

@dataclass(frozen=True)
class Result(Generic[T]):
    """Generic result type for handling success/error cases"""
    success: bool
    error: Optional[str] = None
    data: Optional[T] = None

@dataclass(frozen=True)
class Success(Result[T]):
    """Represents a successful result"""
    success: bool = True
    error: Optional[str] = None
    data: Optional[T] = None

@dataclass(frozen=True)
class Error(Result[T]):
    """Represents an error result"""
    success: bool = False
    data: Optional[T] = None

def success(data: T) -> Success[T]:
    """Create a successful result with data"""
    return Success(data=data)

def error(message: str) -> Error:
    """Create an error result with message"""
    return Error(error=message)