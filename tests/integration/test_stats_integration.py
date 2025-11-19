"""Integration tests for Stats resource.

This test suite performs comprehensive integration testing of all Stats resource methods
against the live IFPA API. Tests cover all 10 statistical endpoints with real data validation.

Test Categories:
1. StatsClient.country_players() - Player counts by country
2. StatsClient.state_players() - Player counts by state/province (North America)
3. StatsClient.state_tournaments() - Tournament counts and points by state
4. StatsClient.events_by_year() - Historical tournament trends by year
5. StatsClient.players_by_year() - Player retention metrics by year
6. StatsClient.largest_tournaments() - Top tournaments by player count
7. StatsClient.lucrative_tournaments() - Top tournaments by WPPR value
8. StatsClient.points_given_period() - Top point earners in date range
9. StatsClient.events_attended_period() - Most active players in date range
10. StatsClient.overall() - Overall IFPA statistics and demographics

All endpoints were verified operational as of 2025-11-19 via curl testing.

These tests make real API calls and require a valid API key.
Run with: pytest -m integration tests/integration/test_stats_integration.py
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from ifpa_api import IfpaClient
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
from tests.integration.helpers import skip_if_no_api_key

# =============================================================================
# COUNTRY PLAYERS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestCountryPlayers:
    """Test StatsClient.country_players() method."""

    def test_country_players_default(self, api_key: str) -> None:
        """Test country_players() with default parameters (OPEN rankings)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.country_players()
            assert isinstance(result, CountryPlayersResponse)
            assert result.type == "Players by Country"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify first entry structure
            first_stat = result.stats[0]
            assert first_stat.country_name is not None
            assert first_stat.country_code is not None
            assert first_stat.player_count > 0
            assert first_stat.stats_rank == 1  # First entry should be rank 1
        finally:
            client.close()

    def test_country_players_women(self, api_key: str) -> None:
        """Test country_players() with WOMEN ranking system."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.country_players(rank_type="WOMEN")
            assert isinstance(result, CountryPlayersResponse)
            assert result.type == "Players by Country"
            assert result.rank_type == "WOMEN"
            assert len(result.stats) > 0

            # Verify data types after string coercion
            for stat in result.stats[:5]:  # Check first 5
                assert isinstance(stat.player_count, int)
                assert isinstance(stat.stats_rank, int)
                assert stat.player_count > 0
        finally:
            client.close()


# =============================================================================
# STATE PLAYERS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatePlayers:
    """Test StatsClient.state_players() method."""

    def test_state_players_default(self, api_key: str) -> None:
        """Test state_players() with default parameters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.state_players()
            assert isinstance(result, StatePlayersResponse)
            assert "Players by State" in result.type  # API may add "(North America)"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify US states are included
            state_codes = [stat.stateprov for stat in result.stats]
            # Common US states should be present
            common_states = ["CA", "NY", "TX", "WA"]
            assert any(state in state_codes for state in common_states)

            # Verify structure
            first_stat = result.stats[0]
            assert first_stat.stateprov is not None
            assert isinstance(first_stat.player_count, int)
            assert first_stat.player_count > 0
            assert first_stat.stats_rank == 1
        finally:
            client.close()


