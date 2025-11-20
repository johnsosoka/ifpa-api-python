"""Integration tests for Stats resource.

This test suite performs comprehensive integration testing of all Stats resource methods
against the live IFPA API. Tests cover all 10 statistical endpoints with real data validation.

Test Categories:
1. TestStatsGeographicData - Geographic statistics (country/state players,
   state tournaments)
2. TestStatsHistoricalTrends - Historical trends (events_by_year, players_by_year)
3. TestStatsTournamentRankings - Tournament rankings (largest, lucrative tournaments)
4. TestStatsPlayerActivity - Player activity in date ranges (points_given,
   events_attended)
5. TestStatsOverall - Overall IFPA statistics
6. TestStatsDataQualityAndErrors - Data quality validation and error handling

All endpoints were verified operational as of 2025-11-19 via curl testing.

These tests make real API calls and require a valid API key.
Run with: pytest -m integration tests/integration/test_stats_integration.py
"""

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
from tests.integration.conftest import (
    assert_numeric_in_range,
    assert_stats_fields_types,
    assert_stats_ranking_list,
)

# =============================================================================
# GEOGRAPHIC STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatsGeographicData:
    """Test geographic statistics endpoints (country/state-based data)."""

    @pytest.mark.parametrize("rank_type", ["OPEN", "WOMEN"])
    def test_country_players_by_rank_type(self, client: IfpaClient, rank_type: str) -> None:
        """Test country_players() with different ranking systems.

        Args:
            client: IFPA API client fixture
            rank_type: Ranking system to test (OPEN or WOMEN)
        """
        result = client.stats.country_players(rank_type=rank_type)

        # Validate response structure
        assert isinstance(result, CountryPlayersResponse)
        assert result.type == "Players by Country"
        assert result.rank_type == rank_type
        assert len(result.stats) > 0

        # Validate first entry structure using helper
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "country_name": str,
                "country_code": str,
                "player_count": int,
                "stats_rank": int,
            },
        )
        assert first_stat.player_count > 0
        assert first_stat.stats_rank == 1  # First entry should be rank 1

    def test_state_players(self, client: IfpaClient) -> None:
        """Test state_players() returns North American state/province data.

        Args:
            client: IFPA API client fixture
        """
        result = client.stats.state_players()

        # Validate response structure
        assert isinstance(result, StatePlayersResponse)
        assert "Players by State" in result.type  # API may add "(North America)"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Verify US states are included
        state_codes = [stat.stateprov for stat in result.stats]
        common_states = ["CA", "NY", "TX", "WA"]
        assert any(
            state in state_codes for state in common_states
        ), "Expected common US states in results"

        # Validate structure using helper
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "stateprov": str,
                "player_count": int,
                "stats_rank": int,
            },
        )
        assert first_stat.player_count > 0
        assert first_stat.stats_rank == 1

    @pytest.mark.parametrize("rank_type", ["OPEN", "WOMEN"])
    def test_state_tournaments_by_rank_type(self, client: IfpaClient, rank_type: str) -> None:
        """Test state_tournaments() with different ranking systems.

        Args:
            client: IFPA API client fixture
            rank_type: Ranking system to test (OPEN or WOMEN)
        """
        result = client.stats.state_tournaments(rank_type=rank_type)

        # Validate response structure
        assert isinstance(result, StateTournamentsResponse)
        assert "Tournaments by State" in result.type
        assert result.rank_type == rank_type
        assert len(result.stats) > 0

        # Validate detailed tournament statistics
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "stateprov": str,
                "tournament_count": int,
                "total_points_all": Decimal,
                "total_points_tournament_value": Decimal,
                "stats_rank": int,
            },
        )
        assert first_stat.tournament_count > 0
        assert first_stat.total_points_all > 0
        assert first_stat.stats_rank == 1


