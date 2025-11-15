"""Unit tests for StatsClient.

Tests the statistics resource client using mocked HTTP requests.
"""

import pytest
import requests_mock

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.exceptions import IfpaApiError
from ifpa_sdk.models.stats import (
    GlobalStats,
    HistoricalStatsResponse,
    MachinePopularityResponse,
    ParticipationStatsResponse,
    PlayerCountStatsResponse,
    RecentTournamentsResponse,
    TopCountriesResponse,
    TopTournamentsResponse,
    TournamentCountStatsResponse,
    TrendsResponse,
)


class TestStatsClientGlobal:
    """Test cases for global statistics queries."""

    def test_global_stats(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting global IFPA statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/global",
            json={
                "total_players": 100000,
                "total_tournaments": 50000,
                "total_active_players": 30000,
                "total_countries": 75,
                "total_wppr_points": 5000000.0,
                "average_wppr": 50.0,
                "stats_date": "2024-06-15",
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.global_stats()

        assert isinstance(stats, GlobalStats)
        assert stats.total_players == 100000
        assert stats.total_tournaments == 50000
        assert stats.total_active_players == 30000
        assert stats.total_countries == 75
        assert stats.average_wppr == 50.0


class TestStatsClientCounts:
    """Test cases for player and tournament count statistics."""

    def test_player_counts_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player count statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/player_counts",
            json={
                "stats": [
                    {
                        "period": "2024",
                        "player_count": 30000,
                        "active_count": 15000,
                        "new_players": 5000,
                        "returning_players": 10000,
                    },
                    {
                        "period": "2023",
                        "player_count": 28000,
                        "active_count": 14000,
                        "new_players": 4500,
                    },
                ],
                "total_periods": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.player_counts()

        assert isinstance(stats, PlayerCountStatsResponse)
        assert len(stats.stats) == 2
        assert stats.stats[0].period == "2024"
        assert stats.stats[0].player_count == 30000
        assert stats.total_periods == 2

    def test_player_counts_with_period(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting player counts with period filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/player_counts",
            json={
                "stats": [
                    {
                        "period": "2024-01",
                        "player_count": 2500,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.player_counts(period="month")

        assert len(stats.stats) == 1
        assert "period=month" in mock_requests.last_request.query

    def test_tournament_counts_basic(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting tournament count statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/tournament_counts",
            json={
                "stats": [
                    {
                        "period": "2024",
                        "tournament_count": 5000,
                        "total_players": 150000,
                        "average_size": 30.0,
                        "largest_event": 500,
                    },
                    {
                        "period": "2023",
                        "tournament_count": 4800,
                        "total_players": 140000,
                        "average_size": 29.2,
                    },
                ],
                "total_periods": 2,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.tournament_counts()

        assert isinstance(stats, TournamentCountStatsResponse)
        assert len(stats.stats) == 2
        assert stats.stats[0].tournament_count == 5000
        assert stats.stats[0].average_size == 30.0


class TestStatsClientTopAndRecent:
    """Test cases for top countries, tournaments, and recent data."""

    def test_top_countries(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting top countries statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/top_countries",
            json={
                "countries": [
                    {
                        "rank": 1,
                        "country_code": "US",
                        "country_name": "United States",
                        "player_count": 40000,
                        "tournament_count": 20000,
                        "average_wppr": 60.5,
                        "top_player": {"player_id": 1, "player_name": "Top Player"},
                    },
                    {
                        "rank": 2,
                        "country_code": "CA",
                        "country_name": "Canada",
                        "player_count": 5000,
                        "tournament_count": 2500,
                        "average_wppr": 55.0,
                    },
                ],
                "total_countries": 75,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.top_countries()

        assert isinstance(stats, TopCountriesResponse)
        assert len(stats.countries) == 2
        assert stats.countries[0].rank == 1
        assert stats.countries[0].country_code == "US"
        assert stats.countries[0].player_count == 40000
        assert stats.total_countries == 75

    def test_top_countries_with_limit(self, mock_requests: requests_mock.Mocker) -> None:
        """Test top countries with limit parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/top_countries",
            json={
                "countries": [
                    {"rank": i, "country_code": f"C{i}", "country_name": f"Country {i}"}
                    for i in range(1, 11)
                ],
                "total_countries": 75,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.top_countries(limit=10)

        assert len(stats.countries) == 10
        assert "limit=10" in mock_requests.last_request.query

    def test_top_tournaments(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting top tournaments statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/top_tournaments",
            json={
                "tournaments": [
                    {
                        "rank": 1,
                        "tournament_id": 10001,
                        "tournament_name": "World Championship",
                        "event_date": "2024-06-15",
                        "player_count": 500,
                        "rating_value": 100.0,
                        "country_code": "US",
                    },
                    {
                        "rank": 2,
                        "tournament_id": 10002,
                        "tournament_name": "National Championship",
                        "player_count": 400,
                        "rating_value": 95.0,
                    },
                ],
                "criteria": "size",
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.top_tournaments()

        assert isinstance(stats, TopTournamentsResponse)
        assert len(stats.tournaments) == 2
        assert stats.tournaments[0].rank == 1
        assert stats.tournaments[0].player_count == 500
        assert stats.criteria == "size"

    def test_top_tournaments_with_criteria_and_limit(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test top tournaments with criteria and limit."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/top_tournaments",
            json={
                "tournaments": [
                    {"rank": i, "tournament_id": i, "tournament_name": f"Tournament {i}"}
                    for i in range(1, 11)
                ],
                "criteria": "value",
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.top_tournaments(criteria="value", limit=10)

        assert len(stats.tournaments) == 10
        query = mock_requests.last_request.query
        assert "criteria=value" in query
        assert "limit=10" in query

    def test_recent_tournaments(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting recent tournaments statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/recent_tournaments",
            json={
                "tournaments": [
                    {
                        "tournament_id": 20001,
                        "tournament_name": "Last Week Tournament",
                        "event_date": "2024-06-08",
                        "player_count": 64,
                        "rating_value": 85.0,
                        "country_code": "US",
                        "days_ago": 7,
                    },
                    {
                        "tournament_id": 20002,
                        "tournament_name": "Yesterday Tournament",
                        "event_date": "2024-06-14",
                        "player_count": 32,
                        "days_ago": 1,
                    },
                ],
                "period_days": 30,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.recent_tournaments()

        assert isinstance(stats, RecentTournamentsResponse)
        assert len(stats.tournaments) == 2
        assert stats.tournaments[0].days_ago == 7
        assert stats.period_days == 30

    def test_recent_tournaments_with_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test recent tournaments with days and limit filters."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/recent_tournaments",
            json={
                "tournaments": [],
                "period_days": 7,
            },
        )

        client = IfpaClient(api_key="test-key")
        client.stats.recent_tournaments(days=7, limit=50)

        query = mock_requests.last_request.query
        assert "days=7" in query
        assert "limit=50" in query


class TestStatsClientMachinesAndTrends:
    """Test cases for machine popularity and trend data."""

    def test_machine_popularity(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting machine popularity statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/machine_popularity",
            json={
                "machines": [
                    {
                        "rank": 1,
                        "machine_name": "Medieval Madness",
                        "manufacturer": "Williams",
                        "year": 1997,
                        "usage_count": 5000,
                        "tournament_count": 2000,
                        "average_players": 25.5,
                    },
                    {
                        "rank": 2,
                        "machine_name": "The Addams Family",
                        "manufacturer": "Bally",
                        "year": 1992,
                        "usage_count": 4500,
                        "tournament_count": 1800,
                    },
                ],
                "period": "year",
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.machine_popularity()

        assert isinstance(stats, MachinePopularityResponse)
        assert len(stats.machines) == 2
        assert stats.machines[0].rank == 1
        assert stats.machines[0].machine_name == "Medieval Madness"
        assert stats.machines[0].usage_count == 5000
        assert stats.period == "year"

    def test_machine_popularity_with_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test machine popularity with period and limit filters."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/machine_popularity",
            json={
                "machines": [{"rank": i, "machine_name": f"Machine {i}"} for i in range(1, 26)],
                "period": "all-time",
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.machine_popularity(period="all-time", limit=25)

        assert len(stats.machines) == 25
        query = mock_requests.last_request.query
        assert "period=all-time" in query
        assert "limit=25" in query

    def test_trends(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting trend statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/trends",
            json={
                "metric": "players",
                "data_points": [
                    {
                        "date": "2024-01",
                        "value": 29000.0,
                        "change": 1000.0,
                        "percentage_change": 3.57,
                    },
                    {
                        "date": "2024-02",
                        "value": 30000.0,
                        "change": 1000.0,
                        "percentage_change": 3.45,
                    },
                ],
                "trend_direction": "up",
            },
        )

        client = IfpaClient(api_key="test-key")
        trends = client.stats.trends(metric="players")

        assert isinstance(trends, TrendsResponse)
        assert trends.metric == "players"
        assert len(trends.data_points) == 2
        assert trends.data_points[0].value == 29000.0
        assert trends.data_points[0].change == 1000.0
        assert trends.trend_direction == "up"

    def test_trends_with_period(self, mock_requests: requests_mock.Mocker) -> None:
        """Test trends with period filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/trends",
            json={
                "metric": "tournaments",
                "data_points": [],
                "trend_direction": "stable",
            },
        )

        client = IfpaClient(api_key="test-key")
        client.stats.trends(metric="tournaments", period="month")

        query = mock_requests.last_request.query
        assert "metric=tournaments" in query
        assert "period=month" in query


class TestStatsClientHistoricalAndParticipation:
    """Test cases for historical and participation statistics."""

    def test_historical(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting historical statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/historical",
            json={
                "stats": [
                    {
                        "year": 2024,
                        "total_players": 30000,
                        "total_tournaments": 5000,
                        "new_players": 5000,
                        "average_wppr": 52.5,
                        "additional_metrics": {"growth_rate": 5.2},
                    },
                    {
                        "year": 2023,
                        "total_players": 28000,
                        "total_tournaments": 4800,
                        "new_players": 4500,
                        "average_wppr": 50.0,
                    },
                ],
                "earliest_year": 2010,
                "latest_year": 2024,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.historical()

        assert isinstance(stats, HistoricalStatsResponse)
        assert len(stats.stats) == 2
        assert stats.stats[0].year == 2024
        assert stats.stats[0].total_players == 30000
        assert stats.earliest_year == 2010
        assert stats.latest_year == 2024

    def test_historical_with_year_range(self, mock_requests: requests_mock.Mocker) -> None:
        """Test historical stats with year range filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/historical",
            json={
                "stats": [
                    {"year": 2020, "total_players": 25000},
                    {"year": 2021, "total_players": 26000},
                    {"year": 2022, "total_players": 27000},
                ],
                "earliest_year": 2020,
                "latest_year": 2022,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.historical(start_year=2020, end_year=2022)

        assert len(stats.stats) == 3
        query = mock_requests.last_request.query
        assert "start_year=2020" in query
        assert "end_year=2022" in query

    def test_participation(self, mock_requests: requests_mock.Mocker) -> None:
        """Test getting participation statistics."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/participation",
            json={
                "stats": [
                    {
                        "category": "Active (10+ events/year)",
                        "player_count": 5000,
                        "percentage": 16.7,
                        "average_events": 15.5,
                    },
                    {
                        "category": "Casual (1-9 events/year)",
                        "player_count": 20000,
                        "percentage": 66.7,
                        "average_events": 3.2,
                    },
                    {
                        "category": "Inactive",
                        "player_count": 5000,
                        "percentage": 16.6,
                    },
                ],
                "total_active_players": 25000,
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.participation()

        assert isinstance(stats, ParticipationStatsResponse)
        assert len(stats.stats) == 3
        assert stats.stats[0].category == "Active (10+ events/year)"
        assert stats.stats[0].player_count == 5000
        assert stats.stats[0].percentage == 16.7
        assert stats.total_active_players == 25000

    def test_participation_with_category(self, mock_requests: requests_mock.Mocker) -> None:
        """Test participation stats with category filter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/participation",
            json={
                "stats": [
                    {
                        "category": "Active",
                        "player_count": 5000,
                    }
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        stats = client.stats.participation(category="active")

        assert len(stats.stats) == 1
        assert "category=active" in mock_requests.last_request.query


class TestStatsClientErrors:
    """Test error handling for stats client."""

    def test_global_stats_handles_error(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that global_stats properly handles API errors."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/global",
            status_code=500,
            json={"error": "Internal server error"},
        )

        client = IfpaClient(api_key="test-key")
        with pytest.raises(IfpaApiError) as exc_info:
            client.stats.global_stats()

        assert exc_info.value.status_code == 500

    def test_trends_requires_metric(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that trends method requires metric parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/stats/trends",
            json={
                "metric": "players",
                "data_points": [],
            },
        )

        client = IfpaClient(api_key="test-key")
        client.stats.trends(metric="players")

        # Verify metric was included in request
        assert "metric=players" in mock_requests.last_request.query