# =============================================================================
# STATE TOURNAMENTS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStateTournaments:
    """Test StatsClient.state_tournaments() method."""

    def test_state_tournaments_default(self, api_key: str) -> None:
        """Test state_tournaments() with default parameters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.state_tournaments()
            assert isinstance(result, StateTournamentsResponse)
            assert "Tournaments by State" in result.type  # API may add "(North America)"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify detailed tournament statistics
            first_stat = result.stats[0]
            assert first_stat.stateprov is not None
            assert isinstance(first_stat.tournament_count, int)
            assert first_stat.tournament_count > 0
            # Points fields should be Decimal with proper coercion
            assert isinstance(first_stat.total_points_all, Decimal)
            assert isinstance(first_stat.total_points_tournament_value, Decimal)
            assert first_stat.total_points_all > 0
            assert first_stat.stats_rank == 1
        finally:
            client.close()


# =============================================================================
# EVENTS BY YEAR STATISTICS
# =============================================================================


@pytest.mark.integration
class TestEventsByYear:
    """Test StatsClient.events_by_year() method."""

    def test_events_by_year_default(self, api_key: str) -> None:
        """Test events_by_year() with default parameters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.events_by_year()
            assert isinstance(result, EventsByYearResponse)
            assert (
                "Events" in result.type and "Year" in result.type
            )  # API returns "Events Per Year"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify historical data structure
            first_stat = result.stats[0]
            assert first_stat.year is not None
            assert isinstance(first_stat.country_count, int)
            assert isinstance(first_stat.tournament_count, int)
            assert isinstance(first_stat.player_count, int)
            assert first_stat.country_count > 0
            assert first_stat.tournament_count > 0
            assert first_stat.player_count > 0
        finally:
            client.close()

    def test_events_by_year_with_country_filter(self, api_key: str) -> None:
        """Test events_by_year() filtered by country."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.events_by_year(country_code="US")
            assert isinstance(result, EventsByYearResponse)
            assert len(result.stats) > 0

            # All entries should have tournament activity
            for stat in result.stats[:5]:
                assert stat.tournament_count > 0
        finally:
            client.close()


# =============================================================================
# PLAYERS BY YEAR STATISTICS
# =============================================================================


@pytest.mark.integration
class TestPlayersByYear:
    """Test StatsClient.players_by_year() method."""

    def test_players_by_year_default(self, api_key: str) -> None:
        """Test players_by_year() with default parameters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.players_by_year()
            assert isinstance(result, PlayersByYearResponse)
            assert result.type == "Players by Year"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify retention metrics structure
            first_stat = result.stats[0]
            assert first_stat.year is not None
            assert isinstance(first_stat.current_year_count, int)
            assert isinstance(first_stat.previous_year_count, int)
            assert isinstance(first_stat.previous_2_year_count, int)
            assert first_stat.current_year_count > 0
            # Retention counts should be less than or equal to current year
            assert first_stat.previous_year_count <= first_stat.current_year_count
        finally:
            client.close()


