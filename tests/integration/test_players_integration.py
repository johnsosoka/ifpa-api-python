"""Integration tests for PlayersClient and PlayerHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.models.player import Player, PlayerSearchResponse
from tests.integration.helpers import get_test_player_id, skip_if_no_api_key


@pytest.mark.integration
class TestPlayersClientIntegration:
    """Integration tests for PlayersClient."""

    def test_search_players(self, api_key: str) -> None:
        """Test searching for players with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(count=10)

        assert isinstance(result, PlayerSearchResponse)
        assert result.players is not None

    def test_search_players_with_filters(self, api_key: str) -> None:
        """Test searching players with location filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(country="US", count=5)

        assert isinstance(result, PlayerSearchResponse)
        assert result.players is not None
        # If results exist, verify they match filter
        if len(result.players) > 0:
            for player in result.players:
                if player.country_code:
                    assert player.country_code == "US"


@pytest.mark.integration
class TestPlayerHandleIntegration:
    """Integration tests for PlayerHandle."""

    def test_get_player(self, api_key: str) -> None:
        """Test getting player details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player_id = get_test_player_id(client)
        if player_id is None:
            pytest.skip("Could not find test player")

        player = client.player(player_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_id
        assert player.first_name is not None
        assert player.last_name is not None

    def test_player_rankings(self, api_key: str) -> None:
        """Test getting player rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player_id = get_test_player_id(client)
        if player_id is None:
            pytest.skip("Could not find test player")

        rankings = client.player(player_id).rankings()

        assert isinstance(rankings, list)
        # Should have at least one ranking system
        if len(rankings) > 0:
            assert "ranking_system" in rankings[0] or "system" in rankings[0]

    def test_player_results(self, api_key: str) -> None:
        """Test getting player tournament results with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player_id = get_test_player_id(client)
        if player_id is None:
            pytest.skip("Could not find test player")

        results = client.player(player_id).results(count=5)

        assert results.player_id == player_id
        assert results.results is not None

    def test_player_history(self, api_key: str) -> None:
        """Test getting player ranking history with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player_id = get_test_player_id(client)
        if player_id is None:
            pytest.skip("Could not find test player")

        history = client.player(player_id).history()

        assert history.player_id == player_id
        assert history.history is not None
