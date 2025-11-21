"""Integration tests for Async Tournament resource.

This test suite performs integration testing of async Tournament resource methods
against the live IFPA API. These tests verify that async tournament operations work
correctly with real API calls.

Test fixtures use known IFPA tournaments:
- IFPA State Championship Series (54321): Large recurring series
- PAPA World Championship (various IDs): Major pinball event
- Idaho Pinball Museum events: Reliable test data

These tests make real API calls and require a valid API key.
Run with: pytest -m integration -m asyncio
"""

import pytest

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import TournamentNotLeagueError
from ifpa_api.models.tournaments import (
    Tournament,
    TournamentFormatsListResponse,
    TournamentSearchResponse,
)
from ifpa_api.resources.tournament.async_client import AsyncTournamentClient
from tests.integration.helpers import skip_if_no_api_key

# Test tournament IDs - using reliable, large tournaments
TOURNAMENT_PAPA_2023 = 94123  # PAPA World Championship 2023
TOURNAMENT_PINGOLF_BOISE = 70337  # Idaho Pinball Museum event
TOURNAMENT_LARGE_EVENT = 54321  # IFPA State Championship


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncTournamentClientIntegration:
    """Integration tests for AsyncTournamentClient methods."""

    async def test_tournament_get(self, api_key: str) -> None:
        """Test async get() method with real API."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            tournament = await client.get(TOURNAMENT_PAPA_2023)

            assert isinstance(tournament, Tournament)
            assert tournament.tournament_id == TOURNAMENT_PAPA_2023
            assert tournament.tournament_name is not None

    async def test_tournament_get_or_none_found(self, api_key: str) -> None:
        """Test get_or_none returns tournament when found."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            tournament = await client.get_or_none(TOURNAMENT_PINGOLF_BOISE)

            assert tournament is not None
            assert tournament.tournament_id == TOURNAMENT_PINGOLF_BOISE

    async def test_tournament_get_or_none_not_found(self, api_key: str) -> None:
        """Test get_or_none returns None when tournament doesn't exist."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            tournament = await client.get_or_none(99999999)

            assert tournament is None

    async def test_tournament_exists_true(self, api_key: str) -> None:
        """Test exists returns True for valid tournament."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            exists = await client.exists(TOURNAMENT_PAPA_2023)

            assert exists is True

    async def test_tournament_exists_false(self, api_key: str) -> None:
        """Test exists returns False for non-existent tournament."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            exists = await client.exists(99999999)

            assert exists is False

    async def test_tournament_search(self, api_key: str) -> None:
        """Test async search() query builder."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            results = await client.search("PAPA").limit(10).get()

            assert isinstance(results, TournamentSearchResponse)
            assert len(results.tournaments) > 0
            # Note: API ignores count parameter and returns 50-result pages
            assert len(results.tournaments) == 50
            # Should find PAPA tournaments
            assert any("PAPA" in t.tournament_name for t in results.tournaments)

    async def test_tournament_search_with_location(self, api_key: str) -> None:
        """Test search with location filters."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            results = await client.search().country("US").state("ID").limit(10).get()

            assert isinstance(results, TournamentSearchResponse)
            # Note: API ignores count parameter and returns 50-result pages
            assert len(results.tournaments) > 0
            # Should find Idaho tournaments
            if len(results.tournaments) > 0:
                assert any(t.stateprov == "ID" for t in results.tournaments)

    async def test_tournament_search_with_date_range(self, api_key: str) -> None:
        """Test search with date range filter."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            results = await (
                client.search("Championship").date_range("2023-01-01", "2023-12-31").limit(10).get()
            )

            assert isinstance(results, TournamentSearchResponse)
            # Note: API ignores count parameter and returns 50-result pages
            assert len(results.tournaments) > 0

    async def test_tournament_search_first(self, api_key: str) -> None:
        """Test search().first() returns single result."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            tournament = await client.search("PAPA").first()

            assert tournament is not None
            assert "PAPA" in tournament.tournament_name

    async def test_tournament_search_first_or_none(self, api_key: str) -> None:
        """Test search().first_or_none() returns result or None."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            # Should find results
            tournament = await client.search("PAPA").first_or_none()
            assert tournament is not None

            # Very unlikely name should return None
            no_result = await client.search("ZZZNonExistentTournamentXXX9999").first_or_none()
            assert no_result is None

    async def test_tournament_list_formats(self, api_key: str) -> None:
        """Test list_formats() returns format types."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            response = await client.list_formats()

            assert isinstance(response, TournamentFormatsListResponse)
            assert len(response.qualifying_formats) > 0
            assert len(response.finals_formats) > 0
            # Verify formats have names
            assert all(f.name for f in response.qualifying_formats)
            assert all(f.name for f in response.finals_formats)


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncTournamentContextIntegration:
    """Integration tests for AsyncTournamentContext methods."""

    async def test_tournament_context_details(self, api_key: str) -> None:
        """Test context details() method (deprecated)."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)
            tournament = await context.details()

            assert isinstance(tournament, Tournament)
            assert tournament.tournament_id == TOURNAMENT_PAPA_2023

    async def test_tournament_context_results(self, api_key: str) -> None:
        """Test context results() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)
            response = await context.results()

            # PAPA is a large tournament with many results
            assert len(response.results) > 0
            # Note: Some results may have None for player_name if data is incomplete
            # Just verify we got results back
            assert isinstance(response.results, list)

    async def test_tournament_context_formats(self, api_key: str) -> None:
        """Test context formats() method."""
        skip_if_no_api_key()
        import pytest

        from ifpa_api.core.exceptions import IfpaApiError

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)
            try:
                response = await context.formats()

                # Should have format information
                assert hasattr(response, "formats")
                assert len(response.formats) > 0
            except IfpaApiError as e:
                if e.status_code == 404:
                    pytest.skip("Tournament formats endpoint returns 404 for this tournament")
                raise

    async def test_tournament_context_submissions(self, api_key: str) -> None:
        """Test context submissions() method."""
        skip_if_no_api_key()
        import pytest

        from ifpa_api.core.exceptions import IfpaApiError

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)
            try:
                response = await context.submissions()

                # Should have submission data structure
                assert hasattr(response, "submissions")
            except IfpaApiError as e:
                if e.status_code == 404:
                    pytest.skip("Tournament submissions endpoint returns 404 for this tournament")
                raise

    async def test_tournament_context_related(self, api_key: str) -> None:
        """Test context related() method."""
        skip_if_no_api_key()
        import pytest

        from ifpa_api.core.exceptions import IfpaApiError

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)
            try:
                response = await context.related()

                # PAPA has many related tournaments (other years)
                assert hasattr(response, "tournament")
                # Should have other PAPA events
                assert len(response.tournament) > 0
            except IfpaApiError as e:
                if e.status_code == 404:
                    pytest.skip("Tournament related endpoint returns 404 for this tournament")
                raise

    async def test_tournament_context_league_not_league(self, api_key: str) -> None:
        """Test context league() raises error for non-league tournament."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncTournamentClient(http_client, validate_requests=False)

            context = client(TOURNAMENT_PAPA_2023)

            # PAPA is not a league, should raise TournamentNotLeagueError
            with pytest.raises(TournamentNotLeagueError):
                await context.league()
