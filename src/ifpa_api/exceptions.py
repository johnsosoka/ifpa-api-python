"""Custom exceptions for the IFPA SDK.

This module defines the exception hierarchy for the SDK, providing clear error
messages and appropriate error information for different failure scenarios.
"""

from typing import Any


class IfpaError(Exception):
    """Base exception for all IFPA SDK errors.

    All custom exceptions in the SDK inherit from this base class, making it
    easy to catch any SDK-related error.
    """


class MissingApiKeyError(IfpaError):
    """Raised when no API key is provided or available in environment.

    This error occurs during client initialization when:
    - No api_key is passed to the constructor
    - The IFPA_API_KEY environment variable is not set
    """


class IfpaApiError(IfpaError):
    """Raised when the IFPA API returns a non-2xx HTTP status code.

    This exception wraps HTTP errors from the API, providing access to the
    status code, error message, and raw response body for debugging.

    Attributes:
        status_code: The HTTP status code returned by the API
        message: A human-readable error message
        response_body: The raw response body from the API (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: Any | None = None,
    ) -> None:
        """Initialize an API error.

        Args:
            message: A human-readable error message
            status_code: The HTTP status code from the API response
            response_body: The raw response body (typically dict or string)
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.response_body = response_body

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"IfpaApiError(message={self.message!r}, "
            f"status_code={self.status_code!r}, "
            f"response_body={self.response_body!r})"
        )


class IfpaClientValidationError(IfpaError):
    """Raised when client-side request validation fails.

    This error occurs when validate_requests=True and Pydantic model validation
    fails for request parameters. It wraps the underlying Pydantic ValidationError
    to provide context about which SDK method call failed.

    Attributes:
        message: A human-readable error message describing the validation failure
        validation_errors: The underlying Pydantic validation error details
    """

    def __init__(self, message: str, validation_errors: Any | None = None) -> None:
        """Initialize a validation error.

        Args:
            message: A human-readable error message
            validation_errors: The underlying Pydantic ValidationError or error details
        """
        super().__init__(message)
        self.message = message
        self.validation_errors = validation_errors

    def __str__(self) -> str:
        """Return a string representation of the validation error."""
        if self.validation_errors:
            return f"{self.message}: {self.validation_errors}"
        return self.message

    def __repr__(self) -> str:
        """Return a detailed representation of the validation error."""
        return (
            f"IfpaClientValidationError(message={self.message!r}, "
            f"validation_errors={self.validation_errors!r})"
        )
