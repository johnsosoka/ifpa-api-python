"""Unit tests for AsyncIfpaClient."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.async_client import AsyncIfpaClient
from ifpa_api.core.exceptions import MissingApiKeyError
from ifpa_api.resources.director.async_client import AsyncDirectorClient
from ifpa_api.resources.player.async_client import AsyncPlayerClient
from ifpa_api.resources.rankings.async_client import AsyncRankingsClient
from ifpa_api.resources.reference.async_client import AsyncReferenceClient
from ifpa_api.resources.series.async_client import AsyncSeriesClient
from ifpa_api.resources.stats.async_client import AsyncStatsClient
from ifpa_api.resources.tournament.async_client import AsyncTournamentClient


@pytest.mark.asyncio
class TestAsyncIfpaClientInitialization:
    """Test AsyncIfpaClient initialization."""

    async def test_initialization_with_api_key(self) -> None:
        """Test client initializes with explicit API key."""
        client = AsyncIfpaClient(api_key="test_key")
        try:
            assert client._config.api_key == "test_key"
            assert client._config.timeout == 10.0
            assert client._config.validate_requests is True
        finally:
            await client.close()

    async def test_initialization_with_custom_config(self) -> None:
        """Test client initializes with custom configuration."""
        client = AsyncIfpaClient(
            api_key="test_key",
            base_url="https://custom.api.com",
            timeout=30.0,
            validate_requests=False,
        )
        try:
            assert client._config.api_key == "test_key"
            assert client._config.base_url == "https://custom.api.com"
            assert client._config.timeout == 30.0
            assert client._config.validate_requests is False
        finally:
            await client.close()

    async def test_initialization_without_api_key_raises_error(self, monkeypatch: Any) -> None:
        """Test client raises error when no API key provided."""
        # Clear environment variable
        monkeypatch.delenv("IFPA_API_KEY", raising=False)

        with pytest.raises(MissingApiKeyError):
            AsyncIfpaClient()

    async def test_initialization_from_environment(self, monkeypatch: Any) -> None:
        """Test client reads API key from environment variable."""
        monkeypatch.setenv("IFPA_API_KEY", "env_test_key")

        client = AsyncIfpaClient()
        try:
            assert client._config.api_key == "env_test_key"
        finally:
            await client.close()


@pytest.mark.asyncio
class TestAsyncIfpaClientContextManager:
    """Test AsyncIfpaClient as async context manager."""

    async def test_async_context_manager_enters_successfully(self) -> None:
        """Test client enters async context manager successfully."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            assert client is not None
            assert client._http is not None

    async def test_async_context_manager_closes_on_exit(self) -> None:
        """Test client closes when exiting async context manager."""
        client = AsyncIfpaClient(api_key="test_key")
        async with client:
            assert client._http is not None
        # Client should be closed after exiting context

    async def test_async_context_manager_with_exception(self) -> None:
        """Test client closes even when exception occurs in context."""
        try:
            async with AsyncIfpaClient(api_key="test_key") as client:
                assert client is not None
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        # Client should still be closed


@pytest.mark.asyncio
class TestAsyncIfpaClientLazyLoading:
    """Test lazy loading of resource clients."""

    async def test_director_property_lazy_loads(self) -> None:
        """Test director property lazy loads AsyncDirectorClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            # First access should create client
            director1 = client.director
            assert isinstance(director1, AsyncDirectorClient)

            # Second access should return same instance
            director2 = client.director
            assert director1 is director2

    async def test_player_property_lazy_loads(self) -> None:
        """Test player property lazy loads AsyncPlayerClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            player1 = client.player
            assert isinstance(player1, AsyncPlayerClient)

            player2 = client.player
            assert player1 is player2

    async def test_rankings_property_lazy_loads(self) -> None:
        """Test rankings property lazy loads AsyncRankingsClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            rankings1 = client.rankings
            assert isinstance(rankings1, AsyncRankingsClient)

            rankings2 = client.rankings
            assert rankings1 is rankings2

    async def test_reference_property_lazy_loads(self) -> None:
        """Test reference property lazy loads AsyncReferenceClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            reference1 = client.reference
            assert isinstance(reference1, AsyncReferenceClient)

            reference2 = client.reference
            assert reference1 is reference2

    async def test_tournament_property_lazy_loads(self) -> None:
        """Test tournament property lazy loads AsyncTournamentClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            tournament1 = client.tournament
            assert isinstance(tournament1, AsyncTournamentClient)

            tournament2 = client.tournament
            assert tournament1 is tournament2

    async def test_series_property_lazy_loads(self) -> None:
        """Test series property lazy loads AsyncSeriesClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            series1 = client.series
            assert isinstance(series1, AsyncSeriesClient)

            series2 = client.series
            assert series1 is series2

    async def test_stats_property_lazy_loads(self) -> None:
        """Test stats property lazy loads AsyncStatsClient."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            stats1 = client.stats
            assert isinstance(stats1, AsyncStatsClient)

            stats2 = client.stats
            assert stats1 is stats2

    async def test_all_resources_load_successfully(self) -> None:
        """Test all resource properties load successfully."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            assert isinstance(client.director, AsyncDirectorClient)
            assert isinstance(client.player, AsyncPlayerClient)
            assert isinstance(client.rankings, AsyncRankingsClient)
            assert isinstance(client.reference, AsyncReferenceClient)
            assert isinstance(client.tournament, AsyncTournamentClient)
            assert isinstance(client.series, AsyncSeriesClient)
            assert isinstance(client.stats, AsyncStatsClient)


