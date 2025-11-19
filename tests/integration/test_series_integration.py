"""Integration tests for SeriesClient and SeriesHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration

Test organization:
- SeriesClient tests: List operations (collection-level)
- SeriesHandle tests: Individual series operations (callable pattern)
- Parameter variation tests: Edge cases and pagination
- Method removal verification: Ensure deleted methods raise AttributeError
- Endpoint verification tests: Direct API validation
"""

import logging

import pytest
import requests

from ifpa_api.client import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.series import (
    RegionRepsResponse,
    SeriesListResponse,
    SeriesPlayerCard,
    SeriesRegionsResponse,
    SeriesRegionStandingsResponse,
    SeriesStandingsResponse,
    SeriesStats,
    SeriesTournamentsResponse,
)
from tests.integration.helpers import get_test_series_code, skip_if_no_api_key

logger = logging.getLogger(__name__)


# =============================================================================
# SECTION 1: SeriesClient Tests (Collection Operations)
# =============================================================================


@pytest.mark.integration
class TestSeriesClient:
    """Integration tests for SeriesClient collection operations."""

    def test_list_all_series(self, api_key: str) -> None:
        """Test listing all series without filters."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list()

        # Validate response structure
        assert isinstance(result, SeriesListResponse)
        assert hasattr(result, "series")
        assert isinstance(result.series, list)
        assert len(result.series) > 0, "Expected at least one series"

        # Check first series structure
        first_series = result.series[0]
        assert hasattr(first_series, "series_code")
        assert hasattr(first_series, "series_name")
        assert first_series.series_code is not None
        assert first_series.series_name is not None

        logger.info(f"list() returned {len(result.series)} series")

    def test_list_active_only(self, api_key: str) -> None:
        """Test listing only active series."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list(active_only=True)

        assert isinstance(result, SeriesListResponse)
        assert result.series is not None
        assert len(result.series) > 0, "Expected at least one active series"

        # Verify structure
        if len(result.series) > 0:
            first_series = result.series[0]
            assert first_series.series_code is not None
            assert first_series.series_name is not None

        logger.info(f"list(active_only=True) returned {len(result.series)} active series")

    def test_list_inactive_included(self, api_key: str) -> None:
        """Test listing all series including inactive (active_only=False)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list(active_only=False)

        assert isinstance(result, SeriesListResponse)
        assert len(result.series) > 0

        logger.info(f"list(active_only=False) returned {len(result.series)} total series")


# =============================================================================
# SECTION 2: SeriesHandle Tests (Individual Series Operations)
# =============================================================================


@pytest.mark.integration
class TestSeriesHandle:
    """Integration tests for SeriesHandle individual series operations."""

    # --- Standings Tests ---

    def test_standings_basic(self, api_key: str, count_small: int) -> None:
        """Test getting overall standings (region overviews).

        The standings() method calls /overall_standings and returns region overviews,
        not individual player standings. Use region_standings() for player data.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            # Get overall standings (no region required)
            result = client.series(series_code).standings(count=count_small)

            # Validate response
            assert isinstance(result, SeriesStandingsResponse)
            assert result.series_code == series_code
            assert hasattr(result, "overall_results")
            assert isinstance(result.overall_results, list)
            assert len(result.overall_results) > 0

            logger.info(
                f"standings() returned {len(result.overall_results)} region overviews "
                f"for series {series_code}"
            )

        except IfpaApiError as e:
            if e.status_code == 400 and "Region Code" in str(e):
                pytest.skip(f"Series {series_code} requires region_code parameter")
            raise

    def test_standings_with_pagination(self, api_key: str) -> None:
        """Test standings() with pagination parameters.

        Note: The API may not use pagination parameters for this endpoint.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use NACS for consistency in pagination testing
        series_code = "NACS"

        result = client.series(series_code).standings(start_pos=0, count=10)

        assert isinstance(result, SeriesStandingsResponse)
        assert hasattr(result, "overall_results")

        logger.info(
            f"standings(start_pos=0, count=10) "
            f"returned {len(result.overall_results)} region overviews"
        )

    def test_region_standings_basic(self, api_key: str) -> None:
        """Test region_standings() to get detailed player standings for a region."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = "NACS"
        region_code = "OH"

        result = client.series(series_code).region_standings(region_code=region_code)

        assert isinstance(result, SeriesRegionStandingsResponse)
        assert hasattr(result, "standings")
        assert isinstance(result.standings, list)
        assert len(result.standings) > 0

        logger.info(
            f"region_standings('{region_code}') returned {len(result.standings)} player standings"
        )

    def test_region_standings_with_pagination(self, api_key: str, count_small: int) -> None:
        """Test region_standings() with pagination parameters.

        Note: API appears to ignore pagination parameters and returns all results.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = "NACS"
        region_code = "OH"

        result = client.series(series_code).region_standings(
            region_code=region_code, start_pos=0, count=count_small
        )

        assert isinstance(result, SeriesRegionStandingsResponse)
        assert len(result.standings) > 0

        logger.info(
            f"region_standings('{region_code}', start_pos=0, count={count_small}) "
            f"returned {len(result.standings)} standings (API may ignore pagination)"
        )

    def test_standings_vs_region_standings_relationship(self, api_key: str) -> None:
        """Clarify the relationship between standings() and region_standings().

        This test demonstrates that:
        - standings() returns region OVERVIEWS (summary data per region)
        - region_standings() returns PLAYER STANDINGS within a specific region
        - The two methods are complementary, not duplicates
        - Data should be consistent between the two methods
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = "NACS"
        region_code = "OH"

        # Get overall standings (region overviews)
        overall = client.series(series_code).standings()

        # Verify we got region overviews, not player data
        assert isinstance(overall, SeriesStandingsResponse)
        assert hasattr(overall, "overall_results")
        assert len(overall.overall_results) > 0

        # Find the Ohio region in overall standings
        oh_overview = next(
            (r for r in overall.overall_results if r.region_code == region_code),
            None,
        )
        assert oh_overview is not None, f"Region {region_code} not found in overall standings"

        # Get detailed player standings for Ohio
        detail = client.series(series_code).region_standings(region_code)

        # Verify we got player standings, not region overviews
        assert isinstance(detail, SeriesRegionStandingsResponse)
        assert detail.region_code == region_code
        assert detail.series_code == series_code
        assert len(detail.standings) > 0, "Should have player standings"

        # Validate consistency: leader in overview should match top player in detailed standings
        if oh_overview.current_leader:
            detail_leader = detail.standings[0]  # First place in detailed standings
            player_id_str = oh_overview.current_leader.get("player_id")
            if player_id_str is not None:
                overview_leader_id = int(player_id_str)
                assert detail_leader.player_id == overview_leader_id, (
                    f"Leader mismatch: overview shows player {overview_leader_id}, "
                    f"but detailed standings show player {detail_leader.player_id}"
                )

        logger.info(
            f"✓ Verified relationship: standings() returned {len(overall.overall_results)} region "
            f"overviews, region_standings('{region_code}') returned {len(detail.standings)} players"
        )

    # --- Player Card Tests ---

    def test_player_card_basic(self, api_key: str, player_active_id: int) -> None:
        """Test getting player series card with required parameters only."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"
        region_code = "OH"

        try:
            card = client.series(series_code).player_card(player_active_id, region_code)

            assert isinstance(card, SeriesPlayerCard)
            assert card.player_id == player_active_id
            assert card is not None

            logger.info(f"player_card({player_active_id}, {region_code}) successful")

        except IfpaApiError as e:
            # Player may not have participated in this series
            if e.status_code == 404:
                pytest.skip(f"Player {player_active_id} not in series {series_code}")
            raise

    def test_player_card_with_year(self, api_key: str, player_active_id: int) -> None:
        """Test player_card() with year parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"
        region_code = "OH"
        year = 2023

        try:
            result = client.series(series_code).player_card(
                player_active_id, region_code, year=year
            )

            assert isinstance(result, SeriesPlayerCard)
            assert result.player_id == player_active_id

            logger.info(f"player_card({player_active_id}, {region_code}, year={year}) successful")

        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(
                    f"Player {player_active_id} not in series {series_code} for year {year}"
                )
            raise

    def test_player_card_different_region(self, api_key: str, player_active_id: int) -> None:
        """Test player_card() with different region codes."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"
        region_code = "IL"  # Different region

        try:
            result = client.series(series_code).player_card(player_active_id, region_code)

            assert isinstance(result, SeriesPlayerCard)

            logger.info(f"player_card with region {region_code} successful")

        except IfpaApiError as e:
            if e.status_code == 404:
                pytest.skip(
                    f"Player {player_active_id} not in series {series_code} region {region_code}"
                )
            raise

    # --- Region Tests ---

    def test_regions(self, api_key: str) -> None:
        """Test getting series regions (requires region_code and year parameters)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            # regions() requires region_code and year
            result = client.series(series_code).regions("OH", 2025)

            assert isinstance(result, SeriesRegionsResponse)
            assert hasattr(result, "active_regions")
            assert isinstance(result.active_regions, list)

            if len(result.active_regions) > 0:
                first_region = result.active_regions[0]
                assert hasattr(first_region, "region_code")
                assert hasattr(first_region, "region_name")

                logger.info(
                    f"regions(region_code='OH', year=2025) "
                    f"returned {len(result.active_regions)} regions"
                )

        except IfpaApiError as e:
            # Some series endpoints require additional parameters
            if e.status_code == 400:
                pytest.skip(f"Series {series_code} regions endpoint requires parameters")
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} regions not available")
            raise

    def test_region_reps(self, api_key: str) -> None:
        """Test getting series region representatives."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            result = client.series(series_code).region_reps()

            assert isinstance(result, RegionRepsResponse)
            assert hasattr(result, "representative")
            assert isinstance(result.representative, list)
            assert result is not None

            if len(result.representative) > 0:
                first_rep = result.representative[0]
                assert hasattr(first_rep, "player_id")
                assert hasattr(first_rep, "name")
                assert hasattr(first_rep, "region_code")

                logger.info(f"region_reps() returned {len(result.representative)} reps")

        except IfpaApiError as e:
            # Not all series have region reps
            if e.status_code == 404:
                pytest.skip(f"Series {series_code} has no region reps")
            raise

    # --- Statistics Tests ---

    def test_stats(self, api_key: str) -> None:
        """Test getting series statistics (requires region_code parameter)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        try:
            # stats() requires region_code parameter
            result = client.series(series_code).stats("OH")

            assert isinstance(result, SeriesStats)
            assert hasattr(result, "series_code")
            assert result is not None

            logger.info("stats(region_code='OH') successful")

        except IfpaApiError as e:
            # Not all series have stats endpoints available
            if e.status_code in [400, 404]:
                pytest.skip(f"Series {series_code} stats not available or requires region code")
            raise

    # --- Tournaments Tests ---

    def test_tournaments(self, api_key: str) -> None:
        """Test getting series tournaments (requires region_code parameter)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use NACS for consistency
        series_code = "NACS"
        region_code = "OH"

        result = client.series(series_code).tournaments(region_code=region_code)

        assert isinstance(result, SeriesTournamentsResponse)
        assert hasattr(result, "tournaments")
        assert isinstance(result.tournaments, list)

        logger.info(
            f"tournaments(region_code='{region_code}') "
            f"returned {len(result.tournaments)} tournaments"
        )


# =============================================================================
# SECTION 3: Method Removal Verification
# =============================================================================


@pytest.mark.integration
class TestRemovedMethods:
    """Verify that removed methods from Phase 1 properly raise AttributeError."""

    def test_overview_method_removed(self, api_key: str) -> None:
        """Verify overview() method was removed from Phase 1 implementation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_context = client.series("NACS")
        assert not hasattr(series_context, "overview"), "overview() method should not exist"
        logger.info("overview() correctly does not exist (method removed)")

    def test_rules_method_removed(self, api_key: str) -> None:
        """Verify rules() method was removed from Phase 1 implementation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_context = client.series("NACS")
        assert not hasattr(series_context, "rules"), "rules() method should not exist"
        logger.info("rules() correctly does not exist (method removed)")

    def test_schedule_method_removed(self, api_key: str) -> None:
        """Verify schedule() method was removed from Phase 1 implementation."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_context = client.series("NACS")
        assert not hasattr(series_context, "schedule"), "schedule() method should not exist"
        logger.info("schedule() correctly does not exist (method removed)")