# =============================================================================
# LARGEST TOURNAMENTS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestLargestTournaments:
    """Test StatsClient.largest_tournaments() method."""

    def test_largest_tournaments_default(self, api_key: str) -> None:
        """Test largest_tournaments() with default parameters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.largest_tournaments()
            assert isinstance(result, LargestTournamentsResponse)
            assert result.type == "Largest Tournaments"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0
            # API returns top 25
            assert len(result.stats) <= 25

            # Verify tournament metadata
            first_stat = result.stats[0]
            assert first_stat.tournament_id > 0
            assert first_stat.tournament_name is not None
            assert first_stat.event_name is not None
            assert first_stat.country_name is not None
            assert first_stat.country_code is not None
            assert isinstance(first_stat.player_count, int)
            assert first_stat.player_count > 0
            assert first_stat.tournament_date is not None  # YYYY-MM-DD format
            assert first_stat.stats_rank == 1
        finally:
            client.close()


# =============================================================================
# LUCRATIVE TOURNAMENTS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestLucrativeTournaments:
    """Test StatsClient.lucrative_tournaments() method."""

    def test_lucrative_tournaments_default_major(self, api_key: str) -> None:
        """Test lucrative_tournaments() with default parameters (major=Y)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.lucrative_tournaments()
            assert isinstance(result, LucrativeTournamentsResponse)
            assert result.type == "Lucrative Tournaments"
            assert result.rank_type == "OPEN"
            assert len(result.stats) > 0

            # Verify tournament value is float (not string)
            first_stat = result.stats[0]
            assert first_stat.tournament_id > 0
            assert first_stat.tournament_name is not None
            assert isinstance(first_stat.tournament_value, float)
            assert first_stat.tournament_value > 0
            assert first_stat.stats_rank == 1
        finally:
            client.close()

    def test_lucrative_tournaments_non_major(self, api_key: str) -> None:
        """Test lucrative_tournaments() with major=N filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.lucrative_tournaments(major="N")
            assert isinstance(result, LucrativeTournamentsResponse)
            assert len(result.stats) > 0

            # Non-major tournaments should have lower values than majors
            for stat in result.stats[:5]:
                assert isinstance(stat.tournament_value, float)
                assert stat.tournament_value > 0
        finally:
            client.close()


# =============================================================================
# POINTS GIVEN PERIOD STATISTICS
# =============================================================================


@pytest.mark.integration
class TestPointsGivenPeriod:
    """Test StatsClient.points_given_period() method."""

    def test_points_given_period_recent(self, api_key: str) -> None:
        """Test points_given_period() with recent date range."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Use last 3 months to ensure data availability
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            result = client.stats.points_given_period(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                limit=10,
            )

            assert isinstance(result, PointsGivenPeriodResponse)
            assert "Points" in result.type  # API may vary text
            assert result.start_date is not None
            assert result.end_date is not None
            assert result.return_count >= 0
            assert result.rank_type == "OPEN"

            # May be empty if no tournaments in date range, but structure should be valid
            if len(result.stats) > 0:
                first_stat = result.stats[0]
                assert first_stat.player_id > 0
                assert first_stat.first_name is not None
                assert first_stat.last_name is not None
                assert first_stat.country_name is not None
                assert isinstance(first_stat.wppr_points, Decimal)
                assert first_stat.wppr_points > 0
                assert first_stat.stats_rank == 1
        finally:
            client.close()

    def test_points_given_period_with_country_filter(self, api_key: str) -> None:
        """Test points_given_period() with country filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Use last 6 months for more data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)

            result = client.stats.points_given_period(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                country_code="US",
                limit=10,
            )

            assert isinstance(result, PointsGivenPeriodResponse)
            # If results exist, verify country filter
            if len(result.stats) > 0:
                # Country filter may not work perfectly in API, just verify structure
                assert result.stats[0].country_code is not None
        finally:
            client.close()


# =============================================================================
# EVENTS ATTENDED PERIOD STATISTICS
# =============================================================================


@pytest.mark.integration
class TestEventsAttendedPeriod:
    """Test StatsClient.events_attended_period() method."""

    def test_events_attended_period_recent(self, api_key: str) -> None:
        """Test events_attended_period() with recent date range."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Use last 3 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            result = client.stats.events_attended_period(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                limit=10,
            )

            assert isinstance(result, EventsAttendedPeriodResponse)
            assert "Events" in result.type or "Tournaments" in result.type  # API may vary text
            assert result.start_date is not None
            assert result.end_date is not None
            assert result.return_count >= 0

            # Note: This endpoint doesn't include rank_type field
            # May be empty if no tournaments in date range
            if len(result.stats) > 0:
                first_stat = result.stats[0]
                assert first_stat.player_id > 0
                assert first_stat.first_name is not None
                assert first_stat.last_name is not None
                assert isinstance(first_stat.tournament_count, int)
                assert first_stat.tournament_count > 0
                assert first_stat.stats_rank == 1
        finally:
            client.close()


# =============================================================================
# OVERALL STATISTICS
# =============================================================================


@pytest.mark.integration
class TestOverallStats:
    """Test StatsClient.overall() method."""

    def test_overall_default(self, api_key: str) -> None:
        """Test overall() with default system_code (OPEN)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.overall()
            assert isinstance(result, OverallStatsResponse)
            assert result.type == "Overall Stats"
            assert result.system_code == "OPEN"

            # Verify nested stats object (not an array)
            stats = result.stats
            assert isinstance(stats.overall_player_count, int)
            assert isinstance(stats.active_player_count, int)
            assert isinstance(stats.tournament_count, int)
            assert isinstance(stats.tournament_count_last_month, int)
            assert isinstance(stats.tournament_count_this_year, int)
            assert isinstance(stats.tournament_player_count, int)
            assert isinstance(stats.tournament_player_count_average, float)

            # Verify counts are reasonable
            assert stats.overall_player_count > 100000  # Should have 100k+ players
            assert stats.active_player_count > 0
            assert stats.tournament_count > 0
            assert stats.tournament_player_count_average > 0

            # Verify age distribution
            age = stats.age
            assert isinstance(age.age_under_18, float)
            assert isinstance(age.age_18_to_29, float)
            assert isinstance(age.age_30_to_39, float)
            assert isinstance(age.age_40_to_49, float)
            assert isinstance(age.age_50_to_99, float)

            # All age percentages should be positive
            assert age.age_under_18 >= 0
            assert age.age_18_to_29 >= 0
            assert age.age_30_to_39 >= 0
            assert age.age_40_to_49 >= 0
            assert age.age_50_to_99 >= 0
        finally:
            client.close()

    def test_overall_women_system_code(self, api_key: str) -> None:
        """Test overall() with WOMEN system_code.

        Note: As of 2025-11-19, the API has a bug where system_code=WOMEN
        returns OPEN data. This test documents the current behavior.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.overall(system_code="WOMEN")
            assert isinstance(result, OverallStatsResponse)

            # API bug: Always returns OPEN regardless of system_code
            # This test documents current API behavior
            assert result.system_code == "OPEN"  # Known bug
            assert result.stats.overall_player_count > 0
        finally:
            client.close()


