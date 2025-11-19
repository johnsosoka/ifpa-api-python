"""Unit tests for enhanced error messages with request context.

Tests for Feature 1: Enhanced Error Messages
- IfpaApiError now includes request_url and request_params fields
- Error string representation includes URL when present
- Error repr includes all fields
"""

import pytest

from ifpa_api.core.exceptions import IfpaApiError


class TestEnhancedErrorFields:
    """Test IfpaApiError with new request_url and request_params fields."""

    def test_error_with_request_context(self) -> None:
        """Test IfpaApiError can be instantiated with request context."""
        error = IfpaApiError(
            message="Resource not found",
            status_code=404,
            response_body={"error": "Not found"},
            request_url="https://api.ifpapinball.com/player/99999",
            request_params={"count": 10, "start_pos": 0},
        )

        assert error.message == "Resource not found"
        assert error.status_code == 404
        assert error.response_body == {"error": "Not found"}
        assert error.request_url == "https://api.ifpapinball.com/player/99999"
        assert error.request_params == {"count": 10, "start_pos": 0}

    def test_error_without_request_context(self) -> None:
        """Test IfpaApiError backward compatibility without new fields."""
        error = IfpaApiError(
            message="Request failed",
            status_code=500,
            response_body="Internal server error",
        )

        assert error.message == "Request failed"
        assert error.status_code == 500
        assert error.response_body == "Internal server error"
        assert error.request_url is None
        assert error.request_params is None

    def test_error_with_none_values(self) -> None:
        """Test IfpaApiError with explicitly None request context."""
        error = IfpaApiError(
            message="Connection error",
            status_code=None,
            response_body=None,
            request_url=None,
            request_params=None,
        )

        assert error.message == "Connection error"
        assert error.status_code is None
        assert error.response_body is None
        assert error.request_url is None
        assert error.request_params is None


class TestEnhancedErrorStringRepresentation:
    """Test __str__ and __repr__ with request context."""

    def test_str_includes_url_when_present(self) -> None:
        """Test that __str__ includes URL in error message."""
        error = IfpaApiError(
            message="Resource not found",
            status_code=404,
            request_url="https://api.ifpapinball.com/player/99999",
        )

        error_str = str(error)
        assert "[404]" in error_str
        assert "Resource not found" in error_str
        assert "(URL: https://api.ifpapinball.com/player/99999)" in error_str

    def test_str_without_url(self) -> None:
        """Test that __str__ works without URL (backward compatible)."""
        error = IfpaApiError(
            message="Request failed",
            status_code=500,
        )

        error_str = str(error)
        assert error_str == "[500] Request failed"
        assert "URL:" not in error_str

    def test_str_without_status_code(self) -> None:
        """Test __str__ when status_code is None."""
        error = IfpaApiError(
            message="Connection timeout",
            request_url="https://api.ifpapinball.com/player/search",
        )

        error_str = str(error)
        assert "Connection timeout" in error_str
        assert "(URL: https://api.ifpapinball.com/player/search)" in error_str
        assert "[" not in error_str  # No status code bracket

    def test_repr_includes_all_fields(self) -> None:
        """Test that __repr__ includes all fields."""
        error = IfpaApiError(
            message="Not found",
            status_code=404,
            response_body={"error": "Player not found"},
            request_url="https://api.ifpapinball.com/player/99999",
            request_params={"count": 10},
        )

        error_repr = repr(error)
        assert "IfpaApiError(" in error_repr
        assert "message='Not found'" in error_repr
        assert "status_code=404" in error_repr
        assert "response_body={'error': 'Player not found'}" in error_repr
        assert "request_url='https://api.ifpapinball.com/player/99999'" in error_repr
        assert "request_params={'count': 10}" in error_repr

    def test_repr_with_none_values(self) -> None:
        """Test __repr__ when optional fields are None."""
        error = IfpaApiError(
            message="Error message",
            status_code=None,
            response_body=None,
            request_url=None,
            request_params=None,
        )

        error_repr = repr(error)
        assert "IfpaApiError(" in error_repr
        assert "message='Error message'" in error_repr
        assert "status_code=None" in error_repr
        assert "response_body=None" in error_repr
        assert "request_url=None" in error_repr
        assert "request_params=None" in error_repr


class TestEnhancedErrorExceptionBehavior:
    """Test that enhanced errors behave correctly as exceptions."""

    def test_can_raise_and_catch(self) -> None:
        """Test that enhanced errors can be raised and caught."""
        with pytest.raises(IfpaApiError) as exc_info:
            raise IfpaApiError(
                message="Test error",
                status_code=400,
                request_url="https://api.ifpapinball.com/test",
                request_params={"param": "value"},
            )

        error = exc_info.value
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.request_url == "https://api.ifpapinball.com/test"
        assert error.request_params == {"param": "value"}

    def test_exception_chaining_preserved(self) -> None:
        """Test that exception chaining works with enhanced errors."""
        original_error = ValueError("Original error")

        try:
            try:
                raise original_error
            except ValueError as e:
                raise IfpaApiError(
                    message="API error",
                    status_code=500,
                    request_url="https://api.ifpapinball.com/endpoint",
                ) from e
        except IfpaApiError as api_error:
            assert api_error.message == "API error"
            assert api_error.__cause__ is original_error
