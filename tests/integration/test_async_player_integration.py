"""Integration tests for Async Player resource.

This test suite performs integration testing of async Player resource methods
against the live IFPA API. These tests verify that async player operations work
correctly with real API calls.

NOTE: These tests require AsyncIfpaClient which is not yet implemented in v1.0.0.
They will be enabled once the main async client is complete.

Test fixtures use Idaho Pinball Museum community players:
- Dwayne Smith (25584): Highly active, rank #753, 433 events
- Debbie Smith (47585): Active, rank #7078, 81 active events
- Dave Fellows (52913): Active, rank #3303
- John Sosoka (50104): Low activity, rank #47572
- Anna Rigas (50106): Inactive since 2017

These tests make real API calls and require a valid API key.
Run with: pytest -m integration -m asyncio
"""

import pytest

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import PlayersNeverMetError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)
from ifpa_api.resources.player.async_client import AsyncPlayerClient
from tests.integration.helpers import skip_if_no_api_key

# Test player IDs from Idaho Pinball Museum community
PLAYER_HIGHLY_ACTIVE_ID = 25584  # Dwayne Smith: 753 rank, 433 events
PLAYER_ACTIVE_ID = 47585  # Debbie Smith: 7078 rank, 81 active events
PLAYER_ACTIVE_ID_2 = 52913  # Dave Fellows: 3303 rank
PLAYER_LOW_ACTIVITY_ID = 50104  # John Sosoka: 47572 rank
PLAYER_INACTIVE_ID = 50106  # Anna Rigas: inactive since 2017

