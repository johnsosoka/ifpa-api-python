"""Low-level async HTTP client for the IFPA API.

This module provides the internal async HTTP client that handles request/response
cycles, authentication, error mapping, and session management using httpx.
"""

import contextlib
from typing import Any

import httpx

from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import IfpaApiError


class _AsyncHttpClient:
    """Internal async HTTP client for making requests to the IFPA API.

    This class is not part of the public API and should only be used internally
    by async resource clients and handles. It manages the underlying httpx.AsyncClient,
    handles authentication, and maps HTTP errors to SDK exceptions.

    Attributes:
        _config: The configuration object containing API key, base URL, etc.
        _client: The httpx.AsyncClient used for all HTTP calls
    """

    def __init__(self, config: Config) -> None:
        """Initialize the async HTTP client.

        Args:
            config: Configuration object with API key, base URL, and settings
        """
        self._config = config
        self._client = self._create_client()

    def _create_client(self) -> httpx.AsyncClient:
        """Create and configure an httpx.AsyncClient with default headers.

        Returns:
            A configured httpx.AsyncClient instance
        """
        return httpx.AsyncClient(
            base_url=self._config.base_url,
            timeout=self._config.timeout,
            headers={
                "X-API-Key": self._config.api_key,
                "Accept": "application/json",
                "User-Agent": "ifpa-api-python",
            },
        )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an async HTTP request to the IFPA API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/player/123")
            params: Optional query parameters
            json: Optional JSON request body

        Returns:
            The parsed JSON response as a dict

        Raises:
            IfpaApiError: If the API returns a non-2xx status code
            httpx.RequestError: For network-level errors
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"

        url = f"{self._config.base_url}{path}"

        try:
            response = await self._client.request(
                method=method,
                url=path,  # httpx AsyncClient with base_url handles paths
                params=params,
                json=json,
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                # Handle empty or invalid JSON responses
                response_data = None

            # Check for error indicators in response body
            # Some IFPA API endpoints return HTTP 200 with errors in the body
            self._check_response_errors(response_data, response.status_code, url, params)

            return response_data

        except httpx.HTTPStatusError as exc:
            # Map HTTP errors to IfpaApiError
            self._handle_http_error(exc, url, params)
        except httpx.TimeoutException as exc:
            raise IfpaApiError(
                message=f"Request timed out after {self._config.timeout} seconds",
                status_code=None,
                response_body=None,
                request_url=url,
                request_params=params,
            ) from exc
        except httpx.RequestError as exc:
            # Network errors, connection errors, etc.
            raise IfpaApiError(
                message=f"Request failed: {str(exc)}",
                status_code=None,
                response_body=None,
                request_url=url,
                request_params=params,
            ) from exc

    def _check_response_errors(
        self,
        response_data: Any,
        status_code: int,
        url: str,
        params: dict[str, Any] | None,
    ) -> None:
        """Check for error indicators in response body.

        The IFPA API sometimes returns HTTP 200 with error details in the
        response body instead of using proper HTTP error codes.

        Args:
            response_data: Parsed JSON response data
            status_code: HTTP status code from response
            url: The full URL that was requested
            params: The query parameters sent with the request

        Raises:
            IfpaApiError: If error indicators are found in response body
        """
        # Check for null/None response (often indicates invalid ID or not found)
        if response_data is None:
            raise IfpaApiError(
                message="API returned null response (resource not found or invalid ID)",
                status_code=404,
                response_body=None,
                request_url=url,
                request_params=params,
            )

        if not isinstance(response_data, dict):
            return

        # Check for {"error": "..."} pattern
        if "error" in response_data:
            error_message = response_data["error"]
            raise IfpaApiError(
                message=error_message,
                status_code=status_code,
                response_body=response_data,
                request_url=url,
                request_params=params,
            )

        # Check for {"message": "...", "code": "404"} pattern
        if "message" in response_data and "code" in response_data:
            error_message = response_data["message"]
            error_code = response_data["code"]
            # Use the code from the body if it looks like an HTTP status
            with contextlib.suppress(ValueError, TypeError):
                status_code = int(error_code)
            raise IfpaApiError(
                message=error_message,
                status_code=status_code,
                response_body=response_data,
                request_url=url,
                request_params=params,
            )

    def _handle_http_error(
        self,
        exc: httpx.HTTPStatusError,
        url: str,
        params: dict[str, Any] | None,
    ) -> None:
        """Map httpx.HTTPStatusError to IfpaApiError with detailed information.

        Args:
            exc: The HTTPStatusError exception from httpx
            url: The full URL that was requested
            params: The query parameters sent with the request

        Raises:
            IfpaApiError: Always raises with appropriate error details
        """
        response = exc.response
        status_code = response.status_code

        # Try to extract error message from response body
        try:
            error_body = response.json()
            # Common error message fields in APIs
            error_message = (
                error_body.get("message")
                or error_body.get("error")
                or error_body.get("detail")
                or response.text
            )
        except ValueError:
            # Response is not JSON
            error_body = response.text
            error_message = response.text or f"HTTP {status_code} error"

        raise IfpaApiError(
            message=error_message,
            status_code=status_code,
            response_body=error_body,
            request_url=url,
            request_params=params,
        ) from exc

    async def close(self) -> None:
        """Close the underlying async client.

        This should be called when the client is no longer needed to properly
        clean up resources.
        """
        await self._client.aclose()

    async def __aenter__(self) -> "_AsyncHttpClient":
        """Support async context manager protocol."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close client when exiting async context manager."""
        await self.close()
