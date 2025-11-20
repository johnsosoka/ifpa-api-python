"""Unit tests for TournamentClient.

Tests the tournaments resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import (
    IfpaApiError,
    IfpaClientValidationError,
    TournamentNotLeagueError,
)
from ifpa_api.models.tournaments import (
    RelatedTournamentsResponse,
    Tournament,
    TournamentFormatsListResponse,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSubmissionsResponse,
)


class TestTournamentsClient:
    """Test cases for TournamentClient collection-level operations."""

    def test_search_with_name_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments by name using query builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "Pinball Championship 2024",
                        "event_date": "2024-06-15",
                        "city": "Portland",
                        "country_code": "US",
                        "player_count": 64,
                        "rating_value": 95.5,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search("Pinball").get()

        assert isinstance(result, TournamentSearchResponse)
        assert len(result.tournaments) == 1
        assert result.tournaments[0].tournament_id == 10001
        assert result.tournaments[0].tournament_name == "Pinball Championship 2024"
        assert result.total_results == 1

    def test_search_with_location_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments by location using query builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 10002,
                        "tournament_name": "Portland Monthly",
                        "city": "Portland",
                        "stateprov": "OR",
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search().city("Portland").state("OR").country("US").get()

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "city=portland" in query
        assert "stateprov=or" in query
        assert "country=us" in query

    def test_search_with_date_range(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments with date range using query builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 10003,
                        "tournament_name": "Summer Championship",
                        "event_date": "2024-07-20",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search().date_range("2024-07-01", "2024-07-31").get()

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=2024-07-01" in query
        assert "end_date=2024-07-31" in query

    def test_search_with_tournament_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching with tournament type filter using query builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 10004,
                        "tournament_name": "Women's Championship",
                        "tournament_type": "women",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search().tournament_type("women").get()

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        assert "tournament_type=women" in mock_requests.last_request.query

    def test_search_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments with pagination using query builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {"tournament_id": i, "tournament_name": f"Tournament {i}"} for i in range(50)
                ],
                "total_results": 500,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search().offset(0).limit(50).get()

        assert len(result.tournaments) == 50
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=1" in query
        assert "count=50" in query


class TestTournamentHandle:
    """Test cases for TournamentHandle resource-specific operations."""

    def test_get_tournament(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting a specific tournament's details."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
                "director_name": "Josh Sharpe",
                "director_id": 1000,
                "location_name": "Pinball Paradise",
                "city": "Portland",
                "stateprov": "OR",
                "country_name": "United States",
                "country_code": "US",
                "event_date": "2024-06-15",
                "player_count": 64,
                "machine_count": 20,
                "rating_value": 95.5,
                "women_only": False,
            },
        )

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get(12345)

        assert isinstance(tournament, Tournament)
        assert tournament.tournament_id == 12345
        assert tournament.tournament_name == "Championship 2024"
        assert tournament.director_name == "Josh Sharpe"
        assert tournament.player_count == 64
        assert tournament.women_only is False

    def test_get_tournament_with_string_id(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that tournament ID can be a string."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Test Tournament",
            },
        )

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get("12345")

        assert tournament.tournament_id == 12345

    def test_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting tournament results."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345/results",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
                "event_date": "2024-06-15",
                "results": [
                    {
                        "position": 1,
                        "player_id": 5001,
                        "player_name": "John Smith",
                        "points": 50.0,
                        "ratings_value": 100.0,
                    },
                    {
                        "position": 2,
                        "player_id": 5002,
                        "player_name": "Jane Doe",
                        "points": 40.0,
                        "ratings_value": 80.0,
                    },
                ],
                "player_count": 64,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.tournament(12345).results()

        assert isinstance(results, TournamentResultsResponse)
        assert results.tournament_id == 12345
        assert len(results.results) == 2
        assert results.results[0].position == 1
        assert results.results[0].player_name == "John Smith"
        assert results.results[0].points == 50.0
        assert results.player_count == 64

    def test_formats(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting tournament formats."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345/formats",
            json={
                "tournament_id": 12345,
                "formats": [
                    {
                        "format_id": 1,
                        "format_name": "Strike Knockout",
                        "rounds": 5,
                        "games_per_round": 3,
                        "player_count": 64,
                        "machine_list": ["Medieval Madness", "The Addams Family"],
                    },
                    {
                        "format_id": 2,
                        "format_name": "Swiss",
                        "rounds": 7,
                        "games_per_round": 4,
                        "player_count": 32,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        formats = client.tournament(12345).formats()

        assert isinstance(formats, TournamentFormatsResponse)
        assert formats.tournament_id == 12345
        assert len(formats.formats) == 2
        assert formats.formats[0].format_name == "Strike Knockout"
        assert formats.formats[0].rounds == 5
        assert len(formats.formats[0].machine_list) == 2

    def test_league(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting league information."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345/league",
            json={
                "tournament_id": 12345,
                "league_format": "Monthly Series",
                "sessions": [
                    {
                        "session_date": "2024-01-15",
                        "player_count": 20,
                        "session_value": 5.0,
                    },
                    {
                        "session_date": "2024-02-15",
                        "player_count": 25,
                        "session_value": 5.5,
                    },
                ],
                "total_sessions": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        league = client.tournament(12345).league()

        assert isinstance(league, TournamentLeagueResponse)
        assert league.tournament_id == 12345
        assert league.league_format == "Monthly Series"
        assert len(league.sessions) == 2
        assert league.total_sessions == 2
        assert league.sessions[0].player_count == 20

    def test_submissions(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting tournament submissions."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345/submissions",
            json={
                "tournament_id": 12345,
                "submissions": [
                    {
                        "submission_id": 1,
                        "submission_date": "2024-06-16",
                        "submitter_name": "Josh Sharpe",
                        "status": "approved",
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        submissions = client.tournament(12345).submissions()

        assert isinstance(submissions, TournamentSubmissionsResponse)
        assert submissions.tournament_id == 12345
        assert len(submissions.submissions) == 1
        assert submissions.submissions[0].status == "approved"


class TestTournamentsIntegration:
    """Integration tests ensuring TournamentClient and TournamentHandle work together."""

    def test_search_then_get_tournament(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of searching then getting tournament details using query builder."""
        # Mock search
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 12345,
                        "tournament_name": "Championship 2024",
                        "event_date": "2024-06-15",
                    }
                ],
                "total_results": 1,
            },
        )

        # Mock get tournament
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
                "location_name": "Pinball Paradise",
                "player_count": 64,
            },
        )

        client = IfpaClient(api_key="test-key")

        # Search for tournament using query builder
        search_results = client.tournament.search("Championship").get()
        assert len(search_results.tournaments) == 1

        # Get full details using the ID from search
        tournament_id = search_results.tournaments[0].tournament_id
        full_tournament = client.tournament.get(tournament_id)

        assert full_tournament.tournament_id == 12345
        assert full_tournament.location_name == "Pinball Paradise"
        assert full_tournament.player_count == 64

    def test_tournament_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that getting non-existent tournament raises error."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/99999",
            status_code=404,
            json={"error": "Tournament not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.tournament.get(99999)

        assert exc_info.value.status_code == 404

    def test_league_raises_semantic_exception_on_404(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that 404 for non-league tournament raises TournamentNotLeagueError."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345/league",
            status_code=404,
            json={"error": "Not a league"},
        )

        client = IfpaClient(api_key="test-key")

        with pytest.raises(TournamentNotLeagueError) as exc_info:
            client.tournament(12345).league()

        error = exc_info.value
        assert error.tournament_id == 12345
        assert "12345" in str(error)
        assert "league" in str(error).lower()

        # Verify exception chaining
        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, IfpaApiError)


