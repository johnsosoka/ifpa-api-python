"""Low-level HTTP client for the IFPA API.

This module provides the internal HTTP client that handles request/response
cycles, authentication, error mapping, and session management.
"""

from typing import Any

import requests

from ifpa_api.config import Config
from ifpa_api.exceptions import IfpaApiError


class _HttpClient:
    """Internal HTTP client for making requests to the IFPA API.

    This class is not part of the public API and should only be used internally
    by resource clients and handles. It manages the underlying requests.Session,
    handles authentication, and maps HTTP errors to SDK exceptions.

    Attributes:
        _config: The configuration object containing API key, base URL, etc.
        _session: The requests.Session used for all HTTP calls
    """

    def __init__(self, config: Config) -> None:
        """Initialize the HTTP client.

        Args:
            config: Configuration object with API key, base URL, and settings
        """
        self._config = config
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure a requests.Session with default headers.

        Returns:
            A configured requests.Session instance
        """
        session = requests.Session()
        session.headers.update(
            {
                "X-API-Key": self._config.api_key,
                "Accept": "application/json",
                "User-Agent": "ifpa-api-python",
            }
        )
        return session

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP request to the IFPA API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (e.g., "/player/123")
            params: Optional query parameters
            json: Optional JSON request body

        Returns:
            The parsed JSON response as a dict

        Raises:
            IfpaApiError: If the API returns a non-2xx status code
            requests.RequestException: For network-level errors
        """
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"

        url = f"{self._config.base_url}{path}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                timeout=self._config.timeout,
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse and return JSON response
            return response.json()

        except requests.exceptions.HTTPError as exc:
            # Map HTTP errors to IfpaApiError
            self._handle_http_error(exc)
        except requests.exceptions.Timeout as exc:
            raise IfpaApiError(
                message=f"Request timed out after {self._config.timeout} seconds",
                status_code=None,
                response_body=None,
            ) from exc
        except requests.exceptions.RequestException as exc:
            # Network errors, connection errors, etc.
            raise IfpaApiError(
                message=f"Request failed: {str(exc)}",
                status_code=None,
                response_body=None,
            ) from exc

    def _handle_http_error(self, exc: requests.exceptions.HTTPError) -> None:
        """Map requests.HTTPError to IfpaApiError with detailed information.

        Args:
            exc: The HTTPError exception from requests

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
        ) from exc

    def close(self) -> None:
        """Close the underlying session.

        This should be called when the client is no longer needed to properly
        clean up resources.
        """
        self._session.close()

    def __enter__(self) -> "_HttpClient":
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close session when exiting context manager."""
        self.close()
