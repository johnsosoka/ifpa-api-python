"""Integration tests for PlayersClient and PlayerHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

from typing import cast

import pytest
from pydantic import ValidationError

from ifpa_api.client import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerSearchResponse
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestPlayersClientIntegration:
    """Integration tests for PlayersClient."""

    def test_search_players(self, api_key: str, country_code: str, count_medium: int) -> None:
        """Test searching for players with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # API requires at least one search parameter
        result = client.players.search(country=country_code, count=count_medium)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None

    def test_search_players_with_filters(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test searching players with location filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(country=country_code, count=count_small)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        # If results exist, verify they match filter
        if len(result.search) > 0:
            for player in result.search:
                if player.country_code:
                    assert player.country_code == country_code

    def test_search_with_multiple_filters(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test search with multiple filter combinations."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test country + count combination
        result = client.players.search(country=country_code, count=count_small)
        assert isinstance(result.search, list)
        # Verify result count respects the limit
        assert len(result.search) <= count_small

    def test_search_with_tournament_and_position(self, api_key: str, count_small: int) -> None:
        """Test search filtering by tournament and position.

        Searches for top finishers (position 1) in PAPA tournaments.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players with top finishes in PAPA tournaments
        result = client.players.search(tournament="PAPA", tourpos=1, count=count_small)
        assert isinstance(result.search, list)


@pytest.mark.integration
class TestPlayerHandleIntegration:
    """Integration tests for PlayerHandle."""

    def test_get_player(self, api_key: str, player_active_id: int) -> None:
        """Test getting player details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        from ifpa_api.models.player import Player

        # Use known test player fixture (active)
        player = client.player(player_active_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_active_id
        assert player.first_name is not None
        assert player.last_name is not None

    def test_player_results(self, api_key: str, player_active_id: int, count_small: int) -> None:
        """Test getting player tournament results with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use known test player fixture (active)
        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            count=count_small,
        )

        assert results.player_id == player_active_id
        assert results.results is not None

    def test_player_history(self, api_key: str, player_active_id: int) -> None:
        """Test getting player ranking history with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use known test player fixture (active, with history data)
        history = client.player(player_active_id).history()

        assert history.player_id == player_active_id
        assert hasattr(history, "rank_history")
        assert hasattr(history, "rating_history")
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)

    def test_pvp_all_integration(self, api_key: str, player_active_id: int) -> None:
        """Test pvp_all with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with known active player
        summary = client.player(player_active_id).pvp_all()
        assert summary.player_id == player_active_id
        assert isinstance(summary.total_competitors, int)
        assert summary.system is not None

    def test_get_multiple_integration(self, api_key: str, player_ids_multiple: list[int]) -> None:
        """Test get_multiple with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with multiple test players (active and inactive)
        result = client.players.get_multiple(cast(list[int | str], player_ids_multiple))
        assert result.player is not None
        # Verify we got a list of players
        if isinstance(result.player, list):
            assert len(result.player) == len(player_ids_multiple)
            assert all(p.player_id in player_ids_multiple for p in result.player)

    def test_search_with_tournament_integration(self, api_key: str, count_small: int) -> None:
        """Test search with tournament parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players in PAPA tournaments
        result = client.players.search(tournament="PAPA", count=count_small)
        assert isinstance(result.search, list)

    def test_history_structure_integration(self, api_key: str, player_active_id: int) -> None:
        """Test history returns correct structure with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with player fixture (has history data)
        history = client.player(player_active_id).history()

        # Verify dual-array structure
        assert hasattr(history, "rank_history")
        assert hasattr(history, "rating_history")
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)
        assert history.system is not None
        assert history.active_flag in ["Y", "N"]

    def test_get_player_not_found(self, api_key: str) -> None:
        """Test that getting non-existent player raises appropriate error.

        Uses a very high player ID that is extremely unlikely to exist.
        The API returns None for non-existent players, which Pydantic
        validates as an error.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist - API returns None which fails validation
        with pytest.raises(ValidationError):
            client.player(99999999).get()

    def test_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test getting an inactive player still returns valid data."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get inactive player - should still work
        player = client.player(player_inactive_id).get()

        assert player.player_id == player_inactive_id
        assert player is not None