# =============================================================================
# HISTORICAL TRENDS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatsHistoricalTrends:
    """Test historical trend statistics endpoints."""

    @pytest.mark.parametrize("country_code", [None, "US"])
    def test_events_by_year(self, client: IfpaClient, country_code: str | None) -> None:
        """Test events_by_year() with optional country filter.

        Args:
            client: IFPA API client fixture
            country_code: Optional country code filter
        """
        result = client.stats.events_by_year(country_code=country_code)

        # Validate response structure
        assert isinstance(result, EventsByYearResponse)
        assert "Events" in result.type and "Year" in result.type
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Validate historical data structure
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "year": str,
                "country_count": int,
                "tournament_count": int,
                "player_count": int,
            },
        )
        assert first_stat.country_count > 0
        assert first_stat.tournament_count > 0
        assert first_stat.player_count > 0

    def test_players_by_year(self, client: IfpaClient) -> None:
        """Test players_by_year() returns player retention metrics.

        Args:
            client: IFPA API client fixture
        """
        result = client.stats.players_by_year()

        # Validate response structure
        assert isinstance(result, PlayersByYearResponse)
        assert result.type == "Players by Year"
        assert result.rank_type == "OPEN"
        assert len(result.stats) > 0

        # Validate retention metrics structure
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "year": str,
                "current_year_count": int,
                "previous_year_count": int,
                "previous_2_year_count": int,
            },
        )
        assert first_stat.current_year_count > 0
        # Retention counts should be less than or equal to current year
        assert first_stat.previous_year_count <= first_stat.current_year_count


# =============================================================================
# TOURNAMENT RANKINGS STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatsTournamentRankings:
    """Test tournament ranking statistics endpoints."""

    @pytest.mark.parametrize("rank_type", ["OPEN", "WOMEN"])
    def test_largest_tournaments_by_rank_type(self, client: IfpaClient, rank_type: str) -> None:
        """Test largest_tournaments() with different ranking systems.

        Args:
            client: IFPA API client fixture
            rank_type: Ranking system to test (OPEN or WOMEN)
        """
        result = client.stats.largest_tournaments(rank_type=rank_type)

        # Validate response structure
        assert isinstance(result, LargestTournamentsResponse)
        assert result.type == "Largest Tournaments"
        assert result.rank_type == rank_type
        assert len(result.stats) > 0
        assert len(result.stats) <= 25  # API returns top 25

        # Validate tournament metadata
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "tournament_id": int,
                "tournament_name": str,
                "event_name": str,
                "country_name": str,
                "country_code": str,
                "player_count": int,
                "tournament_date": str,
                "stats_rank": int,
            },
        )
        assert first_stat.player_count > 0
        assert first_stat.stats_rank == 1

    @pytest.mark.parametrize(
        ("rank_type", "major"),
        [
            ("OPEN", "Y"),  # Default: OPEN majors
            ("OPEN", "N"),  # OPEN non-majors
            ("WOMEN", "Y"),  # WOMEN majors
        ],
    )
    def test_lucrative_tournaments(self, client: IfpaClient, rank_type: str, major: str) -> None:
        """Test lucrative_tournaments() with rank types and major filter.

        Args:
            client: IFPA API client fixture
            rank_type: Ranking system to test (OPEN or WOMEN)
            major: Major tournament filter ("Y" or "N")
        """
        result = client.stats.lucrative_tournaments(rank_type=rank_type, major=major)

        # Validate response structure
        assert isinstance(result, LucrativeTournamentsResponse)
        assert result.type == "Lucrative Tournaments"
        assert result.rank_type == rank_type
        assert len(result.stats) > 0

        # Validate tournament value fields
        first_stat = result.stats[0]
        assert_stats_fields_types(
            first_stat,
            {
                "tournament_id": int,
                "tournament_name": str,
                "tournament_value": float,
                "stats_rank": int,
            },
        )
        assert first_stat.tournament_value > 0
        assert first_stat.stats_rank == 1


