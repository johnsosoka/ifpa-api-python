"""Unit tests for async director resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
)
from ifpa_api.resources.director.async_client import AsyncDirectorClient
from ifpa_api.resources.director.async_context import AsyncDirectorContext
from ifpa_api.resources.director.async_query_builder import AsyncDirectorQueryBuilder


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_director_client(async_http_client: _AsyncHttpClient) -> AsyncDirectorClient:
    """Create async director client for testing."""
    return AsyncDirectorClient(async_http_client, validate_requests=False)


# AsyncDirectorClient tests


@pytest.mark.asyncio
async def test_director_client_callable_returns_context(
    async_director_client: AsyncDirectorClient,
) -> None:
    """Test that calling director client returns AsyncDirectorContext."""
    context = async_director_client(1533)
    assert isinstance(context, AsyncDirectorContext)
    assert context._resource_id == 1533


@pytest.mark.asyncio
async def test_director_get(
    async_director_client: AsyncDirectorClient,
    respx_mock: Any,
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test AsyncDirectorClient.get() method."""
    director_data = {
        "director_id": 1533,
        "name": "Josh Sharpe",
        "city": "Chicago",
        "stateprov": "IL",
        "country_code": "US",
        "country_name": "United States",
    }

    respx_mock.get("https://api.ifpapinball.com/director/1533").mock(
        return_value=Response(200, json=director_data)
    )

    director = await async_director_client.get(1533)

    assert isinstance(director, Director)
    assert director.director_id == 1533
    assert director.name == "Josh Sharpe"


