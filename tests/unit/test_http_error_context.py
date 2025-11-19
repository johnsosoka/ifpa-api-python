"""Unit tests for HTTP client error context propagation.

Tests that _HttpClient properly populates request_url and request_params
in all error scenarios.
"""

from typing import Any

import pytest
import requests

from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.core.http import _HttpClient


class TestHttpClientErrorContext:
    """Test that HTTP client populates request context in errors."""

    @pytest.fixture
    def http_client(self) -> _HttpClient:
        """Create an HTTP client instance for testing."""
        config = Config(api_key="test-key", base_url="https://api.ifpapinball.com")
        return _HttpClient(config)

    def test_http_error_includes_url_and_params(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that HTTP errors include request URL and params."""
        url = "https://api.ifpapinball.com/player/99999"
        requests_mock.get(url, status_code=404, json={"error": "Not found"})

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/player/99999", params={"count": 10})

        error = exc_info.value
        assert error.status_code == 404
        assert error.request_url == url
        assert error.request_params == {"count": 10}

    def test_null_response_includes_url_and_params(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that null response errors include request context."""
        url = "https://api.ifpapinball.com/player/99999"
        # Mock a response that returns None/null JSON
        requests_mock.get(url, status_code=200, text="null")

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/player/99999", params={"start_pos": 0})

        error = exc_info.value
        assert error.status_code == 404
        assert "null response" in error.message.lower()
        assert error.request_url == url
        assert error.request_params == {"start_pos": 0}

    def test_error_field_in_response_includes_context(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that error field in response includes request context."""
        url = "https://api.ifpapinball.com/test"
        requests_mock.get(url, status_code=200, json={"error": "Invalid request"})

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/test", params={"param": "value"})

        error = exc_info.value
        assert error.message == "Invalid request"
        assert error.request_url == url
        assert error.request_params == {"param": "value"}

    def test_timeout_error_includes_url_and_params(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that timeout errors include request context."""
        url = "https://api.ifpapinball.com/slow"
        requests_mock.get(url, exc=requests.exceptions.Timeout)

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/slow", params={"delay": 30})

        error = exc_info.value
        assert "timed out" in error.message.lower()
        assert error.status_code is None
        assert error.request_url == url
        assert error.request_params == {"delay": 30}

    def test_connection_error_includes_url_and_params(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that connection errors include request context."""
        url = "https://api.ifpapinball.com/unreachable"
        requests_mock.get(url, exc=requests.exceptions.ConnectionError)

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/unreachable", params={"retry": 3})

        error = exc_info.value
        assert "failed" in error.message.lower()
        assert error.status_code is None
        assert error.request_url == url
        assert error.request_params == {"retry": 3}

    def test_request_without_params(self, http_client: _HttpClient, requests_mock: Any) -> None:
        """Test error context when no query parameters provided."""
        url = "https://api.ifpapinball.com/player/99999"
        requests_mock.get(url, status_code=404)

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/player/99999")

        error = exc_info.value
        assert error.request_url == url
        assert error.request_params is None

    def test_message_code_error_includes_context(
        self, http_client: _HttpClient, requests_mock: Any
    ) -> None:
        """Test that message+code errors include request context."""
        url = "https://api.ifpapinball.com/test"
        requests_mock.get(
            url,
            status_code=200,
            json={"message": "Resource not found", "code": "404"},
        )

        with pytest.raises(IfpaApiError) as exc_info:
            http_client._request("GET", "/test", params={"id": 123})

        error = exc_info.value
        assert error.message == "Resource not found"
        assert error.status_code == 404
        assert error.request_url == url
        assert error.request_params == {"id": 123}

    def test_error_string_shows_url(self, http_client: _HttpClient, requests_mock: Any) -> None:
        """Test that error string representation includes URL."""
        url = "https://api.ifpapinball.com/player/99999"
        requests_mock.get(url, status_code=404, json={"error": "Not found"})

        try:
            http_client._request("GET", "/player/99999", params={"count": 10})
        except IfpaApiError as error:
            error_str = str(error)
            assert "(URL: https://api.ifpapinball.com/player/99999)" in error_str
            assert "[404]" in error_str
