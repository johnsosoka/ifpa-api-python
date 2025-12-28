"""Unit tests for Phase 1 v4.0 standardization features.

Tests for:
- Response extraction overrides (_extract_results)
- Convenience methods (.get(), .get_or_none(), .exists())
- QueryBuilder convenience methods (.first(), .first_or_none())
- Parameter overwriting detection
"""

import pytest
import requests_mock

from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError

# ============================================================================
# Response Extraction Tests
# ============================================================================


class TestDirectorResponseExtraction:
    """Test that DirectorQueryBuilder._extract_results works correctly."""

    def test_iterate_works_with_directors_field(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .iterate() extracts results from 'directors' field."""
        # Mock paginated responses - need to handle multiple requests
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            [
                {
                    "json": {
                        "directors": [
                            {"director_id": 1, "name": "Director 1"},
                        ]
                    }
                },
                {"json": {"directors": []}},  # Empty page ends iteration
            ],
        )

        client = IfpaClient(api_key="test-key")
        results = list(client.director.query("Test").iterate(limit=1))

        assert len(results) == 1
        assert results[0].director_id == 1

    def test_get_all_works_with_directors_field(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_all() extracts results from 'directors' field."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            [
                {
                    "json": {
                        "directors": [
                            {"director_id": 1, "name": "Director 1"},
                            {"director_id": 2, "name": "Director 2"},
                        ]
                    }
                },
                {"json": {"directors": []}},
            ],
        )

        client = IfpaClient(api_key="test-key")
        results = client.director.query("Test").get_all()

        assert len(results) == 2


class TestTournamentResponseExtraction:
    """Test that TournamentQueryBuilder._extract_results works correctly."""

    def test_iterate_works_with_tournaments_field(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test .iterate() extracts results from 'tournaments' field."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            [
                {
                    "json": {
                        "tournaments": [
                            {"tournament_id": 1, "tournament_name": "Event 1"},
                        ]
                    }
                },
                {"json": {"tournaments": []}},
            ],
        )

        client = IfpaClient(api_key="test-key")
        results = list(client.tournament.query("Test").iterate(limit=1))

        assert len(results) == 1
        assert results[0].tournament_id == 1

    def test_get_all_works_with_tournaments_field(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test .get_all() extracts results from 'tournaments' field."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            [
                {
                    "json": {
                        "tournaments": [
                            {"tournament_id": 1, "tournament_name": "Event 1"},
                        ]
                    }
                },
                {"json": {"tournaments": []}},
            ],
        )

        client = IfpaClient(api_key="test-key")
        results = client.tournament.query("Test").get_all()

        assert len(results) == 1


# ============================================================================
# Convenience Methods Tests (.get(), .get_or_none(), .exists())
# ============================================================================


class TestPlayerConvenienceMethods:
    """Test player convenience methods."""

    def test_get_success(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get() returns player on success."""
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
        player = client.player.get(12345)

        assert player.player_id == 12345
        assert player.first_name == "John"

    def test_get_raises_on_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get() raises IfpaApiError on 404."""
        mock_requests.get("https://api.ifpapinball.com/player/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.player.get(99999)

        assert exc_info.value.status_code == 404

    def test_get_or_none_returns_player(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() returns player on success."""
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
        player = client.player.get_or_none(12345)

        assert player is not None
        assert player.player_id == 12345

    def test_get_or_none_returns_none_on_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() returns None on 404."""
        mock_requests.get("https://api.ifpapinball.com/player/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        player = client.player.get_or_none(99999)

        assert player is None

    def test_get_or_none_raises_on_non_404_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() raises on non-404 errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/12345",
            status_code=500,
            json={"error": "Server error"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.player.get_or_none(12345)

        assert exc_info.value.status_code == 500

    def test_exists_returns_true(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .exists() returns True when player exists."""
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
        assert client.player.exists(12345) is True

    def test_exists_returns_false(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .exists() returns False when player not found."""
        mock_requests.get("https://api.ifpapinball.com/player/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        assert client.player.exists(99999) is False


class TestDirectorConvenienceMethods:
    """Test director convenience methods."""

    def test_get_success(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get() returns director on success."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1533",
            json={
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Portland",
                "stateprov": "OR",
                "country_name": "United States",
                "country_code": "US",
            },
        )

        client = IfpaClient(api_key="test-key")
        director = client.director.get(1533)

        assert director.director_id == 1533
        assert director.name == "Josh Sharpe"

    def test_get_or_none_returns_none_on_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() returns None on 404."""
        mock_requests.get("https://api.ifpapinball.com/director/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        director = client.director.get_or_none(99999)

        assert director is None

    def test_exists_returns_true(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .exists() returns True when director exists."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/1533",
            json={
                "director_id": 1533,
                "name": "Josh Sharpe",
                "city": "Portland",
            },
        )

        client = IfpaClient(api_key="test-key")
        assert client.director.exists(1533) is True


class TestTournamentConvenienceMethods:
    """Test tournament convenience methods."""

    def test_get_success(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get() returns tournament on success."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/54321",
            json={
                "tournament_id": 54321,
                "tournament_name": "PAPA Championships",
                "event_date": "2024-01-15",
                "event_name": "PAPA",
            },
        )

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get(54321)

        assert tournament.tournament_id == 54321
        assert tournament.tournament_name == "PAPA Championships"

    def test_get_or_none_returns_none_on_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() returns None on 404."""
        mock_requests.get("https://api.ifpapinball.com/tournament/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        tournament = client.tournament.get_or_none(99999)

        assert tournament is None

    def test_exists_returns_false(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .exists() returns False when tournament not found."""
        mock_requests.get("https://api.ifpapinball.com/tournament/99999", status_code=404, json={})

        client = IfpaClient(api_key="test-key")
        assert client.tournament.exists(99999) is False


class TestSeriesConvenienceMethods:
    """Test series convenience methods."""

    def test_get_success(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get() returns series standings on success."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/overall_standings",
            json={
                "series_code": "NACS",
                "year": 2024,
                "championship_prize_fund": 10000.0,
                "overall_results": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series.get("NACS")

        assert standings.series_code == "NACS"

    def test_get_or_none_returns_none_on_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_or_none() returns None on 404."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/INVALID/overall_standings",
            status_code=404,
            json={},
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series.get_or_none("INVALID")

        assert standings is None

    def test_exists_returns_true(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .exists() returns True when series exists."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/overall_standings",
            json={
                "series_code": "NACS",
                "year": 2024,
                "championship_prize_fund": 0.0,
                "overall_results": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        assert client.series.exists("NACS") is True


# ============================================================================
# QueryBuilder Convenience Methods Tests (.first(), .first_or_none())
# ============================================================================


class TestQueryBuilderFirstMethods:
    """Test QueryBuilder .first() and .first_or_none() methods."""

    def test_first_returns_first_result(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first() returns first result when results exist."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "query": "Smith",
                "search": [
                    {"player_id": 1, "first_name": "John", "last_name": "Smith"},
                    {"player_id": 2, "first_name": "Jane", "last_name": "Smith"},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        first_player = client.player.query("Smith").first()

        assert first_player.player_id == 1
        assert first_player.first_name == "John"

    def test_first_raises_on_empty_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first() raises ValueError on empty results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"query": "NoMatch", "search": []},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(ValueError, match="No results found"):
            client.player.query("NoMatch").first()

    def test_first_or_none_returns_first_result(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first_or_none() returns first result when results exist."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={
                "directors": [
                    {
                        "director_id": 1,
                        "name": "Director One",
                        "city": "City 1",
                        "stateprov": "ST",
                        "country_code": "US",
                        "country_name": "United States",
                    },
                    {
                        "director_id": 2,
                        "name": "Director Two",
                        "city": "City 2",
                        "stateprov": "ST",
                        "country_code": "US",
                        "country_name": "United States",
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        first_director = client.director.query("Director").first_or_none()

        assert first_director is not None
        assert first_director.director_id == 1
        assert first_director.name == "Director One"

    def test_first_or_none_returns_none_on_empty_results(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test .first_or_none() returns None on empty results."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={"tournaments": []},
        )

        client = IfpaClient(api_key="test-key")
        first_tournament = client.tournament.query("NoMatch").first_or_none()

        assert first_tournament is None


# ============================================================================
# Parameter Overwriting Detection Tests
# ============================================================================


class TestLocationFiltersParameterOverwriting:
    """Test parameter overwriting detection in LocationFiltersMixin."""

    def test_country_overwrite_raises_error(self) -> None:
        """Test calling .country() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().country("US")

        with pytest.raises(ValueError, match="country\\(\\) called multiple times"):
            query.country("CA")

    def test_state_overwrite_raises_error(self) -> None:
        """Test calling .state() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().state("WA")

        with pytest.raises(ValueError, match="state\\(\\) called multiple times"):
            query.state("OR")

    def test_city_overwrite_raises_error(self) -> None:
        """Test calling .city() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.director.query().city("Seattle")

        with pytest.raises(ValueError, match="city\\(\\) called multiple times"):
            query.city("Portland")


class TestPaginationParameterOverwriting:
    """Test parameter overwriting detection in PaginationMixin."""

    def test_limit_overwrite_raises_error(self) -> None:
        """Test calling .limit() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().limit(10)

        with pytest.raises(ValueError, match="limit\\(\\) called multiple times"):
            query.limit(50)

    def test_offset_overwrite_raises_error(self) -> None:
        """Test calling .offset() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().offset(0)

        with pytest.raises(ValueError, match="offset\\(\\) called multiple times"):
            query.offset(25)


class TestPlayerQueryBuilderParameterOverwriting:
    """Test parameter overwriting detection in PlayerQueryBuilder."""

    def test_query_overwrite_raises_error(self) -> None:
        """Test calling .query() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        builder = client.player.query("John")

        with pytest.raises(ValueError, match="query\\(\\) called multiple times"):
            builder.query("Jane")

    def test_tournament_overwrite_raises_error(self) -> None:
        """Test calling .tournament() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().tournament("PAPA")

        with pytest.raises(ValueError, match="tournament\\(\\) called multiple times"):
            query.tournament("Pinburgh")

    def test_position_overwrite_raises_error(self) -> None:
        """Test calling .position() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().position(1)

        with pytest.raises(ValueError, match="position\\(\\) called multiple times"):
            query.position(2)


class TestDirectorQueryBuilderParameterOverwriting:
    """Test parameter overwriting detection in DirectorQueryBuilder."""

    def test_query_overwrite_raises_error(self) -> None:
        """Test calling .query() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        builder = client.director.query("Josh")

        with pytest.raises(ValueError, match="query\\(\\) called multiple times"):
            builder.query("John")


class TestTournamentQueryBuilderParameterOverwriting:
    """Test parameter overwriting detection in TournamentQueryBuilder."""

    def test_query_overwrite_raises_error(self) -> None:
        """Test calling .query() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        builder = client.tournament.query("PAPA")

        with pytest.raises(ValueError, match="query\\(\\) called multiple times"):
            builder.query("Pinburgh")

    def test_tournament_type_overwrite_raises_error(self) -> None:
        """Test calling .tournament_type() twice raises ValueError."""
        client = IfpaClient(api_key="test-key")
        query = client.tournament.query().tournament_type("open")

        with pytest.raises(ValueError, match="tournament_type\\(\\) called multiple times"):
            query.tournament_type("women")


class TestParameterOverwritingErrorMessages:
    """Test that error messages are helpful and include context."""

    def test_error_message_includes_previous_value(self) -> None:
        """Test error message shows previous value."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().country("US")

        with pytest.raises(ValueError) as exc_info:
            query.country("CA")

        error_msg = str(exc_info.value)
        assert "Previous value: 'US'" in error_msg
        assert "Attempted value: 'CA'" in error_msg

    def test_error_message_suggests_solution(self) -> None:
        """Test error message suggests creating new query."""
        client = IfpaClient(api_key="test-key")
        query = client.player.query().limit(10)

        with pytest.raises(ValueError) as exc_info:
            query.limit(50)

        error_msg = str(exc_info.value)
        assert "Create a new query" in error_msg or "likely a mistake" in error_msg