# =============================================================================
# PLAYER ACTIVITY PERIOD STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatsPlayerActivity:
    """Test player activity statistics over time periods."""

    @pytest.mark.parametrize(
        "date_fixture_name",
        ["stats_date_range_90_days", "stats_date_range_180_days"],
    )
    def test_points_given_period(
        self, client: IfpaClient, date_fixture_name: str, request: pytest.FixtureRequest
    ) -> None:
        """Test points_given_period() with different date ranges.

        Args:
            client: IFPA API client fixture
            date_fixture_name: Name of date fixture to use
            request: Pytest fixture request object
        """
        # Get the date range fixture dynamically
        start_date, end_date = request.getfixturevalue(date_fixture_name)

        result = client.stats.points_given_period(
            start_date=start_date, end_date=end_date, limit=10
        )

        # Validate response structure
        assert isinstance(result, PointsGivenPeriodResponse)
        assert "Points" in result.type
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.return_count >= 0
        assert result.rank_type == "OPEN"

        # May be empty if no tournaments in date range, but structure should be valid
        if len(result.stats) > 0:
            first_stat = result.stats[0]
            assert_stats_fields_types(
                first_stat,
                {
                    "player_id": int,
                    "first_name": str,
                    "last_name": str,
                    "country_name": str,
                    "wppr_points": Decimal,
                    "stats_rank": int,
                },
            )
            assert first_stat.wppr_points > 0
            assert first_stat.stats_rank == 1

    def test_points_given_period_with_country_filter(
        self, client: IfpaClient, stats_date_range_180_days: tuple[str, str], country_code: str
    ) -> None:
        """Test points_given_period() with country filter.

        Args:
            client: IFPA API client fixture
            stats_date_range_180_days: 180-day date range fixture
            country_code: Country code from fixture
        """
        start_date, end_date = stats_date_range_180_days

        result = client.stats.points_given_period(
            start_date=start_date,
            end_date=end_date,
            country_code=country_code,
            limit=10,
        )

        # Validate response structure
        assert isinstance(result, PointsGivenPeriodResponse)
        # If results exist, verify structure (country filter may not work perfectly in API)
        if len(result.stats) > 0:
            assert result.stats[0].country_code is not None

    def test_events_attended_period(
        self, client: IfpaClient, stats_date_range_90_days: tuple[str, str]
    ) -> None:
        """Test events_attended_period() with 90-day date range.

        Args:
            client: IFPA API client fixture
            stats_date_range_90_days: 90-day date range fixture
        """
        start_date, end_date = stats_date_range_90_days

        result = client.stats.events_attended_period(
            start_date=start_date, end_date=end_date, limit=10
        )

        # Validate response structure
        assert isinstance(result, EventsAttendedPeriodResponse)
        assert "Events" in result.type or "Tournaments" in result.type
        assert result.start_date is not None
        assert result.end_date is not None
        assert result.return_count >= 0

        # Note: This endpoint doesn't include rank_type field
        # May be empty if no tournaments in date range
        if len(result.stats) > 0:
            first_stat = result.stats[0]
            assert_stats_fields_types(
                first_stat,
                {
                    "player_id": int,
                    "first_name": str,
                    "last_name": str,
                    "tournament_count": int,
                    "stats_rank": int,
                },
            )
            assert first_stat.tournament_count > 0
            assert first_stat.stats_rank == 1


# =============================================================================
# OVERALL STATISTICS
# =============================================================================


@pytest.mark.integration
class TestStatsOverall:
    """Test overall IFPA statistics endpoint."""

    @pytest.mark.parametrize("system_code", ["OPEN", "WOMEN"])
    def test_overall_stats(
        self,
        client: IfpaClient,
        system_code: str,
        stats_thresholds: dict[str, int],
    ) -> None:
        """Test overall() with different system codes.

        Note: As of 2025-11-19, the API has a bug where system_code=WOMEN
        returns OPEN data. This test documents the current behavior.

        Args:
            client: IFPA API client fixture
            system_code: System code to test (OPEN or WOMEN)
            stats_thresholds: Expected minimum thresholds fixture
        """
        result = client.stats.overall(system_code=system_code)

        # Validate response structure
        assert isinstance(result, OverallStatsResponse)
        assert result.type == "Overall Stats"

        # API bug: Always returns OPEN regardless of system_code
        if system_code == "WOMEN":
            assert result.system_code == "OPEN"  # Known bug - document it
        else:
            assert result.system_code == "OPEN"

        # Validate nested stats object (not an array) using helper
        stats = result.stats
        assert_stats_fields_types(
            stats,
            {
                "overall_player_count": int,
                "active_player_count": int,
                "tournament_count": int,
                "tournament_count_last_month": int,
                "tournament_count_this_year": int,
                "tournament_player_count": int,
                "tournament_player_count_average": float,
            },
        )

        # Verify counts are within reasonable ranges using thresholds
        assert_numeric_in_range(
            stats.overall_player_count,
            stats_thresholds["overall_player_count"],
            200000,  # Upper bound
            "overall_player_count",
        )
        assert stats.active_player_count > stats_thresholds["active_player_count"]
        assert stats.tournament_count > stats_thresholds["tournament_count"]
        assert stats.tournament_count_this_year >= stats_thresholds["tournament_count_this_year"]
        assert stats.tournament_count_last_month >= stats_thresholds["tournament_count_last_month"]
        assert stats.tournament_player_count_average > 0

        # Validate age distribution
        age = stats.age
        assert_stats_fields_types(
            age,
            {
                "age_under_18": float,
                "age_18_to_29": float,
                "age_30_to_39": float,
                "age_40_to_49": float,
                "age_50_to_99": float,
            },
        )

        # All age percentages should be non-negative
        assert age.age_under_18 >= 0
        assert age.age_18_to_29 >= 0
        assert age.age_30_to_39 >= 0
        assert age.age_40_to_49 >= 0
        assert age.age_50_to_99 >= 0


