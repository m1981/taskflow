from dataclasses import FrozenInstanceError
import pytest
from src.domain.result import Result, Success, Error, success, error

def test_success_result_with_data():
    result = Success(data="test data")
    assert result.success
    assert result.data == "test data"
    assert result.error is None

def test_success_result_with_none_data():
    result = Success(data=None)
    assert result.success
    assert result.data is None
    assert result.error is None

def test_error_result():
    result = Error(error="something went wrong")
    assert not result.success
    assert result.error == "something went wrong"
    assert result.data is None

def test_result_immutability():
    result = Success(data="test")
    with pytest.raises(FrozenInstanceError):
        result.data = "modified"

def test_success_factory():
    result = success("test data")
    assert isinstance(result, Success)
    assert result.data == "test data"

def test_error_factory():
    result = error("error message")
    assert isinstance(result, Error)
    assert result.error == "error message"

def test_result_type_safety():
    # Generic type hints will be checked by mypy/pyright
    result: Result[int] = Success(data=42)
    assert isinstance(result.data, int)