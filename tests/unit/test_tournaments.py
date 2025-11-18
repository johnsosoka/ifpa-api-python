"""Unit tests for TournamentsClient and TournamentHandle.

Tests the tournaments resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
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
    """Test cases for TournamentsClient collection-level operations."""

    def test_search_with_name_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments by name."""
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
        result = client.tournaments.search(name="Pinball")

        assert isinstance(result, TournamentSearchResponse)
        assert len(result.tournaments) == 1
        assert result.tournaments[0].tournament_id == 10001
        assert result.tournaments[0].tournament_name == "Pinball Championship 2024"
        assert result.total_results == 1

    def test_search_with_location_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments by location."""
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
        result = client.tournaments.search(city="Portland", stateprov="OR", country="US")

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "city=portland" in query
        assert "stateprov=or" in query
        assert "country=us" in query

    def test_search_with_date_range(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments with date range."""
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
        result = client.tournaments.search(start_date="2024-07-01", end_date="2024-07-31")

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=2024-07-01" in query
        assert "end_date=2024-07-31" in query

    def test_search_with_tournament_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching with tournament type filter."""
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
        result = client.tournaments.search(tournament_type="women")

        assert len(result.tournaments) == 1
        assert mock_requests.last_request is not None
        assert "tournament_type=women" in mock_requests.last_request.query

    def test_search_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching tournaments with pagination."""
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
        result = client.tournaments.search(start_pos=0, count=50)

        assert len(result.tournaments) == 50
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
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
        tournament = client.tournament(12345).get()

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
        tournament = client.tournament("12345").get()

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
        assert results.results[0].wppr_points == 50.0
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
    """Integration tests ensuring TournamentsClient and TournamentHandle work together."""

    def test_search_then_get_tournament(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of searching then getting tournament details."""
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

        # Search for tournament
        search_results = client.tournaments.search(name="Championship")
        assert len(search_results.tournaments) == 1

        # Get full details using the ID from search
        tournament_id = search_results.tournaments[0].tournament_id
        full_tournament = client.tournament(tournament_id).get()

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
            client.tournament(99999).get()

        assert exc_info.value.status_code == 404


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
    result = client.tournaments.list_formats()

    assert isinstance(result, TournamentFormatsListResponse)
    assert len(result.qualifying_formats) == 2
    assert len(result.finals_formats) == 2
    assert result.qualifying_formats[0].format_id == 1
    assert result.qualifying_formats[0].name == "Best Game"
    assert result.qualifying_formats[1].description is None
    assert result.finals_formats[0].name == "Single Elimination"
