"""Unit tests for StatsClient.

Tests the stats resource client using mocked HTTP requests with real API responses.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import MajorTournament, StatsRankType, SystemCode
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


class TestStatsClientCountryPlayers:
    """Test cases for country_players endpoint."""

    def test_country_players_default(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country_players with default parameters (OPEN)."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "47101",
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "Canada",
                        "country_code": "CA",
                        "player_count": "4473",
                        "stats_rank": 2,
                    },
                    {
                        "country_name": "Australia",
                        "country_code": "AU",
                        "player_count": "3385",
                        "stats_rank": 3,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "7173",
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "Canada",
                        "country_code": "CA",
                        "player_count": "862",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_players",
            json={
                "type": "Players by State (North America)",
                "rank_type": "OPEN",
                "stats": [
                    {"stateprov": "Unknown", "player_count": "38167", "stats_rank": 1},
                    {"stateprov": "CA", "player_count": "662", "stats_rank": 2},
                    {"stateprov": "WA", "player_count": "549", "stats_rank": 3},
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_players",
            json={
                "type": "Players by State (North America)",
                "rank_type": "WOMEN",
                "stats": [
                    {"stateprov": "Unknown", "player_count": "5182", "stats_rank": 1},
                    {"stateprov": "CA", "player_count": "131", "stats_rank": 2},
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_tournaments",
            json={
                "type": "Tournaments by State (North America)",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "stateprov": "WA",
                        "tournament_count": "5729",
                        "total_points_all": "232841.4800",
                        "total_points_tournament_value": "39232.8200",
                        "stats_rank": 1,
                    },
                    {
                        "stateprov": "MI",
                        "tournament_count": "3469",
                        "total_points_all": "122382.2200",
                        "total_points_tournament_value": "29354.8200",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_tournaments",
            json={
                "type": "Tournaments by State (North America)",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "stateprov": "TX",
                        "tournament_count": "458",
                        "total_points_all": "21036.1100",
                        "total_points_tournament_value": "5084.3200",
                        "stats_rank": 1,
                    },
                    {
                        "stateprov": "MI",
                        "tournament_count": "349",
                        "total_points_all": "2424.3000",
                        "total_points_tournament_value": "1104.8000",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_by_year",
            json={
                "type": "Events Per Year",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "year": "2025",
                        "country_count": "30",
                        "tournament_count": "12300",
                        "player_count": "277684",
                        "stats_rank": 1,
                    },
                    {
                        "year": "2024",
                        "country_count": "25",
                        "tournament_count": "12776",
                        "player_count": "291118",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_by_year",
            json={
                "type": "Events Per Year",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "year": "2025",
                        "country_count": "15",
                        "tournament_count": "1686",
                        "player_count": "22992",
                        "stats_rank": 1,
                    },
                    {
                        "year": "2024",
                        "country_count": "10",
                        "tournament_count": "1597",
                        "player_count": "20927",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_by_year",
            json={
                "type": "Events Per Year",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "year": "2025",
                        "country_count": "1",
                        "tournament_count": "9680",
                        "player_count": "209880",
                        "stats_rank": 1,
                    },
                    {
                        "year": "2024",
                        "country_count": "1",
                        "tournament_count": "10042",
                        "player_count": "221107",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/players_by_year",
            json={
                "type": "Players by Year",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "year": "2025",
                        "current_year_count": "39169",
                        "previous_year_count": "18453",
                        "previous_2_year_count": "8278",
                        "stats_rank": 1,
                    },
                    {
                        "year": "2024",
                        "current_year_count": "38914",
                        "previous_year_count": "14683",
                        "previous_2_year_count": "6707",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/largest_tournaments",
            json={
                "type": "Largest Tournaments",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "987",
                        "tournament_id": "34625",
                        "tournament_name": "Pinburgh Match-Play Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2019-08-03",
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "822",
                        "tournament_id": "26092",
                        "tournament_name": "Pinburgh Match-Play Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2018-07-28",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/largest_tournaments",
            json={
                "type": "Largest Tournaments",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "127",
                        "tournament_id": "34627",
                        "tournament_name": "Women's International Pinball Tournament",
                        "event_name": "Main Tournament",
                        "tournament_date": "2019-08-04",
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "86",
                        "tournament_id": "103188",
                        "tournament_name": "Expo flipOUT! Womens Big Bracket",
                        "event_name": "Womens Division",
                        "tournament_date": "2025-10-18",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/largest_tournaments",
            json={
                "type": "Largest Tournaments",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "987",
                        "tournament_id": "34625",
                        "tournament_name": "Pinburgh Match-Play Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2019-08-03",
                        "stats_rank": 1,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/lucrative_tournaments",
            json={
                "type": "Lucrative Tournaments",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "83318",
                        "tournament_name": "The Open - IFPA World Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2025-01-26",
                        "tournament_value": 400.79,
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "78171",
                        "tournament_name": "IFPA World Pinball Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2024-06-09",
                        "tournament_value": 393.28,
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/lucrative_tournaments",
            json={
                "type": "Lucrative Tournaments",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "83321",
                        "tournament_name": "It Never Drains in Southern California",
                        "event_name": "Classics",
                        "tournament_date": "2025-01-25",
                        "tournament_value": 281.01,
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "66353",
                        "tournament_name": "It Never Drains in Southern California",
                        "event_name": "Classics",
                        "tournament_date": "2024-01-06",
                        "tournament_value": 266.56,
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/lucrative_tournaments",
            json={
                "type": "Lucrative Tournaments",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "83318",
                        "tournament_name": "The Open - IFPA World Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2025-01-26",
                        "tournament_value": 400.79,
                        "stats_rank": 1,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            json={
                "type": "Points given Period",
                "start_date": "'2024-11-19'",
                "end_date": "2025-11-19",
                "return_count": 25,
                "rank_type": "OPEN",
                "stats": [
                    {
                        "player_id": "49549",
                        "first_name": "Arvid",
                        "last_name": "Flygare",
                        "country_name": "Sweden",
                        "country_code": "SE",
                        "wppr_points": "4033.46",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "16004",
                        "first_name": "Viggo",
                        "last_name": "Löwgren",
                        "country_name": "Sweden",
                        "country_code": "SE",
                        "wppr_points": "3854.59",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            json={
                "type": "Points given Period",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "rank_type": "OPEN",
                "stats": [
                    {
                        "player_id": "1605",
                        "first_name": "Escher",
                        "last_name": "Lefkoff",
                        "country_name": "Australia",
                        "country_code": "AU",
                        "wppr_points": "4264.61",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "16004",
                        "first_name": "Viggo",
                        "last_name": "Löwgren",
                        "country_name": "Sweden",
                        "country_code": "SE",
                        "wppr_points": "3049.80",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            json={
                "type": "Points given Period",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "rank_type": "OPEN",
                "stats": [
                    {
                        "player_id": "1605",
                        "first_name": "Escher",
                        "last_name": "Lefkoff",
                        "country_name": "Australia",
                        "country_code": "AU",
                        "wppr_points": "4264.61",
                        "stats_rank": 1,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            json={
                "type": "Points given Period",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "rank_type": "OPEN",
                "stats": [
                    {
                        "player_id": "40612",
                        "first_name": "Carlos",
                        "last_name": "Delaserda",
                        "country_name": "United States",
                        "country_code": "US",
                        "wppr_points": "2986.50",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "8202",
                        "first_name": "Zach",
                        "last_name": "McCarthy",
                        "country_name": "United States",
                        "country_code": "US",
                        "wppr_points": "2940.96",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_attended_period",
            json={
                "type": "Events attended over a period of time",
                "start_date": "'2024-11-19'",
                "end_date": "2025-11-19",
                "return_count": 25,
                "stats": [
                    {
                        "player_id": "91929",
                        "first_name": "Nick",
                        "last_name": "Elliott",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "202",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "55991",
                        "first_name": "Dawnda",
                        "last_name": "Durbin",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "200",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_attended_period",
            json={
                "type": "Events attended over a period of time",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "stats": [
                    {
                        "player_id": "89391",
                        "first_name": "Ben",
                        "last_name": "Fodor",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "199",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "55991",
                        "first_name": "Dawnda",
                        "last_name": "Durbin",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "188",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_attended_period",
            json={
                "type": "Events attended over a period of time",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "stats": [
                    {
                        "player_id": "89391",
                        "first_name": "Ben",
                        "last_name": "Fodor",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "199",
                        "stats_rank": 1,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_attended_period",
            json={
                "type": "Events attended over a period of time",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "return_count": 25,
                "stats": [
                    {
                        "player_id": "89391",
                        "first_name": "Ben",
                        "last_name": "Fodor",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "199",
                        "stats_rank": 1,
                    },
                    {
                        "player_id": "55991",
                        "first_name": "Dawnda",
                        "last_name": "Durbin",
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_count": "188",
                        "stats_rank": 2,
                    },
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/overall",
            json={
                "type": "Overall Stats",
                "system_code": "OPEN",
                "stats": {
                    "overall_player_count": 143756,
                    "active_player_count": 71907,
                    "tournament_count": 85392,
                    "tournament_count_last_month": 1202,
                    "tournament_count_this_year": 14088,
                    "tournament_player_count": 1956522,
                    "tournament_player_count_average": 22.9,
                    "age": {
                        "age_under_18": 3.47,
                        "age_18_to_29": 9.4,
                        "age_30_to_39": 22.7,
                        "age_40_to_49": 31.07,
                        "age_50_to_99": 33.36,
                    },
                },
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/overall",
            json={
                "type": "Overall Stats",
                "system_code": "OPEN",
                "stats": {
                    "overall_player_count": 143756,
                    "active_player_count": 71907,
                    "tournament_count": 85392,
                    "tournament_count_last_month": 1202,
                    "tournament_count_this_year": 14088,
                    "tournament_player_count": 1956522,
                    "tournament_player_count_average": 22.9,
                    "age": {
                        "age_under_18": 3.47,
                        "age_18_to_29": 9.4,
                        "age_30_to_39": 22.7,
                        "age_40_to_49": 31.07,
                        "age_50_to_99": 33.36,
                    },
                },
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "47101",
                        "stats_rank": 1,
                    }
                ],
            },
        )

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
        mock_requests.get(
            "https://api.ifpapinball.com/stats/overall",
            json={
                "type": "Overall Stats",
                "system_code": "OPEN",
                "stats": {
                    "overall_player_count": 143756,
                    "active_player_count": 71907,
                    "tournament_count": 85392,
                    "tournament_count_last_month": 1202,
                    "tournament_count_this_year": 14088,
                    "tournament_player_count": 1956522,
                    "tournament_player_count_average": 22.9,
                    "age": {
                        "age_under_18": 3.47,
                        "age_18_to_29": 9.4,
                        "age_30_to_39": 22.7,
                        "age_40_to_49": 31.07,
                        "age_50_to_99": 33.36,
                    },
                },
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.stats.overall()

        # Verify proper types
        assert isinstance(result.stats.overall_player_count, int)
        assert isinstance(result.stats.tournament_player_count_average, float)
        assert isinstance(result.stats.age.age_under_18, float)


class TestStatsClientEdgeCases:
    """Test edge cases and error handling for stats client."""

    def test_country_players_empty_response(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country_players handles empty stats array."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={"type": "Players by Country", "rank_type": "OPEN", "stats": []},
        )

        client = IfpaClient(api_key="test-key")
        result = client.stats.country_players()

        assert isinstance(result, CountryPlayersResponse)
        assert len(result.stats) == 0
        assert result.type == "Players by Country"

    def test_country_players_missing_required_field(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test country_players raises validation error for missing required fields."""
        from pydantic import ValidationError

        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "OPEN",
                "stats": [{"country_name": "US"}],  # Missing player_count, stats_rank
            },
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(ValidationError):
            client.stats.country_players()

    def test_points_given_period_invalid_date_format(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test points_given_period with invalid date passes to API for validation."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            status_code=400,
            json={"error": "Invalid date format"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.stats.points_given_period(start_date="not-a-date", end_date="also-not-a-date")

        assert exc_info.value.status_code == 400

    def test_points_given_period_empty_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test points_given_period handles empty stats array gracefully."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            json={
                "type": "Points Given in Period",
                "rank_type": "OPEN",
                "start_date": "1900-01-01",
                "end_date": "1900-01-31",
                "return_count": 0,
                "stats": [],  # Empty array - no data in this period
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.stats.points_given_period(start_date="1900-01-01", end_date="1900-01-31")

        assert isinstance(result, PointsGivenPeriodResponse)
        assert result.return_count == 0
        assert len(result.stats) == 0
        assert result.stats == []

    def test_country_players_malformed_response(self, mock_requests: requests_mock.Mocker) -> None:
        """Test handling of API response missing required fields."""
        from pydantic import ValidationError

        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                # Missing rank_type field
                "stats": [
                    {
                        "country_name": "United States",
                        # Missing player_count field
                        "tournament_count": 1234,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")

        # Should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            client.stats.country_players()

        # Verify error mentions the missing field
        error_str = str(exc_info.value).lower()
        assert "player_count" in error_str and (
            "field required" in error_str or "missing" in error_str
        )

    def test_period_endpoint_invalid_date_format(self, mock_requests: requests_mock.Mocker) -> None:
        """Test period endpoint with incorrectly formatted date."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/points_given_period",
            status_code=400,
            json={"error": "Invalid date format"},
        )

        client = IfpaClient(api_key="test-key")

        # Try with US-style date instead of ISO 8601
        with pytest.raises(IfpaApiError) as exc_info:
            client.stats.points_given_period(
                start_date="01/01/2024", end_date="12/31/2024"  # Wrong format
            )

        assert exc_info.value.status_code == 400


class TestStatsClientEnumSupport:
    """Test enum parameter support across stats endpoints."""

    def test_country_players_with_enum(self, mock_requests: requests_mock.Mocker) -> None:
        """Test country_players accepts StatsRankType enum."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "7173",
                        "stats_rank": 1,
                    },
                    {
                        "country_name": "Canada",
                        "country_code": "CA",
                        "player_count": "862",
                        "stats_rank": 2,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Use enum instead of string
        result = client.stats.country_players(rank_type=StatsRankType.WOMEN)

        # Verify it works
        assert isinstance(result, CountryPlayersResponse)
        assert result.rank_type == "WOMEN"
        assert len(result.stats) > 0

        # Verify correct parameter was sent (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        assert "rank_type=women" in mock_requests.last_request.query

    def test_state_players_with_enum(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_players accepts StatsRankType enum."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_players",
            json={
                "type": "Players by State (North America)",
                "rank_type": "OPEN",
                "stats": [
                    {"stateprov": "Unknown", "player_count": "38167", "stats_rank": 1},
                    {"stateprov": "CA", "player_count": "662", "stats_rank": 2},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Use enum for OPEN
        result = client.stats.state_players(rank_type=StatsRankType.OPEN)

        # Verify it works
        assert isinstance(result, StatePlayersResponse)
        assert result.rank_type == "OPEN"

        # Verify no parameter sent for default OPEN
        assert mock_requests.last_request is not None
        assert mock_requests.last_request.qs == {}

    def test_state_tournaments_with_enum(self, mock_requests: requests_mock.Mocker) -> None:
        """Test state_tournaments accepts StatsRankType enum."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/state_tournaments",
            json={
                "type": "Tournaments by State (North America)",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "stateprov": "TX",
                        "tournament_count": "458",
                        "total_points_all": "21036.1100",
                        "total_points_tournament_value": "5084.3200",
                        "stats_rank": 1,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Use enum for WOMEN
        result = client.stats.state_tournaments(rank_type=StatsRankType.WOMEN)

        # Verify it works
        assert isinstance(result, StateTournamentsResponse)
        assert result.rank_type == "WOMEN"

        # Verify correct parameter was sent (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        assert "rank_type=women" in mock_requests.last_request.query

    def test_lucrative_tournaments_with_enums(self, mock_requests: requests_mock.Mocker) -> None:
        """Test lucrative_tournaments accepts both StatsRankType and MajorTournament enums."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/lucrative_tournaments",
            json={
                "type": "Lucrative Tournaments",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "tournament_id": "83321",
                        "tournament_name": "Women's Championship",
                        "event_name": "Main Tournament",
                        "tournament_date": "2025-01-25",
                        "tournament_value": 281.01,
                        "stats_rank": 1,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Use both enums
        result = client.stats.lucrative_tournaments(
            rank_type=StatsRankType.WOMEN, major=MajorTournament.NO
        )

        # Verify it works
        assert isinstance(result, LucrativeTournamentsResponse)
        assert result.rank_type == "WOMEN"

        # Verify both parameters were sent correctly (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "rank_type=women" in query
        assert "major=n" in query

    def test_overall_with_enum(self, mock_requests: requests_mock.Mocker) -> None:
        """Test overall accepts SystemCode enum."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/overall",
            json={
                "type": "Overall Stats",
                "system_code": "WOMEN",
                "stats": {
                    "overall_player_count": 20000,
                    "active_player_count": 10000,
                    "tournament_count": 5000,
                    "tournament_count_last_month": 50,
                    "tournament_count_this_year": 600,
                    "tournament_player_count": 150000,
                    "tournament_player_count_average": 18.5,
                    "age": {
                        "age_under_18": 4.2,
                        "age_18_to_29": 12.1,
                        "age_30_to_39": 25.3,
                        "age_40_to_49": 28.4,
                        "age_50_to_99": 30.0,
                    },
                },
            },
        )

        client = IfpaClient(api_key="test-key")
        # Use SystemCode enum
        result = client.stats.overall(system_code=SystemCode.WOMEN)

        # Verify it works
        assert isinstance(result, OverallStatsResponse)
        assert result.system_code == "WOMEN"

        # Verify correct parameter was sent (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        assert "system_code=women" in mock_requests.last_request.query

    def test_backward_compatibility_with_strings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that string parameters still work (backwards compatibility)."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "OPEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "47101",
                        "stats_rank": 1,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Still use string (backwards compatible)
        result = client.stats.country_players(rank_type="OPEN")

        # Should work exactly as before
        assert isinstance(result, CountryPlayersResponse)
        assert result.rank_type == "OPEN"

    def test_enum_value_extraction(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that enum .value property is extracted correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json={
                "type": "Players by Country",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "country_name": "United States",
                        "country_code": "US",
                        "player_count": "7173",
                        "stats_rank": 1,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")

        # Use enum and verify .value is extracted
        enum_param = StatsRankType.WOMEN
        assert enum_param.value == "WOMEN"

        result = client.stats.country_players(rank_type=enum_param)

        # Verify request used the value, not the enum object (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        assert "rank_type=women" in mock_requests.last_request.query
        assert isinstance(result, CountryPlayersResponse)

    def test_mixed_enum_and_string(self, mock_requests: requests_mock.Mocker) -> None:
        """Test passing enum for rank_type and string for country_code."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/events_by_year",
            json={
                "type": "Events Per Year",
                "rank_type": "WOMEN",
                "stats": [
                    {
                        "year": "2025",
                        "country_count": "1",
                        "tournament_count": "1686",
                        "player_count": "22992",
                        "stats_rank": 1,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        # Mix enum and string parameters
        result = client.stats.events_by_year(rank_type=StatsRankType.WOMEN, country_code="US")

        # Verify both parameters work correctly
        assert isinstance(result, EventsByYearResponse)
        assert result.rank_type == "WOMEN"

        # Verify parameters were sent (requests_mock lowercases query params)
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "rank_type=women" in query
        assert "country_code=us" in query

    def test_stats_enum_string_equivalence(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that enum and string parameters produce identical API calls."""
        # Mock response (same for both calls)
        mock_response = {
            "type": "Players by Country",
            "rank_type": "WOMEN",
            "stats": [
                {
                    "country_code": "US",
                    "country_name": "United States",
                    "player_count": 5000,
                    "stats_rank": 1,
                }
            ],
        }

        # Register mock for both calls
        mock_requests.get(
            "https://api.ifpapinball.com/stats/country_players",
            json=mock_response,
        )

        client = IfpaClient(api_key="test-key")

        # Call 1: Using enum
        result_enum = client.stats.country_players(rank_type=StatsRankType.WOMEN)

        # Call 2: Using string
        result_string = client.stats.country_players(rank_type="WOMEN")

        # Both should produce identical results
        assert result_enum.rank_type == result_string.rank_type
        assert result_enum.rank_type == "WOMEN"
        assert len(result_enum.stats) == len(result_string.stats)

        # Verify query parameters were identical
        history = mock_requests.request_history
        assert len(history) == 2
        # Both requests should have sent rank_type=women (lowercase by requests-mock)
        assert "rank_type=women" in history[0].query.lower()
        assert "rank_type=women" in history[1].query.lower()
