"""Unit tests for DirectorsClient and DirectorHandle.

Tests the directors resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)


class TestDirectorsClient:
    """Test cases for DirectorsClient collection-level operations."""

    def test_search_with_name_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching directors by name."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": 1000,
                        "name": "Josh Sharpe",
                        "city": "Portland",
                        "stateprov": "OR",
                        "country_code": "US",
                        "tournament_count": 42,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.search(name="Josh")

        assert isinstance(result, DirectorSearchResponse)
        assert len(result.directors) == 1
        assert result.directors[0].director_id == 1000
        assert result.directors[0].name == "Josh Sharpe"
        # count field aliased to total_results for backward compatibility
        assert result.count == 1

        # Verify request was made correctly
        assert mock_requests.last_request.query == "name=josh"

    def test_search_with_location_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching directors by location."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": 2000,
                        "name": "Jane Doe",
                        "city": "Chicago",
                        "stateprov": "IL",
                        "country_code": "US",
                        "tournament_count": 15,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.search(city="Chicago", stateprov="IL", country="US")

        assert len(result.directors) == 1
        assert result.directors[0].city == "Chicago"

        # Verify all query params were sent
        query = mock_requests.last_request.query
        assert "city=chicago" in query
        assert "stateprov=il" in query
        assert "country=us" in query

    def test_search_with_no_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test searching directors without filters returns all."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.search()

        assert isinstance(result, DirectorSearchResponse)
        assert len(result.directors) == 0
        assert mock_requests.last_request.query == ""

    def test_search_handles_api_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that search properly handles API errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.directors.search(name="test")

        assert exc_info.value.status_code == 500
        assert "Internal server error" in str(exc_info.value)

    def test_search_with_spec_format(self, mock_requests: requests_mock.Mocker) -> None:
        """Test search with API spec format (search_term and count fields)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "search_term": "sharpe",
                "count": 2,
                "directors": [
                    {
                        "director_id": 1000,
                        "name": "Josh Sharpe",
                        "city": "Chicago",
                        "stateprov": "IL",
                        "country_code": "US",
                        "country_name": "United States",
                        "profile_photo": "https://example.com/photo.jpg",
                        "tournament_count": 42,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.search(name="sharpe")

        assert isinstance(result, DirectorSearchResponse)
        assert result.search_term == "sharpe"
        assert result.count == 2
        assert len(result.directors) == 1
        assert result.directors[0].profile_photo == "https://example.com/photo.jpg"
        assert result.directors[0].country_name == "United States"

    def test_country_directors(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting country directors list."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "directors": [
                    {
                        "player_id": 5000,
                        "name": "Country Director 1",
                        "country_code": "US",
                        "country_name": "United States",
                    },
                    {
                        "player_id": 5001,
                        "name": "Country Director 2",
                        "country_code": "CA",
                        "country_name": "Canada",
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.country_directors()

        assert isinstance(result, CountryDirectorsResponse)
        assert len(result.country_directors) == 2
        assert result.country_directors[0].player_id == 5000
        assert result.country_directors[0].country_code == "US"
        assert result.country_directors[1].country_name == "Canada"

    def test_country_directors_with_spec_fields(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country directors with API spec format (count and profile_photo)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "count": 2,
                "directors": [
                    {
                        "player_id": 5000,
                        "name": "Josh Sharpe",
                        "country_code": "US",
                        "country_name": "United States",
                        "profile_photo": "https://example.com/photo.jpg",
                    },
                    {
                        "player_id": 5001,
                        "name": "Jane Doe",
                        "country_code": "CA",
                        "country_name": "Canada",
                        "profile_photo": "https://example.com/photo2.jpg",
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.directors.country_directors()

        assert isinstance(result, CountryDirectorsResponse)
        assert result.count == 2
        assert len(result.country_directors) == 2
        assert result.country_directors[0].profile_photo == "https://example.com/photo.jpg"
        assert result.country_directors[1].profile_photo == "https://example.com/photo2.jpg"


class TestDirectorHandle:
    """Test cases for DirectorHandle resource-specific operations."""

    def test_get_director(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting a specific director's details."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000",
            json={
                "director_id": 1000,
                "name": "Josh Sharpe",
                "city": "Portland",
                "stateprov": "OR",
                "country_name": "United States",
                "country_code": "US",
                "profile_photo": "https://example.com/photo.jpg",
                "stats": {
                    "tournament_count": 42,
                    "unique_player_count": 500,
                    "average_value": 75.5,
                },
            },
        )

        client = IfpaClient(api_key="test-key")
        director = client.director(1000).get()

        assert isinstance(director, Director)
        assert director.director_id == 1000
        assert director.name == "Josh Sharpe"
        assert director.city == "Portland"
        assert director.stats is not None
        assert director.stats.tournament_count == 42
        assert director.stats.unique_player_count == 500

    def test_get_director_with_string_id(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that director ID can be a string."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000",
            json={
                "director_id": 1000,
                "name": "Josh Sharpe",
            },
        )

        client = IfpaClient(api_key="test-key")
        director = client.director("1000").get()

        assert director.director_id == 1000

    def test_tournaments_past(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting past tournaments for a director."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000/tournaments/past",
            json={
                "director_id": 1000,
                "director_name": "Josh Sharpe",
                "tournaments": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "Monthly Pinball Championship",
                        "event_date": "2024-01-15",
                        "city": "Portland",
                        "country_code": "US",
                        "player_count": 32,
                        "value": 85.0,
                    },
                    {
                        "tournament_id": 10002,
                        "tournament_name": "Pinball Spectacular",
                        "event_date": "2023-12-10",
                        "city": "Portland",
                        "country_code": "US",
                        "player_count": 48,
                        "value": 90.5,
                    },
                ],
                "total_count": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.director(1000).tournaments(TimePeriod.PAST)

        assert isinstance(result, DirectorTournamentsResponse)
        assert result.director_id == 1000
        assert len(result.tournaments) == 2
        assert result.tournaments[0].tournament_id == 10001
        assert result.tournaments[0].tournament_name == "Monthly Pinball Championship"
        assert result.tournaments[0].player_count == 32

    def test_tournaments_future(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting upcoming tournaments for a director."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000/tournaments/future",
            json={
                "director_id": 1000,
                "director_name": "Josh Sharpe",
                "tournaments": [
                    {
                        "tournament_id": 20001,
                        "tournament_name": "Future Championship",
                        "event_date": "2025-06-15",
                        "city": "Portland",
                        "country_code": "US",
                        "player_count": 0,
                    }
                ],
                "total_count": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.director(1000).tournaments(TimePeriod.FUTURE)

        assert len(result.tournaments) == 1
        assert result.tournaments[0].tournament_id == 20001
        assert result.tournaments[0].event_date == "2025-06-15"

    def test_tournaments_with_string_enum(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that tournaments accepts string values for time period."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000/tournaments/past",
            json={
                "director_id": 1000,
                "tournaments": [],
                "total_count": 0,
            },
        )

        client = IfpaClient(api_key="test-key")
        # Should accept string directly
        result = client.director(1000).tournaments("past")  # type: ignore

        assert isinstance(result, DirectorTournamentsResponse)

    def test_tournaments_with_spec_fields(self, mock_requests: requests_mock.Mocker) -> None:
        """Test tournaments with API spec field names (event_start_date, stateprov_code, etc)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000/tournaments/past",
            json={
                "director_id": 1000,
                "tournament_count": 1,
                "tournaments": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "IFPA World Championships",
                        "event_name": "Main Tournament",
                        "event_start_date": "2024-05-01T00:00:00.000Z",
                        "event_end_date": "2024-05-03T00:00:00.000Z",
                        "ranking_system": "MAIN",
                        "qualifying_format": "Matchplay",
                        "finals_format": "Single Elimination",
                        "city": "Denver",
                        "stateprov_code": "CO",
                        "country_code": "US",
                        "country_name": "United States",
                        "player_count": 80,
                    }
                ],
                "total_count": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.director(1000).tournaments(TimePeriod.PAST)

        assert len(result.tournaments) == 1
        tournament = result.tournaments[0]
        # Verify new spec fields are captured
        assert tournament.event_date == "2024-05-01T00:00:00.000Z"  # aliased from event_start_date
        assert tournament.event_end_date == "2024-05-03T00:00:00.000Z"
        assert tournament.ranking_system == "MAIN"
        assert tournament.qualifying_format == "Matchplay"
        assert tournament.finals_format == "Single Elimination"
        assert tournament.stateprov == "CO"  # aliased from stateprov_code

    def test_get_director_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that getting non-existent director raises error."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/99999",
            status_code=404,
            json={"error": "Director not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.director(99999).get()

        assert exc_info.value.status_code == 404


class TestDirectorsIntegration:
    """Integration tests ensuring DirectorsClient and DirectorHandle work together."""

    def test_search_then_get_director(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of searching then getting director details."""
        # Mock search
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": 1000,
                        "name": "Josh Sharpe",
                        "city": "Portland",
                        "country_code": "US",
                    }
                ],
                "total_results": 1,
            },
        )

        # Mock get director
        mock_requests.get(
            "https://api.ifpapinball.com/director/1000",
            json={
                "director_id": 1000,
                "name": "Josh Sharpe",
                "city": "Portland",
                "stats": {"tournament_count": 42},
            },
        )

        client = IfpaClient(api_key="test-key")

        # Search for director
        search_results = client.directors.search(name="Josh")
        assert len(search_results.directors) == 1

        # Get full details using the ID from search
        director_id = search_results.directors[0].director_id
        full_director = client.director(director_id).get()

        assert full_director.director_id == 1000
        assert full_director.stats is not None
        assert full_director.stats.tournament_count == 42
