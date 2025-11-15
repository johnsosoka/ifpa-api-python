"""Unit tests for the config module."""

from typing import Any

import pytest

from ifpa_sdk.config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, Config
from ifpa_sdk.exceptions import MissingApiKeyError


class TestConfigApiKeyResolution:
    """Tests for API key resolution."""

    def test_api_key_from_constructor(self) -> None:
        """Test that API key is used from constructor when provided."""
        api_key = "test-key-12345"
        config = Config(api_key=api_key)
        assert config.api_key == api_key

    def test_api_key_from_environment_variable(self, monkeypatch: Any) -> None:
        """Test that API key is read from environment variable."""
        api_key = "env-key-54321"
        monkeypatch.setenv("IFPA_API_KEY", api_key)
        config = Config()
        assert config.api_key == api_key

    def test_constructor_api_key_takes_precedence(self, monkeypatch: Any) -> None:
        """Test that constructor API key takes precedence over environment."""
        constructor_key = "constructor-key"
        env_key = "env-key"
        monkeypatch.setenv("IFPA_API_KEY", env_key)
        config = Config(api_key=constructor_key)
        assert config.api_key == constructor_key

    def test_missing_api_key_raises_error(self, monkeypatch: Any) -> None:
        """Test that MissingApiKeyError is raised when no key is available."""
        monkeypatch.delenv("IFPA_API_KEY", raising=False)
        with pytest.raises(MissingApiKeyError):
            Config()

    def test_missing_api_key_error_message(self, monkeypatch: Any) -> None:
        """Test that MissingApiKeyError has helpful message."""
        monkeypatch.delenv("IFPA_API_KEY", raising=False)
        with pytest.raises(MissingApiKeyError) as exc_info:
            Config()
        assert "IFPA_API_KEY" in str(exc_info.value)


class TestConfigBaseUrl:
    """Tests for base URL configuration."""

    def test_default_base_url(self) -> None:
        """Test that default base URL is used when not provided."""
        config = Config(api_key="test-key")
        assert config.base_url == DEFAULT_BASE_URL

    def test_custom_base_url(self) -> None:
        """Test that custom base URL can be provided."""
        custom_url = "https://custom.example.com"
        config = Config(api_key="test-key", base_url=custom_url)
        assert config.base_url == custom_url

    def test_base_url_trailing_slash_removed(self) -> None:
        """Test that trailing slashes are removed from base URL."""
        config = Config(api_key="test-key", base_url="https://api.example.com/")
        assert config.base_url == "https://api.example.com"

    def test_base_url_multiple_trailing_slashes_removed(self) -> None:
        """Test that all trailing slashes are removed from base URL."""
        config = Config(api_key="test-key", base_url="https://api.example.com///")
        assert config.base_url == "https://api.example.com"


class TestConfigTimeout:
    """Tests for timeout configuration."""

    def test_default_timeout(self) -> None:
        """Test that default timeout is used when not provided."""
        config = Config(api_key="test-key")
        assert config.timeout == DEFAULT_TIMEOUT

    def test_custom_timeout(self) -> None:
        """Test that custom timeout can be provided."""
        timeout = 30.0
        config = Config(api_key="test-key", timeout=timeout)
        assert config.timeout == timeout

    def test_timeout_value_types(self) -> None:
        """Test that timeout accepts both int and float."""
        int_config = Config(api_key="test-key", timeout=5)
        assert int_config.timeout == 5

        float_config = Config(api_key="test-key", timeout=5.5)
        assert float_config.timeout == 5.5


class TestConfigValidateRequests:
    """Tests for request validation configuration."""

    def test_validate_requests_default_true(self) -> None:
        """Test that validate_requests defaults to True."""
        config = Config(api_key="test-key")
        assert config.validate_requests is True

    def test_validate_requests_can_be_disabled(self) -> None:
        """Test that validate_requests can be set to False."""
        config = Config(api_key="test-key", validate_requests=False)
        assert config.validate_requests is False

    def test_validate_requests_can_be_enabled(self) -> None:
        """Test that validate_requests can be explicitly set to True."""
        config = Config(api_key="test-key", validate_requests=True)
        assert config.validate_requests is True


class TestConfigIntegration:
    """Integration tests for config settings."""

    def test_all_settings_together(self) -> None:
        """Test that all settings can be configured together."""
        config = Config(
            api_key="my-key",
            base_url="https://custom.api.com",
            timeout=20.0,
            validate_requests=False,
        )
        assert config.api_key == "my-key"
        assert config.base_url == "https://custom.api.com"
        assert config.timeout == 20.0
        assert config.validate_requests is False

    def test_minimal_config_with_environment_key(self, monkeypatch: Any) -> None:
        """Test minimal config relying on environment variable."""
        monkeypatch.setenv("IFPA_API_KEY", "env-key")
        config = Config()
        assert config.api_key == "env-key"
        assert config.base_url == DEFAULT_BASE_URL
        assert config.timeout == DEFAULT_TIMEOUT
        assert config.validate_requests is True
