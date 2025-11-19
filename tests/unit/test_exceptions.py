"""Unit tests for the exceptions module."""

import pytest

from ifpa_api.core.exceptions import (
    IfpaApiError,
    IfpaClientValidationError,
    IfpaError,
    MissingApiKeyError,
)


class TestIfpaError:
    """Tests for base IfpaError exception."""

    def test_ifpa_error_is_exception(self) -> None:
        """Test that IfpaError is an Exception subclass."""
        assert issubclass(IfpaError, Exception)

    def test_ifpa_error_can_be_raised(self) -> None:
        """Test that IfpaError can be raised and caught."""
        with pytest.raises(IfpaError):
            raise IfpaError("Test error")

    def test_ifpa_error_message(self) -> None:
        """Test that IfpaError preserves error message."""
        message = "Something went wrong"
        with pytest.raises(IfpaError) as exc_info:
            raise IfpaError(message)
        assert str(exc_info.value) == message


class TestMissingApiKeyError:
    """Tests for MissingApiKeyError."""

    def test_missing_api_key_error_is_ifpa_error(self) -> None:
        """Test that MissingApiKeyError is an IfpaError subclass."""
        assert issubclass(MissingApiKeyError, IfpaError)

    def test_missing_api_key_error_message(self) -> None:
        """Test that MissingApiKeyError preserves message."""
        message = "API key is required"
        with pytest.raises(MissingApiKeyError) as exc_info:
            raise MissingApiKeyError(message)
        assert str(exc_info.value) == message

    def test_missing_api_key_error_can_be_caught_as_ifpa_error(self) -> None:
        """Test that MissingApiKeyError can be caught as IfpaError."""
        with pytest.raises(IfpaError):
            raise MissingApiKeyError("No key")


class TestIfpaApiError:
    """Tests for IfpaApiError."""

    def test_ifpa_sdk_error_is_ifpa_error(self) -> None:
        """Test that IfpaApiError is an IfpaError subclass."""
        assert issubclass(IfpaApiError, IfpaError)

    def test_ifpa_sdk_error_with_status_code(self) -> None:
        """Test IfpaApiError with status code."""
        error = IfpaApiError("Not found", status_code=404)
        assert error.message == "Not found"
        assert error.status_code == 404

    def test_ifpa_sdk_error_with_response_body(self) -> None:
        """Test IfpaApiError with response body."""
        body = {"error": "Player not found"}
        error = IfpaApiError("Not found", status_code=404, response_body=body)
        assert error.response_body == body

    def test_ifpa_sdk_error_string_representation(self) -> None:
        """Test __str__ includes status code when available."""
        error = IfpaApiError("Not found", status_code=404)
        assert str(error) == "[404] Not found"

    def test_ifpa_sdk_error_string_representation_without_status(self) -> None:
        """Test __str__ without status code."""
        error = IfpaApiError("Network error", status_code=None)
        assert str(error) == "Network error"

    def test_ifpa_sdk_error_repr(self) -> None:
        """Test __repr__ includes all details."""
        error = IfpaApiError("Not found", status_code=404, response_body={"error": "missing"})
        repr_str = repr(error)
        assert "IfpaApiError" in repr_str
        assert "404" in repr_str
        assert "Not found" in repr_str

    def test_ifpa_sdk_error_attributes_none_when_not_provided(self) -> None:
        """Test that attributes are None when not provided."""
        error = IfpaApiError("Generic error")
        assert error.message == "Generic error"
        assert error.status_code is None
        assert error.response_body is None

    def test_ifpa_sdk_error_can_be_caught_as_ifpa_error(self) -> None:
        """Test that IfpaApiError can be caught as IfpaError."""
        with pytest.raises(IfpaError):
            raise IfpaApiError("API error", status_code=500)


class TestIfpaClientValidationError:
    """Tests for IfpaClientValidationError."""

    def test_validation_error_is_ifpa_error(self) -> None:
        """Test that IfpaClientValidationError is an IfpaError subclass."""
        assert issubclass(IfpaClientValidationError, IfpaError)

    def test_validation_error_message(self) -> None:
        """Test that validation error preserves message."""
        message = "Invalid player_id"
        error = IfpaClientValidationError(message)
        assert error.message == message

    def test_validation_error_with_validation_errors(self) -> None:
        """Test IfpaClientValidationError with validation errors details."""
        errors = [{"field": "player_id", "type": "value_error"}]
        error = IfpaClientValidationError("Validation failed", validation_errors=errors)
        assert error.validation_errors == errors

    def test_validation_error_string_representation(self) -> None:
        """Test __str__ includes validation errors when available."""
        errors = [{"field": "player_id", "type": "value_error"}]
        error = IfpaClientValidationError("Validation failed", validation_errors=errors)
        str_repr = str(error)
        assert "Validation failed" in str_repr

    def test_validation_error_string_representation_without_errors(self) -> None:
        """Test __str__ without validation errors."""
        error = IfpaClientValidationError("Validation failed", validation_errors=None)
        assert str(error) == "Validation failed"

    def test_validation_error_repr(self) -> None:
        """Test __repr__ includes all details."""
        errors = [{"field": "player_id", "type": "value_error"}]
        error = IfpaClientValidationError("Validation failed", validation_errors=errors)
        repr_str = repr(error)
        assert "IfpaClientValidationError" in repr_str
        assert "Validation failed" in repr_str

    def test_validation_error_can_be_caught_as_ifpa_error(self) -> None:
        """Test that IfpaClientValidationError can be caught as IfpaError."""
        with pytest.raises(IfpaError):
            raise IfpaClientValidationError("Validation failed")
