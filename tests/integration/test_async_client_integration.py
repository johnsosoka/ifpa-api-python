"""Integration tests for AsyncIfpaClient with real API."""

import pytest

from ifpa_api.async_client import AsyncIfpaClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncIfpaClientIntegration:
    """Integration tests for AsyncIfpaClient against real IFPA API."""

    async def test_async_context_manager_with_real_api(
        self, async_ifpa_client: AsyncIfpaClient
    ) -> None:
        """Test async context manager works with real API."""
        async with async_ifpa_client as client:
            # Simple call to verify connection works
            countries = await client.reference.countries()
            assert len(countries.country) > 0

    async def test_player_get_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test player.get() works against real API."""
        async with async_ifpa_client as client:
            # Using a known player ID
            player = await client.player.get(1)
            assert player.player_id == 1
            assert player.first_name is not None

    async def test_player_search_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test player search works against real API."""
        async with async_ifpa_client as client:
            response = await client.player.search("Smith").get()
            # Check that we got search results containing "Smith" in the name
            assert len(response.search) > 0
            assert any("Smith" in p.last_name for p in response.search)

    async def test_rankings_wppr_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test rankings.wppr() works against real API."""
        async with async_ifpa_client as client:
            rankings = await client.rankings.wppr(count=10)
            assert len(rankings.rankings) > 0
            # Rankings should have rank field
            assert rankings.rankings[0].rank is not None

    async def test_reference_countries_integration(
        self, async_ifpa_client: AsyncIfpaClient
    ) -> None:
        """Test reference.countries() works against real API."""
        async with async_ifpa_client as client:
            countries = await client.reference.countries()
            assert len(countries.country) > 50  # Should have many countries
            # USA should be in the list
            assert any(c.country_code == "US" for c in countries.country)

    async def test_tournament_search_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test tournament search works against real API."""
        async with async_ifpa_client as client:
            response = await client.tournament.search("Pinball").get()
            assert len(response.tournaments) > 0

    async def test_director_search_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test director search works against real API."""
        async with async_ifpa_client as client:
            response = await client.director.search("Smith").get()
            assert len(response.directors) > 0

    async def test_series_list_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test series.list() works against real API."""
        async with async_ifpa_client as client:
            series_list = await client.series.list()
            assert len(series_list.series) > 0

    async def test_stats_overall_integration(self, async_ifpa_client: AsyncIfpaClient) -> None:
        """Test stats.overall() works against real API."""
        async with async_ifpa_client as client:
            stats = await client.stats.overall()
            assert stats.stats.overall_player_count > 100000  # IFPA has many players

    async def test_multiple_requests_in_same_session(
        self, async_ifpa_client: AsyncIfpaClient
    ) -> None:
        """Test multiple requests work in same session."""
        async with async_ifpa_client as client:
            # Multiple requests should reuse the same HTTP client
            player = await client.player.get(1)
            rankings = await client.rankings.wppr(count=5)
            countries = await client.reference.countries()

            assert player.player_id == 1
            assert len(rankings.rankings) > 0
            assert len(countries.country) > 0