# =============================================================================
# DATA QUALITY AND ERROR HANDLING
# =============================================================================


@pytest.mark.integration
class TestStatsDataQualityAndErrors:
    """Test data quality validation and error handling for stats endpoints."""

    # === DATA QUALITY TESTS ===

    def test_country_players_sorted_and_ranked(self, client: IfpaClient) -> None:
        """Verify country_players results are sorted correctly with sequential ranks."""
        result = client.stats.country_players()
        assert_stats_ranking_list(result.stats, min_count=5)

        # Verify descending order by player count
        for i in range(len(result.stats) - 1):
            current_count = result.stats[i].player_count
            next_count = result.stats[i + 1].player_count
            assert (
                current_count >= next_count
            ), f"Results not sorted: {current_count} < {next_count} at index {i}"

    def test_string_to_number_coercion(self, client: IfpaClient) -> None:
        """Verify string count fields are properly coerced to numbers."""
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

    def test_overall_stats_numeric_types(self, client: IfpaClient) -> None:
        """Verify overall endpoint returns proper numeric types (not strings)."""
        result = client.stats.overall()

        # Validate all numeric fields using helper
        assert_stats_fields_types(
            result.stats,
            {
                "overall_player_count": int,
                "active_player_count": int,
                "tournament_count": int,
                "tournament_count_last_month": int,
                "tournament_count_this_year": int,
                "tournament_player_count": int,
                "tournament_player_count_average": float,
            },
        )

        # Age percentages should be floats
        assert_stats_fields_types(
            result.stats.age,
            {
                "age_under_18": float,
                "age_18_to_29": float,
            },
        )

    # === ERROR HANDLING TESTS ===

    def test_invalid_date_range_handling(self, client: IfpaClient) -> None:
        """Test that invalid/future date ranges are handled gracefully."""
        from datetime import datetime, timedelta

        # Future dates may return empty results (not an error)
        future_start = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        future_end = (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d")

        try:
            result = client.stats.points_given_period(
                start_date=future_start, end_date=future_end, limit=10
            )
            # Should succeed but may return no results
            assert isinstance(result, PointsGivenPeriodResponse)
            # Empty results are valid for future dates
        except IfpaApiError as e:
            # Some date validation errors may return 400
            assert e.status_code in (400, 404)

    def test_empty_period_results_handling(self, client: IfpaClient) -> None:
        """Test handling of period queries that return no results."""
        # Use a very narrow date range that may have no tournaments
        single_day = "2020-01-01"

        result = client.stats.events_attended_period(
            start_date=single_day, end_date=single_day, limit=10
        )

        assert isinstance(result, EventsAttendedPeriodResponse)
        # Empty stats array is valid
        assert result.return_count >= 0
        assert isinstance(result.stats, list)

    # === COMPREHENSIVE ERROR TESTS FOR ALL ENDPOINTS ===

    def test_country_players_invalid_rank_type(self, client: IfpaClient) -> None:
        """Test country_players() with invalid rank_type."""
        with pytest.raises((IfpaApiError, ValueError)):
            client.stats.country_players(rank_type="INVALID")

    def test_events_by_year_invalid_country(self, client: IfpaClient) -> None:
        """Test events_by_year() with invalid country code."""
        # API may accept invalid country codes and return empty results
        result = client.stats.events_by_year(country_code="INVALID")
        # Should not raise error, but may return empty or all results
        assert isinstance(result, EventsByYearResponse)

    def test_largest_tournaments_invalid_rank_type(self, client: IfpaClient) -> None:
        """Test largest_tournaments() with invalid rank_type."""
        with pytest.raises((IfpaApiError, ValueError)):
            client.stats.largest_tournaments(rank_type="INVALID")

    def test_overall_invalid_system_code(self, client: IfpaClient) -> None:
        """Test overall() with invalid system_code.

        Note: The API doesn't validate system_code and returns OPEN data
        for any invalid value. This test documents that behavior.
        """
        # API accepts any system_code but returns OPEN data
        result = client.stats.overall(system_code="INVALID")
        assert isinstance(result, OverallStatsResponse)
        assert result.system_code == "OPEN"  # API returns OPEN for invalid codes
