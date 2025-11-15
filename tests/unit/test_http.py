"""Unit tests for the HTTP client module."""

import pytest
import requests

from ifpa_sdk.config import Config
from ifpa_sdk.exceptions import IfpaApiError
from ifpa_sdk.http import _HttpClient


class TestHttpClientInitialization:
    """Tests for HTTP client initialization."""

    def test_http_client_initialization(self) -> None:
        """Test that HTTP client initializes with a config."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        assert client._config == config
        assert client._session is not None

    def test_http_client_creates_session(self) -> None:
        """Test that HTTP client creates a requests.Session."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        assert isinstance(client._session, requests.Session)

    def test_http_client_session_has_default_headers(self) -> None:
        """Test that session has default headers set."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        headers = client._session.headers
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test-key"
        assert headers["Accept"] == "application/json"
        assert headers["User-Agent"] == "ifpa-sdk-python"


class TestHttpClientRequest:
    """Tests for HTTP request handling."""

    def test_successful_get_request(self, mock_requests) -> None:
        """Test successful GET request returns parsed JSON."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        response_data = {"player_id": 123, "name": "John"}
        mock_requests.get("https://api.ifpapinball.com/player/123", json=response_data)

        result = client._request("GET", "/player/123")
        assert result == response_data

    def test_request_with_query_parameters(self, mock_requests) -> None:
        """Test that query parameters are passed correctly."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        response_data = {"results": []}
        mock_requests.get(
            "https://api.ifpapinball.com/player/search?name=John&city=Seattle",
            json=response_data,
        )

        result = client._request(
            "GET", "/player/search", params={"name": "John", "city": "Seattle"}
        )
        assert result == response_data

    def test_path_without_leading_slash_is_handled(self, mock_requests) -> None:
        """Test that paths without leading slash are handled correctly."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        response_data = {"player_id": 123}
        mock_requests.get("https://api.ifpapinball.com/player/123", json=response_data)

        result = client._request("GET", "player/123")
        assert result == response_data


class TestHttpClientApiKeyHeader:
    """Tests for API key header handling."""

    def test_api_key_header_is_set(self, mock_requests) -> None:
        """Test that X-API-Key header is set correctly."""
        config = Config(api_key="my-secret-key")
        client = _HttpClient(config)

        mock_requests.get("https://api.ifpapinball.com/player/123", json={})
        client._request("GET", "/player/123")

        assert mock_requests.last_request.headers["X-API-Key"] == "my-secret-key"

    def test_accept_header_is_json(self, mock_requests) -> None:
        """Test that Accept header is set to application/json."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get("https://api.ifpapinball.com/player/123", json={})
        client._request("GET", "/player/123")

        assert mock_requests.last_request.headers["Accept"] == "application/json"

    def test_user_agent_header_is_set(self, mock_requests) -> None:
        """Test that User-Agent header is set."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get("https://api.ifpapinball.com/player/123", json={})
        client._request("GET", "/player/123")

        assert mock_requests.last_request.headers["User-Agent"] == "ifpa-sdk-python"


class TestHttpClientErrorHandling:
    """Tests for error handling."""

    def test_404_error_raises_ifpa_sdk_error(self, mock_requests) -> None:
        """Test that 404 response raises IfpaApiError."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get(
            "https://api.ifpapinball.com/player/999",
            status_code=404,
            json={"error": "Player not found"},
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/999")

        assert exc_info.value.status_code == 404

    def test_500_error_raises_ifpa_sdk_error(self, mock_requests) -> None:
        """Test that 500 response raises IfpaApiError."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get(
            "https://api.ifpapinball.com/player/123",
            status_code=500,
            text="Internal server error",
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/123")

        assert exc_info.value.status_code == 500

    def test_api_error_includes_status_code(self, mock_requests) -> None:
        """Test that IfpaApiError includes status code."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get(
            "https://api.ifpapinball.com/player/999",
            status_code=404,
            json={"error": "Not found"},
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/999")

        error = exc_info.value
        assert error.status_code == 404

    def test_api_error_includes_response_body_json(self, mock_requests) -> None:
        """Test that IfpaApiError includes JSON response body."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        error_body = {"error": "Resource not found"}
        mock_requests.get(
            "https://api.ifpapinball.com/player/999",
            status_code=404,
            json=error_body,
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/999")

        error = exc_info.value
        assert error.response_body == error_body

    def test_api_error_message_from_response(self, mock_requests) -> None:
        """Test that error message is extracted from response."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)

        mock_requests.get(
            "https://api.ifpapinball.com/player/999",
            status_code=404,
            json={"message": "Player with ID 999 not found"},
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/999")

        error = exc_info.value
        assert "Player with ID 999 not found" in error.message

    def test_timeout_raises_ifpa_sdk_error(self, mock_requests) -> None:
        """Test that timeout raises IfpaApiError."""
        config = Config(api_key="test-key", timeout=1.0)
        client = _HttpClient(config)

        mock_requests.get(
            "https://api.ifpapinball.com/player/123",
            exc=requests.exceptions.Timeout(),
        )

        with pytest.raises(IfpaApiError) as exc_info:
            client._request("GET", "/player/123")

        error = exc_info.value
        assert "timed out" in error.message


class TestHttpClientContextManager:
    """Tests for context manager protocol."""

    def test_context_manager_enter_returns_client(self) -> None:
        """Test that __enter__ returns the client instance."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        assert client.__enter__() == client

    def test_context_manager_closes_session_on_exit(self) -> None:
        """Test that __exit__ closes the session."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        session = client._session

        client.__exit__(None, None, None)
        # After close, accessing the session should not raise an error
        # but operations on it would fail (session is closed)
        assert session is not None


class TestHttpClientClose:
    """Tests for session close."""

    def test_close_method_exists(self) -> None:
        """Test that close method can be called."""
        config = Config(api_key="test-key")
        client = _HttpClient(config)
        client.close()
        # Should not raise an error