@pytest.mark.asyncio
async def test_director_get_or_none_found(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test get_or_none when director exists."""
    director_data = {
        "director_id": 1533,
        "name": "Josh Sharpe",
        "city": "Chicago",
        "stateprov": "IL",
        "country_code": "US",
        "country_name": "United States",
    }

    respx_mock.get("https://api.ifpapinball.com/director/1533").mock(
        return_value=Response(200, json=director_data)
    )

    director = await async_director_client.get_or_none(1533)

    assert director is not None
    assert director.name == "Josh Sharpe"


@pytest.mark.asyncio
async def test_director_get_or_none_not_found(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test get_or_none when director doesn't exist (404)."""
    respx_mock.get("https://api.ifpapinball.com/director/99999").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    director = await async_director_client.get_or_none(99999)

    assert director is None


@pytest.mark.asyncio
async def test_director_exists_true(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test exists() returns True when director exists."""
    director_data = {
        "director_id": 1533,
        "name": "Josh Sharpe",
        "city": "Chicago",
        "stateprov": "IL",
        "country_code": "US",
        "country_name": "United States",
    }

    respx_mock.get("https://api.ifpapinball.com/director/1533").mock(
        return_value=Response(200, json=director_data)
    )

    exists = await async_director_client.exists(1533)

    assert exists is True


@pytest.mark.asyncio
async def test_director_exists_false(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test exists() returns False when director doesn't exist."""
    respx_mock.get("https://api.ifpapinball.com/director/99999").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    exists = await async_director_client.exists(99999)

    assert exists is False


@pytest.mark.asyncio
async def test_director_search_returns_query_builder(
    async_director_client: AsyncDirectorClient,
) -> None:
    """Test search() returns AsyncDirectorQueryBuilder."""
    builder = async_director_client.search("Josh")
    assert isinstance(builder, AsyncDirectorQueryBuilder)


@pytest.mark.asyncio
async def test_director_country_directors(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test country_directors() method."""
    country_dirs_data = {
        "country_directors": [
            {
                "player_profile": {
                    "player_id": 1533,
                    "name": "Josh Sharpe",
                    "country_code": "US",
                    "country_name": "United States",
                }
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/country").mock(
        return_value=Response(200, json=country_dirs_data)
    )

    response = await async_director_client.country_directors()

    assert isinstance(response, CountryDirectorsResponse)
    assert len(response.country_directors) == 1
    assert response.country_directors[0].player_profile.name == "Josh Sharpe"


# AsyncDirectorContext tests


@pytest.mark.asyncio
async def test_director_context_details(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test context details() method (deprecated)."""
    director_data = {
        "director_id": 1533,
        "name": "Josh Sharpe",
        "city": "Chicago",
        "stateprov": "IL",
        "country_code": "US",
        "country_name": "United States",
    }

    respx_mock.get("https://api.ifpapinball.com/director/1533").mock(
        return_value=Response(200, json=director_data)
    )

    context = async_director_client(1533)
    director = await context.details()

    assert isinstance(director, Director)
    assert director.director_id == 1533


@pytest.mark.asyncio
async def test_director_context_tournaments(
    async_director_client: AsyncDirectorClient, respx_mock: Any
) -> None:
    """Test context tournaments() method."""
    tournaments_data = {
        "tournaments": [
            {
                "tournament_id": 12345,
                "tournament_name": "Test Tournament",
                "event_date": "2024-01-15",
                "city": "Chicago",
                "state": "IL",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/1533/tournaments/past").mock(
        return_value=Response(200, json=tournaments_data)
    )

    context = async_director_client(1533)
    response = await context.tournaments(TimePeriod.PAST)

    assert len(response.tournaments) == 1
    assert response.tournaments[0].tournament_name == "Test Tournament"


# AsyncDirectorQueryBuilder tests


@pytest.mark.asyncio
async def test_director_query_builder_query(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder query() method."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.query("Josh")

    assert new_builder is not builder  # immutability
    assert new_builder._params["name"] == "Josh"


@pytest.mark.asyncio
async def test_director_query_builder_country(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder country() filter."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.country("US")

    assert new_builder is not builder
    assert new_builder._params["country"] == "US"


@pytest.mark.asyncio
async def test_director_query_builder_state(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder state() filter."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.state("IL")

    assert new_builder is not builder
    assert new_builder._params["stateprov"] == "IL"


@pytest.mark.asyncio
async def test_director_query_builder_city(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder city() filter."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.city("Chicago")

    assert new_builder is not builder
    assert new_builder._params["city"] == "Chicago"


@pytest.mark.asyncio
async def test_director_query_builder_limit(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder limit() pagination."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.limit(25)

    assert new_builder is not builder
    assert new_builder._params["count"] == 25


@pytest.mark.asyncio
async def test_director_query_builder_offset(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder offset() pagination."""
    builder = AsyncDirectorQueryBuilder(async_http_client)
    new_builder = builder.offset(50)

    assert new_builder is not builder
    assert new_builder._params["start_pos"] == 51  # 0-based to 1-based conversion


@pytest.mark.asyncio
async def test_director_query_builder_get(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder get() execution."""
    search_data = {
        "directors": [
            {
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Chicago",
                "stateprov": "IL",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)
    results = await builder.query("Josh").get()

    assert isinstance(results, DirectorSearchResponse)
    assert len(results.directors) == 1
    assert results.directors[0].name == "Josh Sharpe"


@pytest.mark.asyncio
async def test_director_query_builder_first(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first() method."""
    search_data = {
        "directors": [
            {
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Chicago",
                "stateprov": "IL",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)
    director = await builder.query("Josh").first()

    assert director.name == "Josh Sharpe"


@pytest.mark.asyncio
async def test_director_query_builder_first_no_results(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first() with no results raises IndexError."""
    search_data: dict[str, Any] = {"directors": []}

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)

    with pytest.raises(IndexError, match="Search returned no results"):
        await builder.query("NonExistent").first()


@pytest.mark.asyncio
async def test_director_query_builder_first_or_none(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() method."""
    search_data = {
        "directors": [
            {
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Chicago",
                "stateprov": "IL",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)
    director = await builder.query("Josh").first_or_none()

    assert director is not None
    assert director.name == "Josh Sharpe"


@pytest.mark.asyncio
async def test_director_query_builder_first_or_none_no_results(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() with no results returns None."""
    search_data: dict[str, Any] = {"directors": []}

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)
    director = await builder.query("NonExistent").first_or_none()

    assert director is None


@pytest.mark.asyncio
async def test_director_query_builder_chaining(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder method chaining."""
    search_data = {
        "directors": [
            {
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Chicago",
                "stateprov": "IL",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/director/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncDirectorQueryBuilder(async_http_client)
    results = await builder.query("Josh").country("US").state("IL").limit(10).get()

    assert isinstance(results, DirectorSearchResponse)
    assert len(results.directors) == 1
