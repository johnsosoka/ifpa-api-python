"""Unit tests for SeriesClient and SeriesHandle.

Tests the series resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.exceptions import IfpaApiError
from ifpa_sdk.models.series import (
    RegionRepsResponse,
    SeriesListResponse,
    SeriesOverview,
    SeriesPlayerCard,
    SeriesRegionsResponse,
    SeriesRules,
    SeriesScheduleResponse,
    SeriesStandingsResponse,
    SeriesStats,
)


class TestSeriesClient:
    """Test cases for SeriesClient collection-level operations."""

    def test_list_all_series(self, mock_requests: requests_mock.Mocker) -> None:
        """Test listing all series."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "code": "PAPA",
                        "title": "PAPA Circuit",
                        "description": "Professional pinball circuit",
                        "website": "https://papa.org",
                        "active": True,
                    },
                    {
                        "code": "IFPA",
                        "title": "IFPA State Championship Series",
                        "description": "State championship series",
                        "active": True,
                    },
                ],
                "total_count": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.series.list()

        assert isinstance(result, SeriesListResponse)
        assert len(result.series) == 2
        assert result.series[0].series_code == "PAPA"
        assert result.series[0].series_name == "PAPA Circuit"
        assert result.total_count == 2

    def test_list_active_only(self, mock_requests: requests_mock.Mocker) -> None:
        """Test listing only active series."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "code": "PAPA",
                        "title": "PAPA Circuit",
                        "active": True,
                    }
                ],
                "total_count": 1,
            },
        )

        client = IfpaClient(api_key="test-key")
        result = client.series.list(active_only=True)

        assert len(result.series) == 1
        assert "active_only=true" in mock_requests.last_request.query


class TestSeriesHandle:
    """Test cases for SeriesHandle resource-specific operations."""

    def test_standings_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series standings."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/standings",
            json={
                "series_code": "PAPA",
                "series_name": "PAPA Circuit",
                "standings": [
                    {
                        "position": 1,
                        "player_id": 5001,
                        "player_name": "Top Player",
                        "points": 500.0,
                        "events_played": 5,
                        "best_finish": 1,
                    },
                    {
                        "position": 2,
                        "player_id": 5002,
                        "player_name": "Second Player",
                        "points": 450.0,
                        "events_played": 4,
                        "best_finish": 2,
                    },
                ],
                "total_players": 100,
            },
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series_handle("PAPA").standings()

        assert isinstance(standings, SeriesStandingsResponse)
        assert standings.series_code == "PAPA"
        assert len(standings.standings) == 2
        assert standings.standings[0].position == 1
        assert standings.standings[0].points == 500.0
        assert standings.total_players == 100

    def test_standings_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting paginated series standings."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/standings",
            json={
                "series_code": "PAPA",
                "standings": [
                    {"position": i, "player_id": i, "points": 500 - i} for i in range(1, 51)
                ],
                "total_players": 200,
            },
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series_handle("PAPA").standings(start_pos=0, count=50)

        assert len(standings.standings) == 50
        query = mock_requests.last_request.query
        assert "start_pos=0" in query
        assert "count=50" in query

    def test_player_card(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting a player's series card."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/player_card/12345",
            json={
                "series_code": "PAPA",
                "region_code": "OH",
                "year": 2024,
                "player_id": 12345,
                "player_name": "John Smith",
                "player_card": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "PAPA Event 1",
                        "event_name": "Main Tournament",
                        "event_end_date": "2024-01-15T00:00:00.000Z",
                        "wppr_points": 100.0,
                        "region_event_rank": 3,
                    },
                    {
                        "tournament_id": 10002,
                        "tournament_name": "PAPA Event 2",
                        "event_name": "Finals",
                        "event_end_date": "2024-02-20T00:00:00.000Z",
                        "wppr_points": 80.0,
                        "region_event_rank": 5,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        card = client.series_handle("PAPA").player_card(12345, "OH")

        assert isinstance(card, SeriesPlayerCard)
        assert card.series_code == "PAPA"
        assert card.region_code == "OH"
        assert card.year == 2024
        assert card.player_id == 12345
        assert len(card.player_card) == 2
        assert card.player_card[0].tournament_name == "PAPA Event 1"
        assert card.player_card[0].wppr_points == 100.0
        assert card.player_card[0].region_event_rank == 3

        # Verify query parameters
        query = mock_requests.last_request.query
        assert "region_code=oh" in query

    def test_player_card_with_string_id(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that player ID can be a string in player_card."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/player_card/12345",
            json={
                "series_code": "PAPA",
                "region_code": "IL",
                "player_id": 12345,
                "player_name": "John Smith",
                "player_card": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        card = client.series_handle("PAPA").player_card("12345", "IL")

        assert card.player_id == 12345

    def test_player_card_with_year(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting a player's card for a specific year."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/player_card/12345",
            json={
                "series_code": "PAPA",
                "region_code": "OH",
                "year": 2023,
                "player_id": 12345,
                "player_name": "John Smith",
                "player_card": [
                    {
                        "tournament_id": 10001,
                        "tournament_name": "PAPA Event 2023",
                        "wppr_points": 75.0,
                        "region_event_rank": 2,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        card = client.series_handle("PAPA").player_card(12345, "OH", year=2023)

        assert card.year == 2023
        query = mock_requests.last_request.query
        assert "region_code=oh" in query
        assert "year=2023" in query

    def test_overview(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series overview."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/overview",
            json={
                "series_code": "PAPA",
                "series_name": "PAPA Circuit",
                "description": "Professional pinball circuit",
                "total_events": 12,
                "total_players": 500,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "rules_summary": "Best 5 events count",
                "current_leader": {"player_id": 5001, "player_name": "Top Player"},
            },
        )

        client = IfpaClient(api_key="test-key")
        overview = client.series_handle("PAPA").overview()

        assert isinstance(overview, SeriesOverview)
        assert overview.series_code == "PAPA"
        assert overview.series_name == "PAPA Circuit"
        assert overview.total_events == 12
        assert overview.total_players == 500

    def test_regions(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series regions."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/regions",
            json={
                "series_code": "PAPA",
                "regions": [
                    {
                        "region_code": "NW",
                        "region_name": "Northwest",
                        "player_count": 100,
                        "event_count": 5,
                    },
                    {
                        "region_code": "SW",
                        "region_name": "Southwest",
                        "player_count": 80,
                        "event_count": 4,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        regions = client.series_handle("PAPA").regions()

        assert isinstance(regions, SeriesRegionsResponse)
        assert regions.series_code == "PAPA"
        assert len(regions.regions) == 2
        assert regions.regions[0].region_name == "Northwest"
        assert regions.regions[0].player_count == 100

    def test_rules(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series rules."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/rules",
            json={
                "series_code": "PAPA",
                "series_name": "PAPA Circuit",
                "rules_text": "Complete series rules...",
                "scoring_system": "Points based on finish position",
                "events_counted": 5,
                "eligibility": "Open to all IFPA members",
            },
        )

        client = IfpaClient(api_key="test-key")
        rules = client.series_handle("PAPA").rules()

        assert isinstance(rules, SeriesRules)
        assert rules.series_code == "PAPA"
        assert rules.series_name == "PAPA Circuit"
        assert rules.events_counted == 5
        assert rules.eligibility == "Open to all IFPA members"

    def test_stats(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/stats",
            json={
                "series_code": "PAPA",
                "total_events": 12,
                "total_players": 500,
                "total_participations": 1500,
                "average_event_size": 125.0,
                "statistics": {
                    "median_finish": 32,
                    "most_events_played": 12,
                },
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.series_handle("PAPA").stats()

        assert isinstance(stats, SeriesStats)
        assert stats.series_code == "PAPA"
        assert stats.total_events == 12
        assert stats.total_players == 500
        assert stats.average_event_size == 125.0

    def test_schedule(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series schedule."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/schedule",
            json={
                "series_code": "PAPA",
                "events": [
                    {
                        "tournament_id": 20001,
                        "event_name": "PAPA Event 3",
                        "event_date": "2025-03-15",
                        "location": "Pinball Paradise",
                        "city": "Portland",
                        "stateprov": "OR",
                        "status": "scheduled",
                    },
                    {
                        "event_name": "PAPA Event 4",
                        "event_date": "2025-04-20",
                        "city": "Seattle",
                        "status": "scheduled",
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        schedule = client.series_handle("PAPA").schedule()

        assert isinstance(schedule, SeriesScheduleResponse)
        assert schedule.series_code == "PAPA"
        assert len(schedule.events) == 2
        assert schedule.events[0].event_name == "PAPA Event 3"
        assert schedule.events[0].status == "scheduled"

    def test_region_reps(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series region representatives."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/region_reps",
            json={
                "series_code": "PAPA",
                "representative": [
                    {
                        "player_id": 4,
                        "name": "Josh Sharpe",
                        "region_code": "IL",
                        "region_name": "Illinois",
                        "profile_photo": "https://www.ifpapinball.com/images/profiles/players/4.jpg",
                    },
                    {
                        "player_id": 100,
                        "name": "Jane Doe",
                        "region_code": "OH",
                        "region_name": "Ohio",
                        "profile_photo": "https://www.ifpapinball.com/images/profiles/players/100.jpg",
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        reps = client.series_handle("PAPA").region_reps()

        assert isinstance(reps, RegionRepsResponse)
        assert reps.series_code == "PAPA"
        assert len(reps.representative) == 2
        assert reps.representative[0].player_id == 4
        assert reps.representative[0].name == "Josh Sharpe"
        assert reps.representative[0].region_code == "IL"
        assert reps.representative[0].region_name == "Illinois"


class TestSeriesErrors:
    """Test error handling for series client."""

    def test_list_handles_api_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that list properly handles API errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.series.list()

        assert exc_info.value.status_code == 500

    def test_standings_handles_404(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that standings handles not found series."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NONEXISTENT/standings",
            status_code=404,
            json={"error": "Series not found"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.series_handle("NONEXISTENT").standings()

        assert exc_info.value.status_code == 404


class TestSeriesIntegration:
    """Integration tests ensuring SeriesClient and SeriesHandle work together."""

    def test_list_then_get_standings(self, mock_requests: requests_mock.Mocker) -> None:
        """Test workflow of listing series then getting standings."""
        # Mock list
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "code": "PAPA",
                        "title": "PAPA Circuit",
                        "active": True,
                    }
                ],
                "total_count": 1,
            },
        )

        # Mock standings
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/standings",
            json={
                "series_code": "PAPA",
                "standings": [
                    {
                        "position": 1,
                        "player_id": 5001,
                        "points": 500.0,
                    }
                ],
                "total_players": 100,
            },
        )

        client = IfpaClient(api_key="test-key")

        # List series
        series_list = client.series.list()
        assert len(series_list.series) == 1

        # Get standings for first series
        series_code = series_list.series[0].series_code
        standings = client.series_handle(series_code).standings()

        assert standings.series_code == "PAPA"
        assert len(standings.standings) == 1
        assert standings.total_players == 100
