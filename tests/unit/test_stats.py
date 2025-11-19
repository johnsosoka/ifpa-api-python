"""Unit tests for StatsClient.

Tests the stats resource client using mocked HTTP requests with real API responses.
"""

import json
from pathlib import Path
from typing import Any

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.stats import (
    CountryPlayersResponse,
    EventsAttendedPeriodResponse,
    EventsByYearResponse,
    LargestTournamentsResponse,
    LucrativeTournamentsResponse,
    OverallStatsResponse,
    PlayersByYearResponse,
    PointsGivenPeriodResponse,
    StatePlayersResponse,
    StateTournamentsResponse,
)


def load_fixture(filename: str) -> dict[str, Any]:
    """Load a fixture from scripts/stats_responses/.

    Args:
        filename: Name of the fixture file (e.g., "country_players_open.json")

    Returns:
        Parsed JSON fixture as a dictionary
    """
    fixture_path = Path(__file__).parent.parent.parent / "scripts" / "stats_responses" / filename
    with open(fixture_path) as f:
        return json.load(f)


class TestStatsClientCountryPlayers:
    """Test cases for country_players endpoint."""

    def test_country_players_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country_players with default parameters (OPEN)."""
        fixture = load_fixture("country_players_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/country_players", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.country_players()

        # Verify response structure
        assert isinstance(result, CountryPlayersResponse)
        assert result.type == "Players by Country"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry
        assert result.stats[0].country_name == "United States"
        assert result.stats[0].country_code == "US"
        assert result.stats[0].player_count == 47101
        assert result.stats[0].stats_rank == 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_country_players_with_rank_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country_players with WOMEN rank_type."""
        fixture = load_fixture("country_players_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/country_players", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.country_players(rank_type="WOMEN")

        # Verify rank_type parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "rank_type=" in mock_requests.last_request.query

        # Verify response
        assert result.rank_type == "WOMEN"
        assert len(result.stats) > 0


class TestStatsClientStatePlayers:
    """Test cases for state_players endpoint."""

    def test_state_players_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_players with default parameters (OPEN)."""
        fixture = load_fixture("state_players_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/state_players", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.state_players()

        # Verify response structure
        assert isinstance(result, StatePlayersResponse)
        assert result.type == "Players by State (North America)"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry
        first_state = result.stats[0]
        assert first_state.stateprov is not None
        assert first_state.player_count > 0
        assert first_state.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_state_players_with_rank_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_players with WOMEN rank_type."""
        fixture = load_fixture("state_players_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/state_players", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.state_players(rank_type="WOMEN")

        # Verify rank_type parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "rank_type=" in mock_requests.last_request.query

        # Verify response
        assert result.rank_type == "WOMEN"
        assert len(result.stats) > 0


class TestStatsClientStateTournaments:
    """Test cases for state_tournaments endpoint."""

    def test_state_tournaments_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_tournaments with default parameters (OPEN)."""
        fixture = load_fixture("state_tournaments_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/state_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.state_tournaments()

        # Verify response structure
        assert isinstance(result, StateTournamentsResponse)
        assert result.type == "Tournaments by State (North America)"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry has required fields
        first_state = result.stats[0]
        assert first_state.stateprov is not None
        assert first_state.tournament_count > 0
        assert first_state.total_points_all > 0
        assert first_state.total_points_tournament_value > 0
        assert first_state.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_state_tournaments_with_rank_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_tournaments with WOMEN rank_type."""
        fixture = load_fixture("state_tournaments_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/state_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.state_tournaments(rank_type="WOMEN")

        # Verify rank_type parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "rank_type=" in mock_requests.last_request.query

        # Verify response
        assert result.rank_type == "WOMEN"
        assert len(result.stats) > 0


class TestStatsClientEventsByYear:
    """Test cases for events_by_year endpoint."""

    def test_events_by_year_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_by_year with default parameters (OPEN)."""
        fixture = load_fixture("events_by_year_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_by_year", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_by_year()

        # Verify response structure
        assert isinstance(result, EventsByYearResponse)
        assert result.type == "Events Per Year"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry
        first_year = result.stats[0]
        assert first_year.year is not None
        assert first_year.country_count > 0
        assert first_year.tournament_count > 0
        assert first_year.player_count > 0
        assert first_year.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_events_by_year_with_rank_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_by_year with WOMEN rank_type."""
        fixture = load_fixture("events_by_year_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_by_year", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_by_year(rank_type="WOMEN")

        # Verify rank_type parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "rank_type=" in mock_requests.last_request.query

        # Verify response
        assert result.rank_type == "WOMEN"

    def test_events_by_year_with_country_code(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_by_year with country_code filter."""
        fixture = load_fixture("events_by_year_us.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_by_year", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_by_year(country_code="US")

        # Verify country_code parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "country_code=" in mock_requests.last_request.query

        # Verify response
        assert isinstance(result, EventsByYearResponse)
        assert len(result.stats) > 0


class TestStatsClientPlayersByYear:
    """Test cases for players_by_year endpoint."""

    def test_players_by_year(self, mock_requests: requests_mock.Mocker) -> None:
        """Test players_by_year with no parameters."""
        fixture = load_fixture("players_by_year.json")
        mock_requests.get("https://api.ifpapinball.com/stats/players_by_year", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.players_by_year()

        # Verify response structure
        assert isinstance(result, PlayersByYearResponse)
        assert result.type == "Players by Year"
        assert len(result.stats) > 0

        # Verify first entry
        first_year = result.stats[0]
        assert first_year.year is not None
        assert first_year.current_year_count > 0
        assert first_year.previous_year_count >= 0
        assert first_year.previous_2_year_count >= 0
        assert first_year.stats_rank >= 1

        # Verify no params sent (no parameters for this endpoint)
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}


class TestStatsClientLargestTournaments:
    """Test cases for largest_tournaments endpoint."""

    def test_largest_tournaments_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test largest_tournaments with default parameters (OPEN)."""
        fixture = load_fixture("largest_tournaments_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/largest_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.largest_tournaments()

        # Verify response structure
        assert isinstance(result, LargestTournamentsResponse)
        assert result.type == "Largest Tournaments"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry
        first_tourney = result.stats[0]
        assert first_tourney.country_name is not None
        assert first_tourney.country_code is not None
        assert first_tourney.player_count > 0
        assert first_tourney.tournament_id > 0
        assert first_tourney.tournament_name is not None
        assert first_tourney.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_largest_tournaments_with_rank_type(self, mock_requests: requests_mock.Mocker) -> None:
        """Test largest_tournaments with WOMEN rank_type."""
        fixture = load_fixture("largest_tournaments_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/largest_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.largest_tournaments(rank_type="WOMEN")

        # Verify rank_type parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "rank_type=" in mock_requests.last_request.query

        # Verify response
        assert result.rank_type == "WOMEN"

    def test_largest_tournaments_with_country_code(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test largest_tournaments with country_code filter."""
        fixture = load_fixture("largest_tournaments_us.json")
        mock_requests.get("https://api.ifpapinball.com/stats/largest_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.largest_tournaments(country_code="US")

        # Verify country_code parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "country_code=" in mock_requests.last_request.query

        # Verify response
        assert isinstance(result, LargestTournamentsResponse)


class TestStatsClientLucrativeTournaments:
    """Test cases for lucrative_tournaments endpoint."""

    def test_lucrative_tournaments_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test lucrative_tournaments with default parameters (major=Y)."""
        fixture = load_fixture("lucrative_tournaments_major_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/lucrative_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.lucrative_tournaments()

        # Verify response structure
        assert isinstance(result, LucrativeTournamentsResponse)
        assert result.type == "Lucrative Tournaments"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify first entry
        first_tourney = result.stats[0]
        assert first_tourney.country_name is not None
        assert first_tourney.country_code is not None
        assert first_tourney.tournament_id > 0
        assert first_tourney.tournament_name is not None
        assert first_tourney.tournament_value > 0
        assert first_tourney.stats_rank >= 1

        # Verify no params sent for default (major=Y is default)
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_lucrative_tournaments_non_major(self, mock_requests: requests_mock.Mocker) -> None:
        """Test lucrative_tournaments with major=N."""
        fixture = load_fixture("lucrative_tournaments_non_major.json")
        mock_requests.get("https://api.ifpapinball.com/stats/lucrative_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.lucrative_tournaments(major="N")

        # Verify major parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "major=" in mock_requests.last_request.query

        # Verify response
        assert isinstance(result, LucrativeTournamentsResponse)

    def test_lucrative_tournaments_with_country_code(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test lucrative_tournaments with country_code filter."""
        fixture = load_fixture("lucrative_tournaments_us.json")
        mock_requests.get("https://api.ifpapinball.com/stats/lucrative_tournaments", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.lucrative_tournaments(country_code="US")

        # Verify country_code parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "country_code=" in mock_requests.last_request.query

        # Verify response
        assert isinstance(result, LucrativeTournamentsResponse)


class TestStatsClientPointsGivenPeriod:
    """Test cases for points_given_period endpoint."""

    def test_points_given_period_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test points_given_period with default parameters."""
        fixture = load_fixture("points_given_period_default.json")
        mock_requests.get("https://api.ifpapinball.com/stats/points_given_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.points_given_period()

        # Verify response structure
        assert isinstance(result, PointsGivenPeriodResponse)
        assert result.type == "Points given Period"
        assert result.rank_type == "OPEN"
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.return_count > 0
        assert len(result.stats) > 0

        # Verify first entry
        first_player = result.stats[0]
        assert first_player.player_id > 0
        assert first_player.first_name is not None
        assert first_player.last_name is not None
        assert first_player.country_name is not None
        assert first_player.wppr_points > 0
        assert first_player.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_points_given_period_with_date_range(self, mock_requests: requests_mock.Mocker) -> None:
        """Test points_given_period with start_date and end_date."""
        fixture = load_fixture("points_given_period_2024.json")
        mock_requests.get("https://api.ifpapinball.com/stats/points_given_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.points_given_period(start_date="2024-01-01", end_date="2024-12-31")

        # Verify date parameters were passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=" in query
        assert "end_date=" in query

        # Verify response
        assert isinstance(result, PointsGivenPeriodResponse)

    def test_points_given_period_with_limit(self, mock_requests: requests_mock.Mocker) -> None:
        """Test points_given_period with limit parameter."""
        fixture = load_fixture("points_given_period_2024_limit10.json")
        mock_requests.get("https://api.ifpapinball.com/stats/points_given_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.points_given_period(
            start_date="2024-01-01", end_date="2024-12-31", limit=10
        )

        # Verify all parameters were passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=" in query
        assert "end_date=" in query
        assert "limit=" in query

        # Verify response
        assert isinstance(result, PointsGivenPeriodResponse)
        # Note: API returns 25 results regardless of limit in this fixture
        assert result.return_count == 25

    def test_points_given_period_all_params(self, mock_requests: requests_mock.Mocker) -> None:
        """Test points_given_period with all parameters except rank_type.

        Note: rank_type="OPEN" is the default so it's not sent as a parameter.
        """
        fixture = load_fixture("points_given_period_us_2024.json")
        mock_requests.get("https://api.ifpapinball.com/stats/points_given_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.points_given_period(
            country_code="US",
            start_date="2024-01-01",
            end_date="2024-12-31",
            limit=25,
        )

        # Verify all parameters were passed (except rank_type which defaults to OPEN)
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country_code=" in query
        assert "start_date=" in query
        assert "end_date=" in query
        assert "limit=" in query

        # Verify response
        assert isinstance(result, PointsGivenPeriodResponse)


class TestStatsClientEventsAttendedPeriod:
    """Test cases for events_attended_period endpoint."""

    def test_events_attended_period_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_attended_period with default parameters."""
        fixture = load_fixture("events_attended_period_default.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_attended_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_attended_period()

        # Verify response structure
        assert isinstance(result, EventsAttendedPeriodResponse)
        assert result.type == "Events attended over a period of time"
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.return_count > 0
        assert len(result.stats) > 0

        # Verify first entry
        first_player = result.stats[0]
        assert first_player.player_id > 0
        assert first_player.first_name is not None
        assert first_player.last_name is not None
        assert first_player.country_name is not None
        assert first_player.tournament_count > 0
        assert first_player.stats_rank >= 1

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_events_attended_period_with_date_range(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test events_attended_period with start_date and end_date."""
        fixture = load_fixture("events_attended_period_2024.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_attended_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_attended_period(start_date="2024-01-01", end_date="2024-12-31")

        # Verify date parameters were passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=" in query
        assert "end_date=" in query

        # Verify response
        assert isinstance(result, EventsAttendedPeriodResponse)

    def test_events_attended_period_with_limit(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_attended_period with limit parameter."""
        fixture = load_fixture("events_attended_period_2024_limit10.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_attended_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_attended_period(
            start_date="2024-01-01", end_date="2024-12-31", limit=10
        )

        # Verify all parameters were passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "start_date=" in query
        assert "end_date=" in query
        assert "limit=" in query

        # Verify response
        assert isinstance(result, EventsAttendedPeriodResponse)
        # Note: API returns 25 results regardless of limit in this fixture
        assert result.return_count == 25

    def test_events_attended_period_all_params(self, mock_requests: requests_mock.Mocker) -> None:
        """Test events_attended_period with all parameters except rank_type.

        Note: rank_type="OPEN" is the default so it's not sent as a parameter.
        """
        fixture = load_fixture("events_attended_period_us_2024.json")
        mock_requests.get("https://api.ifpapinball.com/stats/events_attended_period", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.events_attended_period(
            country_code="US",
            start_date="2024-01-01",
            end_date="2024-12-31",
            limit=25,
        )

        # Verify all parameters were passed (except rank_type which defaults to OPEN)
        assert mock_requests.called
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "country_code=" in query
        assert "start_date=" in query
        assert "end_date=" in query
        assert "limit=" in query

        # Verify response
        assert isinstance(result, EventsAttendedPeriodResponse)


class TestStatsClientOverall:
    """Test cases for overall endpoint."""

    def test_overall_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test overall with default system_code (OPEN)."""
        fixture = load_fixture("overall_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/overall", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.overall()

        # Verify response structure
        assert isinstance(result, OverallStatsResponse)
        assert result.type == "Overall Stats"
        assert result.system_code == "OPEN"

        # Verify stats object (note: single object, not array)
        stats = result.stats
        assert stats.overall_player_count > 0
        assert stats.active_player_count > 0
        assert stats.tournament_count > 0
        assert stats.tournament_count_last_month >= 0
        assert stats.tournament_count_this_year >= 0
        assert stats.tournament_player_count > 0
        assert stats.tournament_player_count_average > 0

        # Verify age distribution
        assert stats.age.age_under_18 >= 0
        assert stats.age.age_18_to_29 >= 0
        assert stats.age.age_30_to_39 >= 0
        assert stats.age.age_40_to_49 >= 0
        assert stats.age.age_50_to_99 >= 0

        # Verify no params sent for default
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_overall_with_system_code(self, mock_requests: requests_mock.Mocker) -> None:
        """Test overall with system_code=WOMEN.

        Note: As of 2025-11-19, this is a known API bug where WOMEN returns OPEN data.
        We test that the parameter is correctly passed to the API.
        """
        fixture = load_fixture("overall_women.json")
        mock_requests.get("https://api.ifpapinball.com/stats/overall", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.overall(system_code="WOMEN")

        # Verify system_code parameter was passed
        assert mock_requests.called
        assert mock_requests.last_request is not None
        assert "system_code=" in mock_requests.last_request.query

        # Verify response
        assert isinstance(result, OverallStatsResponse)


class TestStatsClientErrors:
    """Test error handling for stats client."""

    def test_stats_handles_api_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that stats properly handles API errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            status_code=503,
            json={"error": "Service temporarily unavailable"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.stats.country_players()

        assert exc_info.value.status_code == 503

    def test_stats_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that stats handles not found errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/overall",
            status_code=404,
            json={"error": "Endpoint not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.stats.overall()

        assert exc_info.value.status_code == 404


class TestStatsClientFieldCoercion:
    """Test that field validators properly coerce string values to correct types."""

    def test_country_players_coerces_player_count(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that player_count is coerced from string to int."""
        fixture = load_fixture("country_players_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/country_players", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.country_players()

        # Verify that player_count (returned as string "47101") is coerced to int
        assert isinstance(result.stats[0].player_count, int)
        assert result.stats[0].player_count == 47101

    def test_overall_returns_proper_numeric_types(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that overall endpoint returns proper numeric types (not strings).

        Unlike other stats endpoints, overall returns proper int/float types.
        """
        fixture = load_fixture("overall_open.json")
        mock_requests.get("https://api.ifpapinball.com/stats/overall", json=fixture)

        client = IfpaClient(api_key="test-key")
        result = client.stats.overall()

        # Verify proper types
        assert isinstance(result.stats.overall_player_count, int)
        assert isinstance(result.stats.tournament_player_count_average, float)
        assert isinstance(result.stats.age.age_under_18, float)