class TestTournamentQueryBuilder:
    """Test cases for the new fluent query builder pattern."""

    def test_simple_query(self, mock_requests: requests_mock.Mocker) -> None:
        """Test simple tournament name query."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 12345,
                        "tournament_name": "PAPA Championship",
                        "event_date": "2024-06-15",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.tournament.search("PAPA").get()

        assert isinstance(results, TournamentSearchResponse)
        assert len(results.tournaments) == 1
        assert results.tournaments[0].tournament_name == "PAPA Championship"

        # Verify query parameter was sent correctly
        assert mock_requests.last_request is not None
        assert "name=papa" in mock_requests.last_request.query.lower()

    def test_query_with_country_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with country filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search("Championship").country("US").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=championship" in query.lower()
        assert "country=us" in query.lower()

    def test_query_with_state_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with state filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search().state("OR").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "stateprov=or" in query.lower()

    def test_query_with_city_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with city filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search().city("Portland").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "city=portland" in query.lower()

    def test_query_with_date_range(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with date range filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search().date_range("2024-01-01", "2024-12-31").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=2024-01-01" in query
        assert "end_date=2024-12-31" in query

    def test_query_with_tournament_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with tournament type filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search().tournament_type("women").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "tournament_type=women" in query

    def test_query_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with pagination (offset and limit)."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.search("Championship").offset(25).limit(50).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=26" in query
        assert "count=50" in query

    def test_query_chaining_all_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test chaining all available filters together."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        (
            client.tournament.search("Championship")
            .country("US")
            .state("WA")
            .city("Seattle")
            .date_range("2024-01-01", "2024-12-31")
            .tournament_type("open")
            .offset(0)
            .limit(25)
            .get()
        )

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=championship" in query.lower()
        assert "country=us" in query.lower()
        assert "stateprov=wa" in query.lower()
        assert "city=seattle" in query.lower()
        assert "start_date=2024-01-01" in query
        assert "end_date=2024-12-31" in query
        assert "tournament_type=open" in query
        assert "start_pos=1" in query
        assert "count=25" in query

    def test_query_immutability(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query builder is immutable - each method returns new instance."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create base search
        base_search = client.tournament.search().country("US")

        # Create two derivative searches
        wa_search = base_search.state("WA")
        or_search = base_search.state("OR")

        # Execute both searches
        wa_search.get()
        wa_request = mock_requests.last_request
        assert wa_request is not None
        assert "stateprov=wa" in wa_request.query.lower()
        assert "stateprov=or" not in wa_request.query.lower()

        or_search.get()
        or_request = mock_requests.last_request
        assert or_request is not None
        assert "stateprov=or" in or_request.query.lower()
        assert "stateprov=wa" not in or_request.query.lower()

        # Verify both searches have country=US
        assert "country=us" in wa_request.query.lower()
        assert "country=us" in or_request.query.lower()

    def test_query_reuse(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query can be reused multiple times (immutability)."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create a reusable query
        us_query = client.tournament.query().country("US")

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
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.tournament.query().country("US").state("WA").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country=us" in query.lower()
        assert "stateprov=wa" in query.lower()
        # Should not have a name parameter
        assert "name=" not in query.lower()

    def test_query_with_initial_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query() method with initial name parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        # Test both ways of setting name
        client.tournament.query("PAPA").get()
        assert mock_requests.last_request is not None
        assert "name=papa" in mock_requests.last_request.query.lower()

        # Also test chaining after initial name
        client.tournament.search("Championship").country("US").get()
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=championship" in query.lower()
        assert "country=us" in query.lower()

    def test_query_builder_repr(self) -> None:
        """Test query builder string representation."""
        client = IfpaClient(api_key="test-key")
        builder = client.tournament.query("PAPA").country("US")

        # Should show class name and params
        repr_str = repr(builder)
        assert "TournamentQueryBuilder" in repr_str
        assert "params=" in repr_str

    def test_date_range_validation_missing_start(self) -> None:
        """Test that get() raises error when only end_date is present."""
        client = IfpaClient(api_key="test-key")
        builder = client.tournament.query()
        # Manually add only end_date to params (simulating partial date range)
        builder._params["end_date"] = "2024-12-31"

        with pytest.raises(IfpaClientValidationError) as exc_info:
            builder.get()

        assert "start_date and end_date must be provided together" in str(exc_info.value)

    def test_date_range_validation_missing_end(self) -> None:
        """Test that get() raises error when only start_date is present."""
        client = IfpaClient(api_key="test-key")
        builder = client.tournament.query()
        # Manually add only start_date to params (simulating partial date range)
        builder._params["start_date"] = "2024-01-01"

        with pytest.raises(IfpaClientValidationError) as exc_info:
            builder.get()

        assert "start_date and end_date must be provided together" in str(exc_info.value)

    def test_date_range_validation_both_present(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that get() succeeds when both dates are present."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        # Should not raise an error
        client.tournament.search().date_range("2024-01-01", "2024-12-31").get()

    def test_date_range_validation_both_absent(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that get() succeeds when both dates are absent."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        # Should not raise an error
        client.tournament.search("Championship").country("US").get()

    def test_date_range_invalid_start_date_format(self) -> None:
        """Test that date_range() raises error with invalid start_date format."""
        client = IfpaClient(api_key="test-key")

        with pytest.raises(IfpaClientValidationError) as exc_info:
            client.tournament.query().date_range("2024/01/01", "2024-12-31")

        assert "start_date must be in YYYY-MM-DD format" in str(exc_info.value)
        assert "2024/01/01" in str(exc_info.value)

    def test_date_range_invalid_end_date_format(self) -> None:
        """Test that date_range() raises error with invalid end_date format."""
        client = IfpaClient(api_key="test-key")

        with pytest.raises(IfpaClientValidationError) as exc_info:
            client.tournament.query().date_range("2024-01-01", "12-31-2024")

        assert "end_date must be in YYYY-MM-DD format" in str(exc_info.value)
        assert "12-31-2024" in str(exc_info.value)

    def test_date_range_valid_format(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that date_range() accepts valid YYYY-MM-DD format."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        # Should not raise an error
        result = client.tournament.search().date_range("2024-01-01", "2024-12-31").get()
        assert isinstance(result, TournamentSearchResponse)


class TestTournamentQueryBuilderIntegration:
    """Integration tests for query builder with realistic scenarios."""

    def test_search_and_refine_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test realistic workflow: search broadly, then refine."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {"tournament_id": i, "tournament_name": f"Tournament {i}"} for i in range(100)
                ],
                "total_results": 100,
            },
        )

        client = IfpaClient(api_key="test-key")

        # Start with broad search
        broad_results = client.tournament.query("Championship").limit(100).get()
        assert len(broad_results.tournaments) == 100

        # Refine to specific country
        client.tournament.query("Championship").country("US").limit(50).get()
        assert mock_requests.last_request is not None
        assert "country=us" in mock_requests.last_request.query.lower()

    def test_pagination_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test paginating through results."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create base query
        base = client.tournament.query("Championship").country("US")

        # Get pages
        page1 = base.offset(0).limit(25)
        page2 = base.offset(25).limit(25)
        page3 = base.offset(50).limit(25)

        # Execute pages
        page1.get()
        assert mock_requests.last_request is not None
        assert "start_pos=1" in mock_requests.last_request.query
        page2.get()
        assert mock_requests.last_request is not None
        assert "start_pos=26" in mock_requests.last_request.query
        page3.get()
        assert mock_requests.last_request is not None
        assert "start_pos=51" in mock_requests.last_request.query

    def test_date_range_search_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments within a date range."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Search for tournaments in 2024
        client.tournament.query().country("US").date_range("2024-01-01", "2024-12-31").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=2024-01-01" in query
        assert "end_date=2024-12-31" in query
        assert "country=us" in query.lower()


def test_tournament_related(mock_requests: requests_mock.Mocker) -> None:
    """Test related() method returns related tournaments."""
    mock_requests.get(
        "https://api.ifpapinball.com/tournament/12345/related",
        json={
            "tournament": [
                {
                    "tournament_id": 12344,
                    "tournament_name": "Previous Event",
                    "tournament_type": "Regular",
                    "event_name": "Same Venue Series",
                    "event_start_date": "2023-01-15",
                    "event_end_date": "2023-01-15",
                    "ranking_system": "WPPR",
                    "winner": {
                        "player_id": 100,
                        "name": "John Doe",
                        "country_name": "United States",
                        "country_code": "US",
                    },
                },
                {
                    "tournament_id": 12346,
                    "tournament_name": "Next Event",
                    "tournament_type": None,
                    "event_name": "Same Venue Series",
                    "event_start_date": "2024-01-15",
                    "event_end_date": "2024-01-15",
                    "ranking_system": "WPPR",
                    "winner": None,
                },
            ]
        },
    )

    client = IfpaClient(api_key="test-key")
    result = client.tournament(12345).related()

    assert isinstance(result, RelatedTournamentsResponse)
    assert len(result.tournament) == 2
    assert result.tournament[0].tournament_id == 12344
    assert result.tournament[0].winner is not None
    assert result.tournament[0].winner.name == "John Doe"
    assert result.tournament[1].winner is None


def test_list_formats(mock_requests: requests_mock.Mocker) -> None:
    """Test list_formats() method returns format lists."""
    mock_requests.get(
        "https://api.ifpapinball.com/tournament/formats",
        json={
            "qualifying_formats": [
                {"format_id": 1, "name": "Best Game", "description": "Best single game"},
                {"format_id": 2, "name": "Swiss", "description": None},
            ],
            "finals_formats": [
                {"format_id": 10, "name": "Single Elimination", "description": "Bracket"},
                {"format_id": 11, "name": "Best of 3", "description": None},
            ],
        },
    )

    client = IfpaClient(api_key="test-key")
    result = client.tournament.list_formats()

    assert isinstance(result, TournamentFormatsListResponse)
    assert len(result.qualifying_formats) == 2
    assert len(result.finals_formats) == 2
    assert result.qualifying_formats[0].format_id == 1
    assert result.qualifying_formats[0].name == "Best Game"
    assert result.qualifying_formats[1].description is None
    assert result.finals_formats[0].name == "Single Elimination"


class TestTournamentConvenienceMethods:
    """Test cases for tournament convenience methods."""

    def test_tournament_get_or_none_found(self, mock_requests: requests_mock.Mocker) -> None:
        """Test get_or_none returns tournament when found."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
            },
        )

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get_or_none(12345)

        assert tournament is not None
        assert tournament.tournament_id == 12345
        assert tournament.tournament_name == "Championship 2024"

    def test_tournament_get_or_none_not_found(self, mock_requests: requests_mock.Mocker) -> None:
        """Test get_or_none returns None for 404."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/99999",
            status_code=404,
            json={"error": "Tournament not found"},
        )

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get_or_none(99999)

        assert tournament is None

    def test_tournament_get_or_none_other_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test get_or_none raises for non-404 errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.tournament.get_or_none(12345)

        assert exc_info.value.status_code == 500

    def test_tournament_exists_true(self, mock_requests: requests_mock.Mocker) -> None:
        """Test exists returns True when tournament found."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
            },
        )

        client = IfpaClient(api_key="test-key")
        assert client.tournament.exists(12345) is True

    def test_tournament_exists_false(self, mock_requests: requests_mock.Mocker) -> None:
        """Test exists returns False when tournament not found."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/99999",
            status_code=404,
            json={"error": "Tournament not found"},
        )

        client = IfpaClient(api_key="test-key")
        assert client.tournament.exists(99999) is False

    def test_tournament_search_first(self, mock_requests: requests_mock.Mocker) -> None:
        """Test first() returns first search result."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 12345,
                        "tournament_name": "PAPA Championship",
                        "event_date": "2024-06-15",
                    },
                    {
                        "tournament_id": 12346,
                        "tournament_name": "PAPA Open",
                        "event_date": "2024-07-15",
                    },
                ],
                "total_results": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search("PAPA").first()

        assert result.tournament_id == 12345
        assert result.tournament_name == "PAPA Championship"

    def test_tournament_search_first_no_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test first() raises IndexError when no results."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IndexError, match="no results"):
            client.tournament.search("NonExistent").first()

    def test_tournament_search_first_or_none_found(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test first_or_none() returns first result when found."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "tournaments": [
                    {
                        "tournament_id": 12345,
                        "tournament_name": "PAPA Championship",
                        "event_date": "2024-06-15",
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search("PAPA").first_or_none()

        assert result is not None
        assert result.tournament_id == 12345

    def test_tournament_search_first_or_none_no_results(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test first_or_none() returns None when no results."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        result = client.tournament.search("NonExistent").first_or_none()

        assert result is None


class TestTournamentDeprecationWarnings:
    """Test cases for deprecated methods."""

    def test_tournament_query_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that query() issues deprecation warning."""
        import warnings

        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.tournament.query("test").get()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "query()" in str(w[0].message)
            assert "search()" in str(w[0].message)

    def test_tournament_details_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that details() issues deprecation warning."""
        import warnings

        mock_requests.get(
            "https://api.ifpapinball.com/tournament/12345",
            json={
                "tournament_id": 12345,
                "tournament_name": "Championship 2024",
            },
        )

        client = IfpaClient(api_key="test-key")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.tournament(12345).details()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "details()" in str(w[0].message)
            assert "get" in str(w[0].message)