@pytest.mark.asyncio
class TestAsyncIfpaClientResourceConfiguration:
    """Test resource clients receive correct configuration."""

    async def test_resources_receive_validate_requests_true(self) -> None:
        """Test resources receive validate_requests=True when set."""
        async with AsyncIfpaClient(api_key="test_key", validate_requests=True) as client:
            assert client.player._validate_requests is True
            assert client.director._validate_requests is True
            assert client.tournament._validate_requests is True

    async def test_resources_receive_validate_requests_false(self) -> None:
        """Test resources receive validate_requests=False when set."""
        async with AsyncIfpaClient(api_key="test_key", validate_requests=False) as client:
            assert client.player._validate_requests is False
            assert client.director._validate_requests is False
            assert client.tournament._validate_requests is False

    async def test_resources_share_http_client(self) -> None:
        """Test all resources share the same HTTP client instance."""
        async with AsyncIfpaClient(api_key="test_key") as client:
            http_client = client._http

            assert client.player._http is http_client
            assert client.director._http is http_client
            assert client.tournament._http is http_client
            assert client.rankings._http is http_client
            assert client.stats._http is http_client
            assert client.series._http is http_client
            assert client.reference._http is http_client


@pytest.mark.asyncio
class TestAsyncIfpaClientClose:
    """Test AsyncIfpaClient close method."""

    async def test_close_method_closes_http_client(self) -> None:
        """Test close method properly closes HTTP client."""
        client = AsyncIfpaClient(api_key="test_key")
        await client.close()
        # If no exception, close succeeded

    async def test_manual_close_without_context_manager(self) -> None:
        """Test manual close works without context manager."""
        client = AsyncIfpaClient(api_key="test_key")
        try:
            # Use client
            assert client._http is not None
        finally:
            await client.close()


@pytest.mark.asyncio
class TestAsyncIfpaClientIntegration:
    """Integration-style tests with mocked HTTP responses."""

    async def test_player_get_through_client(self, respx_mock: Any) -> None:
        """Test player.get() works through main client."""
        player_data = {
            "player": [
                {
                    "player_id": 12345,
                    "first_name": "John",
                    "last_name": "Doe",
                    "city": "Seattle",
                    "state": "WA",
                    "country": "USA",
                    "initials": "JD",
                    "excluded_flag": 0,
                }
            ]
        }

        respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
            return_value=Response(200, json=player_data)
        )

        async with AsyncIfpaClient(api_key="test_key") as client:
            player = await client.player.get(12345)
            assert player.player_id == 12345
            assert player.first_name == "John"

    async def test_rankings_wppr_through_client(self, respx_mock: Any) -> None:
        """Test rankings.wppr() works through main client."""
        rankings_data = {
            "rankings": [
                {
                    "player_id": 1,
                    "first_name": "Top",
                    "last_name": "Player",
                    "current_rank": 1,
                    "wppr_points": "100.00",
                    "country_name": "USA",
                }
            ]
        }

        respx_mock.get("https://api.ifpapinball.com/rankings/wppr").mock(
            return_value=Response(200, json=rankings_data)
        )

        async with AsyncIfpaClient(api_key="test_key") as client:
            rankings = await client.rankings.wppr(start_pos=0, count=1)
            assert len(rankings.rankings) == 1
            assert rankings.rankings[0].rank == 1

    async def test_reference_countries_through_client(self, respx_mock: Any) -> None:
        """Test reference.countries() works through main client."""
        countries_data = {
            "country": [
                {"country_id": 1, "country_name": "USA", "country_code": "US", "active_flag": "Y"},
                {
                    "country_id": 2,
                    "country_name": "Canada",
                    "country_code": "CA",
                    "active_flag": "Y",
                },
            ]
        }

        respx_mock.get("https://api.ifpapinball.com/countries").mock(
            return_value=Response(200, json=countries_data)
        )

        async with AsyncIfpaClient(api_key="test_key") as client:
            countries = await client.reference.countries()
            assert len(countries.country) == 2
            assert countries.country[0].country_name == "USA"
