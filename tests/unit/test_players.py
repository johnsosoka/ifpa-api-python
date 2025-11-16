"""Unit tests for PlayersClient and PlayerHandle.

Tests the players resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    MultiPlayerResponse,
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
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
                "query": "John",
                "search": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "city": "Seattle",
                        "state": "WA",
                        "country_code": "US",
                        "country_name": "United States",
                        "wppr_rank": "100",
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(name="John")

        assert isinstance(result, PlayerSearchResponse)
        assert result.query == "John"
        assert len(result.search) == 1
        assert result.search[0].player_id == 12345
        assert result.search[0].first_name == "John"
        assert result.search[0].last_name == "Smith"
        assert result.search[0].wppr_rank == "100"

    def test_search_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching players with pagination parameters."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "query": "Test",
                "search": [
                    {"player_id": i, "first_name": f"Player{i}", "last_name": "Test"}
                    for i in range(25)
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.search(name="Test", start_pos=0, count=25)

        assert len(result.search) == 25

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=25" in query

    def test_get_multiple(self, mock_requests: requests_mock.Mocker) -> None:
        """Test fetching multiple players at once."""
        mock_requests.get(
            "https://api.ifpapinball.com/player",
            json={
                "player": [
                    {"player_id": 123, "first_name": "John", "last_name": "Smith"},
                    {"player_id": 456, "first_name": "Jane", "last_name": "Doe"},
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.players.get_multiple([123, 456])

        assert isinstance(result, MultiPlayerResponse)
        assert result.player is not None
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "players=123%2c456" in query.lower()

    def test_get_multiple_max_validation(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that get_multiple raises error for more than 50 players."""
        from ifpa_api.exceptions import IfpaClientValidationError

        client = IfpaClient(api_key="test-key")

        with pytest.raises(IfpaClientValidationError) as exc_info:
            client.players.get_multiple(list(range(1, 52)))

        assert "50 player ids" in str(exc_info.value).lower()

    def test_search_parameter_mapping(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that name parameter maps to 'name' query param, not 'q'."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.players.search(name="John")

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=john" in query.lower()
        assert "q=" not in query

    def test_search_with_tournament_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test search with new tournament and tourpos parameters."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.players.search(tournament="PAPA", tourpos=1)

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "tournament=papa" in query.lower()
        assert "tourpos=1" in query


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

    def test_pvp_comparison(self, mock_requests: requests_mock.Mocker) -> None:
        """Test head-to-head player comparison with nested API structure."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/pvp/67890",
            json={
                "player_1": {
                    "player_id": 12345,
                    "first_name": "John",
                    "last_name": "Smith",
                    "city": "Seattle",
                    "stateprov": "WA",
                    "country_name": "United States",
                    "country_code": "US",
                },
                "player_2": {
                    "player_id": 67890,
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "city": "Portland",
                    "stateprov": "OR",
                    "country_name": "United States",
                    "country_code": "US",
                },
                "player1_wins": 5,
                "player2_wins": 3,
                "ties": 1,
                "total_meetings": 9,
                "pvp": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        comparison = client.player(12345).pvp(67890)

        assert isinstance(comparison, PvpComparison)
        assert comparison.player1_id == 12345
        assert comparison.player1_name == "John Smith"
        assert comparison.player2_id == 67890
        assert comparison.player2_name == "Jane Doe"
        assert comparison.player1_wins == 5
        assert comparison.player2_wins == 3
        assert comparison.ties == 1
        assert comparison.total_meetings == 9

    def test_pvp_comparison_with_tournaments(self, mock_requests: requests_mock.Mocker) -> None:
        """Test PVP comparison includes tournament details."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/pvp/67890",
            json={
                "player_1": {
                    "player_id": 12345,
                    "first_name": "John",
                    "last_name": "Smith",
                },
                "player_2": {
                    "player_id": 67890,
                    "first_name": "Jane",
                    "last_name": "Doe",
                },
                "player1_wins": 2,
                "player2_wins": 1,
                "ties": 0,
                "total_meetings": 3,
                "pvp": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "Championship 2024",
                        "event_date": "2024-01-15",
                        "player_1_position": 3,
                        "player_2_position": 5,
                        "winner_player_id": 12345,
                    },
                    {
                        "tournament_id": 10002,
                        "tournament_name": "Spring Open",
                        "event_date": "2024-03-20",
                        "player_1_position": 8,
                        "player_2_position": 2,
                        "winner_player_id": 67890,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        comparison = client.player(12345).pvp(67890)

        assert isinstance(comparison, PvpComparison)
        assert len(comparison.tournaments) == 2
        assert comparison.tournaments[0].tournament_id == 10001
        assert comparison.tournaments[0].tournament_name == "Championship 2024"
        assert comparison.tournaments[0].player_1_position == 3
        assert comparison.tournaments[0].player_2_position == 5
        assert comparison.tournaments[0].winner_player_id == 12345

    def test_pvp_comparison_backwards_compatibility(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test PVP comparison works with old flat format (backwards compatibility)."""
        # This tests that if the API or mocks use the old flat format,
        # the model still works correctly
        from ifpa_api.models.player import PvpComparison

        # Test direct model instantiation with flat format
        flat_data = {
            "player1_id": 12345,
            "player1_name": "John Smith",
            "player2_id": 67890,
            "player2_name": "Jane Doe",
            "player1_wins": 5,
            "player2_wins": 3,
            "ties": 1,
            "total_meetings": 9,
            "tournaments": [],
        }

        comparison = PvpComparison.model_validate(flat_data)

        assert comparison.player1_id == 12345
        assert comparison.player1_name == "John Smith"
        assert comparison.player2_id == 67890
        assert comparison.player2_name == "Jane Doe"
        assert comparison.player1_wins == 5
        assert comparison.player2_wins == 3
        assert comparison.ties == 1
        assert comparison.total_meetings == 9

    def test_results_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player tournament results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results/main/active",
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
        results = client.player(12345).results(
            ranking_system=RankingSystem.MAIN, result_type=ResultType.ACTIVE
        )

        assert isinstance(results, PlayerResultsResponse)
        assert results.player_id == 12345
        assert len(results.results) == 1
        assert results.results[0].tournament_id == 10001
        assert results.results[0].position == 3
        assert results.results[0].wppr_points == 25.5

    def test_results_with_ranking_system(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player results filtered by ranking system."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results/main/active",
            json={
                "player_id": 12345,
                "results": [],
                "total_results": 0,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results(
            ranking_system=RankingSystem.MAIN, result_type=ResultType.ACTIVE
        )

        assert isinstance(results, PlayerResultsResponse)
        assert mock_requests.last_request is not None
        assert "results/main/active" in mock_requests.last_request.path

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
        assert mock_requests.last_request is not None
        assert "results/main/active" in mock_requests.last_request.path

    def test_results_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting paginated player results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/results/main/active",
            json={
                "player_id": 12345,
                "results": [{"tournament_id": i, "tournament_name": f"T{i}"} for i in range(50)],
                "total_results": 200,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.player(12345).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            start_pos=0,
            count=50,
        )

        assert len(results.results) == 50
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=50" in query

    def test_history(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player ranking history."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/rank_history",
            json={
                "player_id": 12345,
                "system": "MAIN",
                "active_flag": "Y",
                "rank_history": [
                    {
                        "rank_date": "2024-01-01",
                        "rank_position": "100",
                        "wppr_points": "450.50",
                        "tournaments_played_count": "10",
                    },
                    {
                        "rank_date": "2024-02-01",
                        "rank_position": "95",
                        "wppr_points": "455.00",
                        "tournaments_played_count": "11",
                    },
                ],
                "rating_history": [
                    {
                        "rating_date": "2024-01-01",
                        "rating": "1500.5",
                    },
                    {
                        "rating_date": "2024-02-01",
                        "rating": "1505.0",
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        history = client.player(12345).history()

        assert isinstance(history, RankingHistory)
        assert history.player_id == 12345
        assert history.system == "MAIN"
        assert history.active_flag == "Y"
        assert len(history.rank_history) == 2
        assert len(history.rating_history) == 2
        assert history.rank_history[0].rank_position == "100"
        assert history.rank_history[1].rank_position == "95"
        assert history.rating_history[0].rating == "1500.5"
        assert history.rating_history[1].rating == "1505.0"

    def test_pvp_all(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting PVP summary (all competitors)."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/pvp",
            json={
                "player_id": 12345,
                "total_competitors": 42,
                "system": "MAIN",
                "type": "all",
                "title": "",
            },
        )

        client = IfpaClient(api_key="test-key")
        summary = client.player(12345).pvp_all()

        assert isinstance(summary, PvpAllCompetitors)
        assert summary.player_id == 12345
        assert summary.total_competitors == 42
        assert summary.system == "MAIN"
        assert summary.type == "all"

    def test_pvp_never_met_raises_custom_exception(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test pvp() raises PlayersNeverMetError when players never met."""
        from ifpa_api.exceptions import PlayersNeverMetError

        mock_requests.get(
            "https://api.ifpapinball.com/player/12345/pvp/67890",
            status_code=404,
            json={"error": "Not found"},
        )

        client = IfpaClient(api_key="test-key")

        with pytest.raises(PlayersNeverMetError) as exc_info:
            client.player(12345).pvp(67890)

        # Verify exception attributes
        assert exc_info.value.player_id == 12345
        assert exc_info.value.opponent_id == 67890
        assert "never competed" in str(exc_info.value).lower()

    def test_pvp_other_404_raises_api_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test pvp() still raises PlayersNeverMetError for any 404."""
        from ifpa_api.exceptions import PlayersNeverMetError

        # Mock a 404 with different message (e.g., player doesn't exist)
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999999/pvp/67890",
            status_code=404,
            json={"error": "Player not found"},
        )

        client = IfpaClient(api_key="test-key")

        # Should still raise PlayersNeverMetError for any 404
        with pytest.raises(PlayersNeverMetError) as exc_info:
            client.player(99999999).pvp(67890)

        # Verify the exception contains both player IDs
        assert exc_info.value.player_id == 99999999
        assert exc_info.value.opponent_id == 67890


class TestPlayersIntegration:
    """Integration tests ensuring PlayersClient and PlayerHandle work together."""

    def test_search_then_get_player(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of searching then getting player details."""
        # Mock search
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "query": "John",
                "search": [
                    {
                        "player_id": 12345,
                        "first_name": "John",
                        "last_name": "Smith",
                        "wppr_rank": "100",
                    }
                ],
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
        assert len(search_results.search) == 1

        # Get full details using the ID from search
        player_id = search_results.search[0].player_id
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