# PVP test pairs
PVP_PAIR_PRIMARY = (25584, 47585)  # Dwayne & Debbie Smith (definitely met)
PVP_PAIR_NEVER_MET = (25584, 99999)  # Valid player vs non-existent


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncPlayerClientIntegration:
    """Integration tests for AsyncPlayerClient methods."""

    async def test_player_get(self, api_key: str) -> None:
        """Test async get() method with real API."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player = await client.get(PLAYER_HIGHLY_ACTIVE_ID)

            assert isinstance(player, Player)
            assert player.player_id == PLAYER_HIGHLY_ACTIVE_ID
            assert player.first_name is not None
            assert player.last_name is not None

    async def test_player_get_or_none_found(self, api_key: str) -> None:
        """Test get_or_none returns player when found."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player = await client.get_or_none(PLAYER_ACTIVE_ID)

            assert player is not None
            assert player.player_id == PLAYER_ACTIVE_ID

    async def test_player_get_or_none_not_found(self, api_key: str) -> None:
        """Test get_or_none returns None when player doesn't exist."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player = await client.get_or_none(99999999)

            assert player is None

    async def test_player_exists_true(self, api_key: str) -> None:
        """Test exists returns True for valid player."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            exists = await client.exists(PLAYER_ACTIVE_ID_2)

            assert exists is True

    async def test_player_exists_false(self, api_key: str) -> None:
        """Test exists returns False for non-existent player."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            exists = await client.exists(99999999)

            assert exists is False

    async def test_player_search(self, api_key: str) -> None:
        """Test async search() with query builder."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            results = await client.search("Smith").country("US").get()

            assert isinstance(results, PlayerSearchResponse)
            assert results.search is not None
            assert len(results.search) > 0

    async def test_player_search_first(self, api_key: str) -> None:
        """Test search with first() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player = await client.search("Sosoka").first()

            assert player is not None
            assert "Sosoka" in player.last_name

    async def test_player_search_first_or_none(self, api_key: str) -> None:
        """Test search with first_or_none() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            # Search for something that likely exists
            player = await client.search("Smith").country("US").first_or_none()
            assert player is not None

            # Search for something that doesn't exist
            no_player = await client.search("ZZZZZZZZZZZZZ").first_or_none()
            assert no_player is None


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncPlayerContextIntegration:
    """Integration tests for AsyncPlayerContext methods."""

    async def test_player_context_details(self, api_key: str) -> None:
        """Test async details() method (deprecated)."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            # Use deprecated callable pattern
            context = client(PLAYER_HIGHLY_ACTIVE_ID)
            player = await context.details()

            assert isinstance(player, Player)
            assert player.player_id == PLAYER_HIGHLY_ACTIVE_ID

    async def test_player_pvp_all(self, api_key: str) -> None:
        """Test async pvp_all() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            context = client(PLAYER_HIGHLY_ACTIVE_ID)
            result = await context.pvp_all()

            assert isinstance(result, PvpAllCompetitors)
            assert result.total_competitors > 0

    async def test_player_pvp_comparison(self, api_key: str) -> None:
        """Test async pvp() comparison between two players."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player1_id, player2_id = PVP_PAIR_PRIMARY
            context = client(player1_id)
            result = await context.pvp(player2_id)

            assert isinstance(result, PvpComparison)
            assert result.player1_id == player1_id
            assert result.player2_id == player2_id
            # Note: total_meetings may be None if API doesn't provide it
            # At minimum, verify we got a valid PvpComparison response
            assert result.player1_name is not None
            assert result.player2_name is not None

    async def test_player_pvp_never_met(self, api_key: str) -> None:
        """Test async pvp() raises PlayersNeverMetError for players who never met."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            player1_id, player2_id = PVP_PAIR_NEVER_MET
            context = client(player1_id)

            with pytest.raises(PlayersNeverMetError) as exc_info:
                await context.pvp(player2_id)

            assert exc_info.value.player_id == player1_id
            assert exc_info.value.opponent_id == player2_id

    async def test_player_results(self, api_key: str) -> None:
        """Test async results() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            context = client(PLAYER_HIGHLY_ACTIVE_ID)
            result = await context.results(RankingSystem.MAIN, ResultType.ACTIVE)

            assert isinstance(result, PlayerResultsResponse)
            assert result.player_id == PLAYER_HIGHLY_ACTIVE_ID
            assert len(result.results) > 0

    async def test_player_results_with_pagination(self, api_key: str) -> None:
        """Test async results() with pagination parameters."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            context = client(PLAYER_HIGHLY_ACTIVE_ID)
            result = await context.results(
                RankingSystem.MAIN, ResultType.ACTIVE, start_pos=0, count=10
            )

            assert isinstance(result, PlayerResultsResponse)
            # Note: API may return more results than count parameter suggests
            assert len(result.results) > 0

    async def test_player_history(self, api_key: str) -> None:
        """Test async history() method."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            context = client(PLAYER_HIGHLY_ACTIVE_ID)
            result = await context.history()

            assert isinstance(result, RankingHistory)
            assert result.player_id == PLAYER_HIGHLY_ACTIVE_ID
            # Active player should have rank history
            assert len(result.rank_history) > 0


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncPlayerQueryBuilderIntegration:
    """Integration tests for AsyncPlayerQueryBuilder."""

    async def test_query_builder_chained_filters(self, api_key: str) -> None:
        """Test query builder with multiple chained filters."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            results = await client.search("Smith").country("US").state("ID").limit(25).get()

            assert isinstance(results, PlayerSearchResponse)
            # Verify filters were applied (if results exist)
            if len(results.search) > 0:
                for player in results.search:
                    if player.country_code:
                        assert player.country_code == "US"

    async def test_query_builder_immutability(self, api_key: str) -> None:
        """Test query builder immutability pattern with real API."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            # Create base query
            base_query = client.search("Smith").country("US")

            # Create two derived queries
            wa_results = await base_query.state("WA").get()
            id_results = await base_query.state("ID").get()

            # Both should succeed without interfering with each other
            assert isinstance(wa_results, PlayerSearchResponse)
            assert isinstance(id_results, PlayerSearchResponse)

    async def test_query_builder_tournament_filter(self, api_key: str) -> None:
        """Test tournament filter in query builder."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            # Search for players who participated in PAPA tournaments
            results = await client.search().tournament("PAPA").limit(10).get()

            assert isinstance(results, PlayerSearchResponse)
            # Results may be empty if no matches, but shouldn't error

    async def test_query_builder_position_filter(self, api_key: str) -> None:
        """Test position filter in query builder."""
        skip_if_no_api_key()

        config = Config(api_key=api_key, base_url="https://api.ifpapinball.com", timeout=30)
        async with _AsyncHttpClient(config) as http_client:
            client = AsyncPlayerClient(http_client, validate_requests=False)

            # Search for players who won (1st place) in PAPA tournaments
            results = await client.search().tournament("PAPA").position(1).limit(10).get()

            assert isinstance(results, PlayerSearchResponse)
            # Results may be empty if no matches, but shouldn't error
