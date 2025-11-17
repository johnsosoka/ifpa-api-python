"""Unit tests for DirectorClient and callable pattern.

Tests the director resource client and callable pattern using mocked HTTP requests.
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


class TestDirectorClient:
    """Test cases for DirectorClient collection-level operations."""

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
        result = client.director.query("Josh").get()

        assert isinstance(result, DirectorSearchResponse)
        assert len(result.directors) == 1
        assert result.directors[0].director_id == 1000
        assert result.directors[0].name == "Josh Sharpe"
        # count field aliased to total_results for backward compatibility
        assert result.count == 1

        # Verify request was made correctly
        assert mock_requests.last_request is not None
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
        result = client.director.query().city("Chicago").state("IL").country("US").get()

        assert len(result.directors) == 1
        assert result.directors[0].city == "Chicago"

        # Verify all query params were sent
        assert mock_requests.last_request is not None
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
        result = client.director.query().get()

        assert isinstance(result, DirectorSearchResponse)
        assert len(result.directors) == 0
        assert mock_requests.last_request is not None
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
            client.director.query("test").get()

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
        result = client.director.query("sharpe").get()

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
                "country_directors": [
                    {
                        "player_profile": {
                            "player_id": 5000,
                            "name": "Country Director 1",
                            "country_code": "US",
                            "country_name": "United States",
                            "profile_photo": "",
                        }
                    },
                    {
                        "player_profile": {
                            "player_id": 5001,
                            "name": "Country Director 2",
                            "country_code": "CA",
                            "country_name": "Canada",
                            "profile_photo": "",
                        }
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.director.country_directors()

        assert isinstance(result, CountryDirectorsResponse)
        assert len(result.country_directors) == 2
        assert result.country_directors[0].player_profile.player_id == 5000
        assert result.country_directors[0].player_profile.country_code == "US"
        assert result.country_directors[1].player_profile.country_name == "Canada"

    def test_country_directors_with_spec_fields(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country directors with API spec format (count and profile_photo)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "count": 2,
                "country_directors": [
                    {
                        "player_profile": {
                            "player_id": 5000,
                            "name": "Josh Sharpe",
                            "country_code": "US",
                            "country_name": "United States",
                            "profile_photo": "https://example.com/photo.jpg",
                        }
                    },
                    {
                        "player_profile": {
                            "player_id": 5001,
                            "name": "Jane Doe",
                            "country_code": "CA",
                            "country_name": "Canada",
                            "profile_photo": "https://example.com/photo2.jpg",
                        }
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.director.country_directors()

        assert isinstance(result, CountryDirectorsResponse)
        assert result.count == 2
        assert len(result.country_directors) == 2
        assert (
            result.country_directors[0].player_profile.profile_photo
            == "https://example.com/photo.jpg"
        )
        assert (
            result.country_directors[1].player_profile.profile_photo
            == "https://example.com/photo2.jpg"
        )


class TestDirectorContext:
    """Test cases for DirectorContext resource-specific operations."""

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
        director = client.director(1000).details()

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
        director = client.director("1000").details()

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
        # Should accept TimePeriod enum
        from ifpa_api.models.common import TimePeriod

        result = client.director(1000).tournaments(TimePeriod.PAST)

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
            client.director(99999).details()

        assert exc_info.value.status_code == 404


class TestDirectorQueryBuilder:
    """Test cases for the new fluent query builder pattern."""

    def test_simple_query(self, mock_requests: requests_mock.Mocker) -> None:
        """Test simple director name query."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": 1000,
                        "name": "Josh Sharpe",
                        "city": "Chicago",
                        "country_code": "US",
                        "tournament_count": 42,
                    }
                ],
                "total_results": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.director.query("Josh").get()

        assert isinstance(results, DirectorSearchResponse)
        assert len(results.directors) == 1
        assert results.directors[0].name == "Josh Sharpe"

        # Verify query parameter was sent correctly
        assert mock_requests.last_request is not None
        assert "name=josh" in mock_requests.last_request.query.lower()

    def test_query_with_country_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with country filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Josh").country("US").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=josh" in query.lower()
        assert "country=us" in query.lower()

    def test_query_with_state_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with state filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Sharpe").state("IL").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=sharpe" in query.lower()
        assert "stateprov=il" in query.lower()

    def test_query_with_city_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with city filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Josh").city("Chicago").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=josh" in query.lower()
        assert "city=chicago" in query.lower()

    def test_query_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with pagination (offset and limit)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Sharpe").offset(25).limit(50).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=25" in query
        assert "count=50" in query

    def test_query_chaining_all_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test chaining all available filters together."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Josh").country("US").state("IL").city("Chicago").offset(0).limit(
            25
        ).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=josh" in query.lower()
        assert "country=us" in query.lower()
        assert "stateprov=il" in query.lower()
        assert "city=chicago" in query.lower()
        assert "start_pos=0" in query
        assert "count=25" in query

    def test_query_immutability(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query builder is immutable - each method returns new instance."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create base query
        base_query = client.director.query().country("US")

        # Create two derivative queries
        il_query = base_query.state("IL")
        or_query = base_query.state("OR")

        # Execute both queries
        il_query.get()
        il_request = mock_requests.last_request
        assert il_request is not None
        assert "stateprov=il" in il_request.query.lower()
        assert "stateprov=or" not in il_request.query.lower()

        or_query.get()
        or_request = mock_requests.last_request
        assert or_request is not None
        assert "stateprov=or" in or_request.query.lower()
        assert "stateprov=il" not in or_request.query.lower()

        # Verify both queries have country=US
        assert "country=us" in il_request.query.lower()
        assert "country=us" in or_request.query.lower()

    def test_query_reuse(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query can be reused multiple times (immutability)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create a reusable query
        us_query = client.director.query().country("US")

        # Execute it multiple times with different additional filters
        us_query.state("IL").city("Chicago").get()
        us_query.state("OR").city("Portland").get()
        us_query.state("WA").city("Seattle").get()

        # Base query should still be unchanged
        us_query.get()
        final_request = mock_requests.last_request
        assert final_request is not None
        assert "country=us" in final_request.query.lower()
        # Should not have any of the state/city filters from previous calls
        assert "stateprov" not in final_request.query.lower()
        assert "city" not in final_request.query.lower()

    def test_empty_query(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query with no name (filter-only query)."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query().country("US").state("IL").get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country=us" in query.lower()
        assert "stateprov=il" in query.lower()
        # Should not have a name parameter
        assert "name=" not in query.lower()

    def test_query_with_initial_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test query() method with initial name parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        # Test both ways of setting name
        client.director.query("Josh").get()
        assert mock_requests.last_request is not None
        assert "name=josh" in mock_requests.last_request.query.lower()

        # Also test chaining after initial name
        client.director.query("Sharpe").country("US").get()
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=sharpe" in query.lower()
        assert "country=us" in query.lower()

    def test_query_builder_repr(self) -> None:
        """Test query builder string representation."""
        client = IfpaClient(api_key="test-key")
        builder = client.director.query("Josh").country("US")

        # Should show class name and params
        repr_str = repr(builder)
        assert "DirectorQueryBuilder" in repr_str
        assert "params=" in repr_str

    def test_query_method_chaining(self, mock_requests: requests_mock.Mocker) -> None:
        """Test fluent chaining of query methods."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Test fluent chaining with parentheses
        results = (
            client.director.query("Josh").country("US").state("IL").city("Chicago").limit(25).get()
        )

        assert isinstance(results, DirectorSearchResponse)
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "name=josh" in query.lower()
        assert "country=us" in query.lower()
        assert "stateprov=il" in query.lower()
        assert "city=chicago" in query.lower()
        assert "count=25" in query

    def test_query_offset_without_limit(self, mock_requests: requests_mock.Mocker) -> None:
        """Test using offset without limit."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")
        client.director.query("Josh").offset(50).get()

        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_pos=50" in query
        assert "count=" not in query


class TestDirectorQueryBuilderIntegration:
    """Integration tests for query builder with realistic scenarios."""

    def test_search_and_refine_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test realistic workflow: search broadly, then refine."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": i,
                        "name": f"Director{i}",
                        "city": "Chicago",
                        "country_code": "US",
                    }
                    for i in range(50)
                ],
                "total_results": 50,
            },
        )

        client = IfpaClient(api_key="test-key")

        # Start with broad search
        broad_results = client.director.query("Director").limit(100).get()
        assert len(broad_results.directors) == 50

        # Refine to specific country
        client.director.query("Director").country("US").limit(50).get()
        assert mock_requests.last_request is not None
        assert "country=us" in mock_requests.last_request.query.lower()

    def test_pagination_workflow(self, mock_requests: requests_mock.Mocker) -> None:
        """Test paginating through results."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [], "total_results": 0},
        )

        client = IfpaClient(api_key="test-key")

        # Create base query
        base = client.director.query("Sharpe").country("US")

        # Get pages
        page1 = base.offset(0).limit(25)
        page2 = base.offset(25).limit(25)
        page3 = base.offset(50).limit(25)

        # Execute pages
        page1.get()
        assert "start_pos=0" in mock_requests.last_request.query
        page2.get()
        assert "start_pos=25" in mock_requests.last_request.query
        page3.get()
        assert "start_pos=50" in mock_requests.last_request.query


# TestDeprecationWarnings class removed - search() method has been removed in favor of query()


class TestDirectorIntegration:
    """Integration tests ensuring DirectorClient and callable pattern work together."""

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

        # Search for director using query builder
        search_results = client.director.query("Josh").get()
        assert len(search_results.directors) == 1

        # Get full details using the ID from search
        director_id = search_results.directors[0].director_id
        full_director = client.director(director_id).details()

        assert full_director.director_id == 1000
        assert full_director.stats is not None
        assert full_director.stats.tournament_count == 42