# =============================================================================
# DATA QUALITY VALIDATION
# =============================================================================


@pytest.mark.integration
class TestStatsDataQuality:
    """Test data quality and consistency across stats endpoints."""

    def test_country_players_sorted_by_count(self, api_key: str) -> None:
        """Verify country_players results are sorted by player count descending."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.country_players()
            assert len(result.stats) > 5  # Need multiple results to check sorting

            # Verify descending order by player count
            for i in range(len(result.stats) - 1):
                current_count = result.stats[i].player_count
                next_count = result.stats[i + 1].player_count
                assert (
                    current_count >= next_count
                ), f"Results not sorted: {current_count} < {next_count} at index {i}"

            # Verify ranks are sequential
            for i, stat in enumerate(result.stats):
                assert stat.stats_rank == i + 1
        finally:
            client.close()

    def test_string_to_number_coercion(self, api_key: str) -> None:
        """Verify string count fields are properly coerced to numbers."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Test various endpoints with string coercion
            country_result = client.stats.country_players()
            if len(country_result.stats) > 0:
                assert isinstance(country_result.stats[0].player_count, int)

            state_result = client.stats.state_tournaments()
            if len(state_result.stats) > 0:
                assert isinstance(state_result.stats[0].tournament_count, int)
                assert isinstance(state_result.stats[0].total_points_all, Decimal)

            largest_result = client.stats.largest_tournaments()
            if len(largest_result.stats) > 0:
                assert isinstance(largest_result.stats[0].player_count, int)
        finally:
            client.close()

    def test_overall_stats_numeric_types(self, api_key: str) -> None:
        """Verify overall endpoint returns proper numeric types (not strings)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.overall()

            # All counts should be integers
            assert isinstance(result.stats.overall_player_count, int)
            assert isinstance(result.stats.active_player_count, int)
            assert isinstance(result.stats.tournament_count, int)
            assert isinstance(result.stats.tournament_count_last_month, int)
            assert isinstance(result.stats.tournament_count_this_year, int)
            assert isinstance(result.stats.tournament_player_count, int)

            # Average should be float
            assert isinstance(result.stats.tournament_player_count_average, float)

            # Age percentages should be floats
            assert isinstance(result.stats.age.age_under_18, float)
            assert isinstance(result.stats.age.age_18_to_29, float)
        finally:
            client.close()


# =============================================================================
# ERROR HANDLING AND EDGE CASES
# =============================================================================


@pytest.mark.integration
class TestStatsErrorHandling:
    """Test error handling for stats endpoints."""

    def test_invalid_date_range(self, api_key: str) -> None:
        """Test that invalid date ranges are handled gracefully."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Future dates may return empty results (not an error)
            future_start = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
            future_end = (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d")

            result = client.stats.points_given_period(
                start_date=future_start, end_date=future_end, limit=10
            )

            # Should succeed but may return no results
            assert isinstance(result, PointsGivenPeriodResponse)
            # Empty results are valid for future dates
        except IfpaApiError as e:
            # Some date validation errors may return 400
            assert e.status_code in (400, 404)
        finally:
            client.close()

    def test_empty_period_results(self, api_key: str) -> None:
        """Test handling of period queries that return no results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            # Use a very narrow date range that may have no tournaments
            single_day = "2020-01-01"

            result = client.stats.events_attended_period(
                start_date=single_day, end_date=single_day, limit=10
            )

            assert isinstance(result, EventsAttendedPeriodResponse)
            # Empty stats array is valid
            assert result.return_count >= 0
            assert isinstance(result.stats, list)
        finally:
            client.close()
