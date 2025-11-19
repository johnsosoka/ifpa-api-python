"""Configuration management for the IFPA SDK.

This module handles API key resolution, base URL configuration, and other
client settings.
"""

import os
from typing import Final

# Default configuration values
DEFAULT_BASE_URL: Final[str] = "https://api.ifpapinball.com"
DEFAULT_TIMEOUT: Final[float] = 10.0
API_KEY_ENV_VAR: Final[str] = "IFPA_API_KEY"


class Config:
    """Configuration container for IFPA API client settings.

    Attributes:
        api_key: The API key for authentication (resolved from constructor or environment)
        base_url: The base URL for the IFPA API
        timeout: Request timeout in seconds
        validate_requests: Whether to validate request parameters using Pydantic models
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        validate_requests: bool = True,
    ) -> None:
        """Initialize configuration settings.

        Args:
            api_key: Optional API key. If not provided, will attempt to read from
                IFPA_API_KEY environment variable.
            base_url: Optional base URL override. Defaults to DEFAULT_BASE_URL.
            timeout: Request timeout in seconds. Defaults to 10.0.
            validate_requests: Whether to validate request parameters. Defaults to True.

        Raises:
            MissingApiKeyError: If no API key is provided and IFPA_API_KEY env var is not set.
        """
        self.api_key = self._resolve_api_key(api_key)
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.validate_requests = validate_requests

    def _resolve_api_key(self, api_key: str | None) -> str:
        """Resolve API key from constructor argument or environment variable.

        Resolution order:
        1. Constructor argument (if provided)
        2. IFPA_API_KEY environment variable
        3. Raise MissingApiKeyError if neither is available

        Args:
            api_key: The API key provided to constructor, or None

        Returns:
            The resolved API key string

        Raises:
            MissingApiKeyError: If no API key can be resolved
        """
        # Import here to avoid circular dependency
        from ifpa_api.core.exceptions import MissingApiKeyError

        if api_key is not None:
            return api_key

        env_key = os.environ.get(API_KEY_ENV_VAR)
        if env_key is not None:
            return env_key

        raise MissingApiKeyError(
            f"No API key provided. Either pass api_key to the constructor "
            f"or set the {API_KEY_ENV_VAR} environment variable."
        )
