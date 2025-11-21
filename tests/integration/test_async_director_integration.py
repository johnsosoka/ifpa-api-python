"""Integration tests for Async Director resource.

This test suite performs integration testing of async Director resource methods
against the live IFPA API. These tests verify that async director operations work
correctly with real API calls.

Test fixtures use known IFPA directors:
- Josh Sharpe (1533): IFPA President, Chicago IL, 400+ tournaments
- Andreas Haugstrup Pedersen (90): Denmark director, many European tournaments
- Zach Sharpe (8817): Texas director, many US tournaments

These tests make real API calls and require a valid API key.
Run with: pytest -m integration -m asyncio
"""

import pytest

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)
from ifpa_api.resources.director.async_client import AsyncDirectorClient
from tests.integration.helpers import skip_if_no_api_key

# Test director IDs
DIRECTOR_JOSH_SHARPE = 1533  # IFPA President, Chicago IL
DIRECTOR_ANDREAS = 90  # Denmark director
DIRECTOR_ZACH_SHARPE = 8817  # Texas director


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncDirectorClientIntegration:
    """Integration tests for AsyncDirectorClient methods."""

    async def test_director_get(self, api_key: str) -> None:
        """Test async get() method with real API."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            director = await client.get(DIRECTOR_JOSH_SHARPE)

            assert isinstance(director, Director)
            assert director.director_id == DIRECTOR_JOSH_SHARPE
            assert director.name is not None

    async def test_director_get_or_none_found(self, api_key: str) -> None:
        """Test get_or_none returns director when found."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            director = await client.get_or_none(DIRECTOR_ANDREAS)

            assert director is not None
            assert director.director_id == DIRECTOR_ANDREAS

    async def test_director_get_or_none_not_found(self, api_key: str) -> None:
        """Test get_or_none returns None when director doesn't exist."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            director = await client.get_or_none(99999999)

            assert director is None

    async def test_director_exists_true(self, api_key: str) -> None:
        """Test exists returns True for valid director."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            exists = await client.exists(DIRECTOR_JOSH_SHARPE)

            assert exists is True

    async def test_director_exists_false(self, api_key: str) -> None:
        """Test exists returns False for non-existent director."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            exists = await client.exists(99999999)

            assert exists is False

    async def test_director_search(self, api_key: str) -> None:
        """Test async search() query builder."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            results = await client.search("Sharpe").get()

            assert isinstance(results, DirectorSearchResponse)
            assert len(results.directors) > 0
            # Should find Josh or Zach Sharpe
            assert any("Sharpe" in d.name for d in results.directors)

    async def test_director_search_with_filters(self, api_key: str) -> None:
        """Test search with location filters."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            results = await client.search("Sharpe").country("US").limit(10).get()

            assert isinstance(results, DirectorSearchResponse)
            # Note: API ignores count parameter and returns 50-result pages
            assert len(results.directors) > 0
            # Note: API may not respect country filter, just verify we got results
            assert results.directors[0].name is not None

    async def test_director_search_first(self, api_key: str) -> None:
        """Test search().first() returns single result."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            director = await client.search("Sharpe").first()

            assert director is not None
            assert "Sharpe" in director.name

    async def test_director_search_first_or_none(self, api_key: str) -> None:
        """Test search().first_or_none() returns result or None."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            # Should find results
            director = await client.search("Sharpe").first_or_none()
            assert director is not None

            # Very unlikely name should return None
            no_result = await client.search("ZZZNonExistentDirectorXXX").first_or_none()
            assert no_result is None

    async def test_director_country_directors(self, api_key: str) -> None:
        """Test country_directors() returns list."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            response = await client.country_directors()

            assert isinstance(response, CountryDirectorsResponse)
            assert len(response.country_directors) > 0
            # Should have US, Canada, etc.
            # Note: CountryDirector has nested player_profile structure
            countries = [d.player_profile.country_code for d in response.country_directors]
            assert "US" in countries


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncDirectorContextIntegration:
    """Integration tests for AsyncDirectorContext methods."""

    async def test_director_context_details(self, api_key: str) -> None:
        """Test context details() method (deprecated)."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            context = client(DIRECTOR_JOSH_SHARPE)
            director = await context.details()

            assert isinstance(director, Director)
            assert director.director_id == DIRECTOR_JOSH_SHARPE

    async def test_director_context_tournaments_past(self, api_key: str) -> None:
        """Test context tournaments() with past period."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            context = client(DIRECTOR_JOSH_SHARPE)
            response = await context.tournaments(TimePeriod.PAST)

            assert isinstance(response, DirectorTournamentsResponse)
            assert len(response.tournaments) > 0
            # Josh Sharpe has directed many tournaments
            assert all(t.tournament_name is not None for t in response.tournaments)

    async def test_director_context_tournaments_future(self, api_key: str) -> None:
        """Test context tournaments() with future period."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncDirectorClient(http_client, validate_requests=False)

            context = client(DIRECTOR_JOSH_SHARPE)
            response = await context.tournaments(TimePeriod.FUTURE)

            assert isinstance(response, DirectorTournamentsResponse)
            # May or may not have future tournaments, just check structure
            assert hasattr(response, "tournaments")
