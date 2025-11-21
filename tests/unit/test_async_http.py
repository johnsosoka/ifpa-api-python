"""Unit tests for the async HTTP client."""

from typing import Any

import httpx
import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import IfpaApiError


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.mark.asyncio
async def test_successful_request(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test successful GET request returns parsed JSON."""
    expected_data = {"player": [{"player_id": 12345, "first_name": "John"}]}

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=expected_data)
    )

    result = await async_http_client._request("GET", "/player/12345")

    assert result == expected_data


@pytest.mark.asyncio
async def test_request_without_leading_slash(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test that path without leading slash is handled correctly."""
    expected_data = {"data": "test"}

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=expected_data)
    )

    result = await async_http_client._request("GET", "player/12345")

    assert result == expected_data


@pytest.mark.asyncio
async def test_request_with_query_params(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test request with query parameters."""
    expected_data = {"search": [{"player_id": 1}]}

    respx_mock.get(
        "https://api.ifpapinball.com/player/search", params={"q": "John", "count": "10"}
    ).mock(return_value=Response(200, json=expected_data))

    result = await async_http_client._request(
        "GET", "/player/search", params={"q": "John", "count": "10"}
    )

    assert result == expected_data


@pytest.mark.asyncio
async def test_http_404_error(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that 404 HTTP error is mapped to IfpaApiError."""
    error_body = {"error": "Player not found"}

    respx_mock.get("https://api.ifpapinball.com/player/99999").mock(
        return_value=Response(404, json=error_body)
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/99999")

    assert exc_info.value.status_code == 404
    assert "Player not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_http_500_error(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that 500 HTTP error is mapped to IfpaApiError."""
    error_body = {"error": "Internal server error"}

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(500, json=error_body)
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/12345")

    assert exc_info.value.status_code == 500
    assert "Internal server error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_timeout_error(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that timeout errors are wrapped in IfpaApiError."""
    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        side_effect=httpx.TimeoutException("Request timed out")
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/12345")

    assert exc_info.value.status_code is None
    assert "timed out after" in str(exc_info.value)


@pytest.mark.asyncio
async def test_network_error(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that network errors are wrapped in IfpaApiError."""
    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        side_effect=httpx.RequestError("Connection failed")
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/12345")

    assert exc_info.value.status_code is None
    assert "Request failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_null_response_error(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that null responses are detected and raise IfpaApiError."""
    respx_mock.get("https://api.ifpapinball.com/player/99999").mock(
        return_value=Response(200, json=None)
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/99999")

    assert exc_info.value.status_code == 404
    assert "null response" in str(exc_info.value)


@pytest.mark.asyncio
async def test_response_error_field(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test that error field in 200 response is detected."""
    error_response = {"error": "Invalid player ID"}

    respx_mock.get("https://api.ifpapinball.com/player/abc").mock(
        return_value=Response(200, json=error_response)
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/abc")

    assert "Invalid player ID" in str(exc_info.value)


@pytest.mark.asyncio
async def test_response_message_code_pattern(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test that message+code error pattern in response is detected."""
    error_response = {"message": "Not found", "code": "404"}

    respx_mock.get("https://api.ifpapinball.com/player/99999").mock(
        return_value=Response(200, json=error_response)
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/99999")

    assert exc_info.value.status_code == 404
    assert "Not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_non_json_error_response(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test that non-JSON error responses are handled."""
    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(500, text="Internal Server Error")
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/12345")

    assert exc_info.value.status_code == 500
    assert "Internal Server Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test async context manager usage."""
    config = Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)

    async with _AsyncHttpClient(config) as client:
        assert client._client is not None

    # Client should be closed after context manager exit
    # httpx AsyncClient doesn't have is_closed, but we verify no exception


@pytest.mark.asyncio
async def test_manual_close() -> None:
    """Test manual close of async client."""
    config = Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)
    client = _AsyncHttpClient(config)

    assert client._client is not None

    await client.close()

    # Verify no exception on close


@pytest.mark.asyncio
async def test_client_initialization() -> None:
    """Test that client is properly initialized with config."""
    config = Config(api_key="my-api-key", base_url="https://api.ifpapinball.com", timeout=60)
    client = _AsyncHttpClient(config)

    assert client._config == config
    assert client._client is not None
    assert client._client.base_url == "https://api.ifpapinball.com"
    assert client._client.timeout.read == 60
    assert client._client.headers["X-API-Key"] == "my-api-key"
    assert client._client.headers["Accept"] == "application/json"
    assert client._client.headers["User-Agent"] == "ifpa-api-python"

    await client.close()


@pytest.mark.asyncio
async def test_error_includes_request_details(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test that errors include full request details for debugging."""
    respx_mock.get("https://api.ifpapinball.com/player/search").mock(
        return_value=Response(400, json={"error": "Bad request"})
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_http_client._request("GET", "/player/search", params={"q": "test"})

    error = exc_info.value
    assert error.request_url == "https://api.ifpapinball.com/player/search"
    assert error.request_params == {"q": "test"}
    assert error.response_body == {"error": "Bad request"}


@pytest.mark.asyncio
async def test_post_request_with_json_body(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test POST request with JSON body."""
    request_body = {"name": "Test Tournament"}
    response_data = {"tournament_id": 12345}

    respx_mock.post("https://api.ifpapinball.com/tournament").mock(
        return_value=Response(201, json=response_data)
    )

    result = await async_http_client._request("POST", "/tournament", json=request_body)

    assert result == response_data