# =============================================================================
# SECTION 4: Cross-Series Validation
# =============================================================================


@pytest.mark.integration
class TestMultipleSeries:
    """Test series operations across different series codes."""

    def test_multiple_series_codes(self, api_key: str, count_small: int) -> None:
        """Test series methods with different series codes."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get list of series first
        series_list = client.series.list(active_only=True)
        assert len(series_list.series) > 0

        # Test with first few series codes
        test_codes = [s.series_code for s in series_list.series[:3]]

        logger.info(f"Testing with series codes: {test_codes}")

        for code in test_codes:
            try:
                _ = client.series(code).standings(count=count_small)
                logger.info(f"Series '{code}' standings accessible")
            except IfpaApiError as e:
                logger.warning(f"Series '{code}' standings failed: {e.status_code}")


# =============================================================================
# SECTION 5: Direct API Verification
# =============================================================================


@pytest.mark.integration
def test_direct_http_endpoint_verification(
    api_key: str,
) -> dict[str, dict[str, int | list[str] | None | bool]]:
    """Use direct HTTP calls to verify all series endpoints.

    This test bypasses the SDK to directly test each endpoint against the API.
    Useful for debugging endpoint availability and response structure.

    Returns:
        dict: Endpoint verification results for inspection.
    """
    skip_if_no_api_key()

    series_code = "NACS"  # North American Championship Series
    base_url = "https://api.ifpapinball.com"
    headers = {"X-API-Key": api_key}

    endpoints_to_test = [
        "/series/list",
        f"/series/{series_code}/standings",
        f"/series/{series_code}/overall_standings",  # Test both paths
        f"/series/{series_code}/regions",
        f"/series/{series_code}/region_reps",
        f"/series/{series_code}/stats",
        f"/series/{series_code}/overview",
        f"/series/{series_code}/rules",
        f"/series/{series_code}/schedule",
        f"/series/{series_code}/tournaments",
    ]

    logger.info("=" * 80)
    logger.info("Direct HTTP Endpoint Verification")
    logger.info("=" * 80)

    results = {}

    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "exists": response.status_code == 200,
                "keys": list(response.json().keys()) if response.status_code == 200 else None,
            }

            if response.status_code == 200:
                logger.info(f"✓ {endpoint} - EXISTS (200)")
            elif response.status_code == 404:
                logger.info(f"✗ {endpoint} - NOT FOUND (404)")
            else:
                logger.info(f"⚠ {endpoint} - {response.status_code}")

        except Exception as e:
            logger.error(f"✗ {endpoint} - ERROR: {str(e)}")
            results[endpoint] = {"status": -1, "exists": False, "keys": None}

    logger.info("=" * 80)

    # Log summary
    existing_endpoints = [ep for ep, info in results.items() if info.get("exists")]
    missing_endpoints = [ep for ep, info in results.items() if not info.get("exists")]

    logger.info(f"\nEXISTING ENDPOINTS ({len(existing_endpoints)}):")
    for ep in existing_endpoints:
        logger.info(f"  - {ep}")

    logger.info(f"\nMISSING ENDPOINTS ({len(missing_endpoints)}):")
    for ep in missing_endpoints:
        logger.info(f"  - {ep}")

    return results
