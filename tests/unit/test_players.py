"""Unit tests for PlayersClient and PlayerHandle.

Tests the players resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.exceptions import IfpaApiError
from ifpa_sdk.models.common import RankingSystem, ResultType
from ifpa_sdk.models.player import (
    Player,
    PlayerCard,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpComparison,
    RankingHistory,
)


class TestPlayersClient:
    """Test cases for PlayersClient collection-level operations."""

    def test_search_with_name_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching players by name."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "players": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "city": "Seattle",
                        "stateprov": "WA",
                        "country_code": "US",
                        "wppr_rank": 100,
                        "wppr_value": 450.5,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(name="John")

        assert isinstance(result, PlayerSearchResponse)
        assert len(result.players) == 1
        assert result.players[0].player_id == 12345
        assert result.players[0].first_name == "John"
        assert result.players[0].last_name == "Smith"
        assert result.players[0].wppr_rank == 100

    def test_search_with_location_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching players by location."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "players": [
                    {
                        "player_id": 67890,
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "city": "Portland",
                        "stateprov": "OR",
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(city="Portland", stateprov="OR", country="US")

        assert len(result.players) == 1
        assert result.players[0].city == "Portland"

    def test_search_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching players with pagination parameters."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "players": [
                    {"player_id": i, "first_name": f"Player{i}", "last_name": "Test"}
                    for i in range(25)
                ],
                "total_results": 100,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(name="Test", start_pos=0, count=25)

        assert len(result.players) == 25
        assert result.total_results == 100

        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=25" in query

    def test_search_with_first_and_last_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching players by first and last name separately."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "players": [
                    {
                        "player_id": 11111,
                        "first_name": "Michael",
                        "last_name": "Jordan",
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(first_name="Michael", last_name="Jordan")

        assert len(result.players) == 1
        query = mock_requests.last_request.query
        assert "first_name=michael" in query
        assert "last_name=jordan" in query


class TestPlayerHandle:
    """Test cases for PlayerHandle resource-specific operations."""

    def test_get_player(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting a specific player's details."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            json={
                "player": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "city": "Seattle",
                        "stateprov": "WA",
                        "country_name": "United States",
                        "country_code": "US",
                        "profile_photo": "https://example.com/photo.jpg",
                        "initials": "JS",
                        "ifpa_registered": True,
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        player = client.player(12345).get()

        assert isinstance(player, Player)
        assert player.player_id == 12345
        assert player.first_name == "John"
        assert player.last_name == "Smith"
        assert player.city == "Seattle"
        assert player.initials == "JS"
        assert player.ifpa_registered is True

    def test_get_player_with_string_id(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that player ID can be a string."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            json={
                "player": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        player = client.player("12345").get()

        assert player.player_id == 12345

    def test_rankings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player rankings across systems."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/rankings",
            json=[
                {
                    "ranking_system": "Main",
                    "rank": 100,
                    "rating": 450.5,
                    "country_rank": 50,
                    "active_events": 10,
                },
                {
                    "ranking_system": "Women",
                    "rank": 25,
                    "rating": 380.2,
                    "country_rank": 10,
                    "active_events": 8,
                },
            ],
        )

        client = IfpaClient(api_key="test-key")
        rankings = client.player(12345).rankings()

        assert isinstance(rankings, list)
        assert len(rankings) == 2
        assert rankings[0]["ranking_system"] == "Main"
        assert rankings[0]["rank"] == 100
        assert rankings[1]["ranking_system"] == "Women"

    def test_pvp_comparison(self, mock_requests: requests_mock.Mocker) -> None:
        """Test head-to-head player comparison."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/pvp/67890",
            json={
                "player1_id": 12345,
                "player1_name": "John Smith",
                "player2_id": 67890,
                "player2_name": "Jane Doe",
                "player1_wins": 5,
                "player2_wins": 3,
                "ties": 1,
                "total_meetings": 9,
                "tournaments": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        comparison = client.player(12345).pvp(67890)

        assert isinstance(comparison, PvpComparison)
        assert comparison.player1_id == 12345
        assert comparison.player2_id == 67890
        assert comparison.player1_wins == 5
        assert comparison.player2_wins == 3
        assert comparison.ties == 1
        assert comparison.total_meetings == 9

    def test_results_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player tournament results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results",
            json={
                "player_id": 12345,
                "results": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "Championship 2024",
                        "event_date": "2024-01-15",
                        "city": "Seattle",
                        "country_code": "US",
                        "position": 3,
                        "wppr_points": 25.5,
                        "player_count": 48,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results()

        assert isinstance(results, PlayerResultsResponse)
        assert results.player_id == 12345
        assert len(results.results) == 1
        assert results.results[0].tournament_id == 10001
        assert results.results[0].position == 3
        assert results.results[0].wppr_points == 25.5

    def test_results_with_ranking_system(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player results filtered by ranking system."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results/main",
            json={
                "player_id": 12345,
                "results": [],
                "total_results": 0,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results(ranking_system=RankingSystem.MAIN)

        assert isinstance(results, PlayerResultsResponse)
        assert "results/main" in mock_requests.last_request.path

    def test_results_with_ranking_system_and_type(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test getting player results filtered by system and result type."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results/main/active",
            json={
                "player_id": 12345,
                "results": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "Active Tournament",
                        "position": 1,
                        "count_flag": True,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results(
            ranking_system=RankingSystem.MAIN, result_type=ResultType.ACTIVE
        )

        assert len(results.results) == 1
        assert "results/main/active" in mock_requests.last_request.path

    def test_results_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting paginated player results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results",
            json={
                "player_id": 12345,
                "results": [{"tournament_id": i, "tournament_name": f"T{i}"} for i in range(50)],
                "total_results": 200,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results(start_pos=0, count=50)

        assert len(results.results) == 50
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=50" in query

    def test_history(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player ranking history."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/rank_history",
            json={
                "player_id": 12345,
                "ranking_system": "Main",
                "history": [
                    {
                        "date": "2024-01-01",
                        "rank": 100,
                        "rating": 450.5,
                        "active_events": 10,
                    },
                    {
                        "date": "2024-02-01",
                        "rank": 95,
                        "rating": 455.0,
                        "active_events": 11,
                        "rating_change": 4.5,
                        "rank_change": -5,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        history = client.player(12345).history()

        assert isinstance(history, RankingHistory)
        assert history.player_id == 12345
        assert history.ranking_system == "Main"
        assert len(history.history) == 2
        assert history.history[0].rank == 100
        assert history.history[1].rank == 95
        assert history.history[1].rank_change == -5

    def test_cards(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player achievement cards."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/cards",
            json={
                "player_id": 12345,
                "player_name": "John Smith",
                "cards": [
                    {"card_id": 1, "card_name": "Tournament Winner", "earned_date": "2024-01-15"}
                ],
                "achievements": {"total_cards": 1, "total_points": 100},
            },
        )

        client = IfpaClient(api_key="test-key")
        cards = client.player(12345).cards()

        assert isinstance(cards, PlayerCard)
        assert cards.player_id == 12345
        assert cards.player_name == "John Smith"
        assert len(cards.cards) == 1
        assert cards.achievements is not None


class TestPlayersIntegration:
    """Integration tests ensuring PlayersClient and PlayerHandle work together."""

    def test_search_then_get_player(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of searching then getting player details."""
        # Mock search
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "players": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "wppr_rank": 100,
                    }
                ],
                "total_results": 1,
            },
        )

        # Mock get player
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            json={
                "player": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "city": "Seattle",
                        "ifpa_registered": True,
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        # Search for player
        search_results = client.players.search(name="John")
        assert len(search_results.players) == 1

        # Get full details using the ID from search
        player_id = search_results.players[0].player_id
        full_player = client.player(player_id).get()

        assert full_player.player_id == 12345
        assert full_player.city == "Seattle"
        assert full_player.ifpa_registered is True

    def test_player_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that getting non-existent player raises error."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999",
            status_code=404,
            json={"error": "Player not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.player(99999).get()

        assert exc_info.value.status_code == 404
