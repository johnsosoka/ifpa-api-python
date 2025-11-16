"""Unit tests for SeriesClient and SeriesHandle.

Tests the series resource client and handle using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.series import (
    RegionRepsResponse,
    SeriesListResponse,
    SeriesPlayerCard,
    SeriesRegionsResponse,
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
        assert mock_requests.last_request is not None
        assert "active_only=true" in mock_requests.last_request.query


class TestSeriesHandle:
    """Test cases for SeriesHandle resource-specific operations."""

    def test_standings_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series overall standings."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/overall_standings",
            json={
                "series_code": "PAPA",
                "year": 2024,
                "championship_prize_fund": 10000.0,
                "overall_results": [
                    {
                        "region_code": "OH",
                        "region_name": "Ohio",
                        "player_count": "150",
                        "unique_player_count": "120",
                        "tournament_count": "10",
                        "current_leader": {
                            "player_id": "5001",
                            "player_name": "Top Player",
                        },
                        "prize_fund": 2000.0,
                    },
                    {
                        "region_code": "IL",
                        "region_name": "Illinois",
                        "player_count": "100",
                        "unique_player_count": "80",
                        "tournament_count": "8",
                        "current_leader": {
                            "player_id": "5002",
                            "player_name": "Second Player",
                        },
                        "prize_fund": 1500.0,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series_handle("PAPA").standings()

        assert isinstance(standings, SeriesStandingsResponse)
        assert standings.series_code == "PAPA"
        assert len(standings.overall_results) == 2
        assert standings.overall_results[0].region_code == "OH"
        assert standings.overall_results[0].region_name == "Ohio"

    def test_standings_with_pagination(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting paginated series overall standings."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/overall_standings",
            json={
                "series_code": "PAPA",
                "year": 2024,
                "championship_prize_fund": 50000.0,
                "overall_results": [
                    {
                        "region_code": f"R{i}",
                        "region_name": f"Region {i}",
                        "player_count": "100",
                        "current_leader": {
                            "player_id": str(i),
                            "player_name": f"Player {i}",
                        },
                        "prize_fund": 1000.0,
                    }
                    for i in range(1, 51)
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        standings = client.series_handle("PAPA").standings(start_pos=0, count=50)

        assert len(standings.overall_results) == 50
        assert mock_requests.last_request is not None
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
        assert mock_requests.last_request is not None
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
        assert mock_requests.last_request is not None
        query = mock_requests.last_request.query
        assert "region_code=oh" in query
        assert "year=2023" in query

    def test_regions(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting series regions."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/regions",
            json={
                "series_code": "PAPA",
                "year": 2024,
                "active_regions": [
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
        regions = client.series_handle("PAPA").regions(region_code="NW", year=2024)

        assert isinstance(regions, SeriesRegionsResponse)
        assert regions.series_code == "PAPA"
        assert len(regions.active_regions) == 2
        assert regions.active_regions[0].region_name == "Northwest"
        assert regions.active_regions[0].player_count == 100

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
        stats = client.series_handle("PAPA").stats(region_code="OH")

        assert isinstance(stats, SeriesStats)
        assert stats.series_code == "PAPA"
        assert stats.total_events == 12
        assert stats.total_players == 500
        assert stats.average_event_size == 125.0

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
            "https://api.ifpapinball.com/series/NONEXISTENT/overall_standings",
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

        # Mock overall standings
        mock_requests.get(
            "https://api.ifpapinball.com/series/PAPA/overall_standings",
            json={
                "series_code": "PAPA",
                "year": 2024,
                "championship_prize_fund": 10000.0,
                "overall_results": [
                    {
                        "region_code": "OH",
                        "region_name": "Ohio",
                        "player_count": "100",
                        "current_leader": {
                            "player_id": "5001",
                            "player_name": "Top Player",
                        },
                        "prize_fund": 2000.0,
                    }
                ],
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
        assert len(standings.overall_results) == 1
