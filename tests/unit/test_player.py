"""Unit tests for PlayersClient and PlayerHandle.

Tests the players resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)


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
        player = client.player(12345).details()

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
        player = client.player("12345").details()

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
                        "current_points": 25.5,
                        "all_time_points": 30.0,
                        "active_points": 25.5,
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
        assert results.results[0].current_points == 25.5
        assert results.results[0].all_time_points == 30.0
        assert results.results[0].active_points == 25.5

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
        from ifpa_api.core.exceptions import PlayersNeverMetError

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
        from ifpa_api.core.exceptions import PlayersNeverMetError

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

    def test_player_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that getting non-existent player raises error."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/99999",
            status_code=404,
            json={"error": "Player not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.player(99999).details()

        assert exc_info.value.status_code == 404


class TestPlayerQueryBuilder:
    """Test cases for the new fluent query builder pattern."""

    def test_simple_query(self, mock_requests: requests_mock.Mocker) -> None:
        """Test simple player name query."""
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

        client = IfpaClient(api_key="test-key")
        results = client.player.query("John").get()

        assert isinstance(results, PlayerSearchResponse)
        assert len(results.search) == 1
        assert results.search[0].first_name == "John"

        # Verify query parameter was sent correctly
        assert mock_requests.last_request is not None
        assert "name=john" in mock_requests.last_request.query.lower()

    def test_query_with_country_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with country filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query("John").country("US").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=john" in query.lower()
        assert "country=us" in query.lower()

    def test_query_with_state_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with state filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query("Smith").state("WA").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=smith" in query.lower()
        assert "stateprov=wa" in query.lower()

    def test_query_with_tournament_and_position(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with tournament and position filters."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query().tournament("PAPA").position(1).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "tournament=papa" in query.lower()
        assert "tourpos=1" in query

    def test_query_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with pagination (offset and limit)."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query("Smith").offset(25).limit(50).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=26" in query
        assert "count=50" in query

    def test_query_chaining_all_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test chaining all available filters together."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query("John").country("US").state("WA").tournament("PAPA").position(1).offset(
            0
        ).limit(25).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=john" in query.lower()
        assert "country=us" in query.lower()
        assert "stateprov=wa" in query.lower()
        assert "tournament=papa" in query.lower()
        assert "tourpos=1" in query
        assert "start_pos=1" in query
        assert "count=25" in query

    def test_query_immutability(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query builder is immutable - each method returns new instance."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")

        # Create base query
        base_query = client.player.query().country("US")

        # Create two derivative queries
        wa_query = base_query.state("WA")
        or_query = base_query.state("OR")

        # Execute both queries
        wa_query.get()
        wa_request = mock_requests.last_request
        assert wa_request is not None
        assert "stateprov=wa" in wa_request.query.lower()
        assert "stateprov=or" not in wa_request.query.lower()

        or_query.get()
        or_request = mock_requests.last_request
        assert or_request is not None
        assert "stateprov=or" in or_request.query.lower()
        assert "stateprov=wa" not in or_request.query.lower()

        # Verify both queries have country=US
        assert "country=us" in wa_request.query.lower()
        assert "country=us" in or_request.query.lower()

    def test_query_reuse(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query can be reused multiple times (immutability)."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")

        # Create a reusable query
        us_query = client.player.query().country("US")

        # Execute it multiple times with different additional filters
        us_query.state("WA").limit(10).get()
        us_query.state("OR").limit(20).get()
        us_query.state("CA").limit(30).get()

        # Base query should still be unchanged
        us_query.get()
        final_request = mock_requests.last_request
        assert final_request is not None
        assert "country=us" in final_request.query.lower()
        # Should not have any of the state filters from previous calls
        assert "stateprov" not in final_request.query.lower()

    def test_empty_query(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with no name (filter-only query)."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        client.player.query().country("US").state("WA").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country=us" in query.lower()
        assert "stateprov=wa" in query.lower()
        # Should not have a name parameter
        assert "name=" not in query.lower()

    def test_query_with_initial_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query() method with initial name parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")
        # Test both ways of setting name
        client.player.query("John").get()
        assert mock_requests.last_request is not None
        assert "name=john" in mock_requests.last_request.query.lower()

        # Also test chaining after initial name
        client.player.query("Jane").country("CA").get()
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=jane" in query.lower()
        assert "country=ca" in query.lower()

    def test_query_builder_repr(self) -> None:
        """Test query builder string representation."""
        client = IfpaClient(api_key="test-key")
        builder = client.player.query("John").country("US")

        # Should show class name and params
        repr_str = repr(builder)
        assert "PlayerQueryBuilder" in repr_str
        assert "params=" in repr_str


class TestPlayerQueryBuilderIntegration:
    """Integration tests for query builder with realistic scenarios."""

    def test_search_and_refine_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test realistic workflow: search broadly, then refine."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "search": [
                    {"player_id": i, "first_name": f"Player{i}", "last_name": "Test"}
                    for i in range(100)
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        # Start with broad search
        broad_results = client.player.query("Test").limit(100).get()
        assert len(broad_results.search) == 100

        # Refine to specific country
        client.player.query("Test").country("US").limit(50).get()
        assert mock_requests.last_request is not None
        assert "country=us" in mock_requests.last_request.query.lower()

    def test_pagination_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test paginating through results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"search": []},
        )

        client = IfpaClient(api_key="test-key")

        # Create base query
        base = client.player.query("Smith").country("US")

        # Get pages
        page1 = base.offset(0).limit(25)
        page2 = base.offset(25).limit(25)
        page3 = base.offset(50).limit(25)

        # Execute pages
        page1.get()
        assert "start_pos=1" in mock_requests.last_request.query
        page2.get()
        assert "start_pos=26" in mock_requests.last_request.query
        page3.get()
        assert "start_pos=51" in mock_requests.last_request.query
