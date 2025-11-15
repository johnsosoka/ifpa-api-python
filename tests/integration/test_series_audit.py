"""Comprehensive audit tests for Series resource.

This test suite audits all Series methods against the live IFPA API to verify:
1. Actual endpoint paths (especially critical for standings)
2. Response structure matches models
3. Which "extra" methods actually exist in the API (overview, rules, schedule)
4. Whether tournaments endpoint exists
5. All parameter combinations work correctly

CRITICAL: This test includes network logging to capture actual endpoint URLs.
"""

import logging

import pytest
import requests

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
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

# Enable detailed HTTP logging to capture actual endpoint paths
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# URL capturing is handled by enabling DEBUG logging which shows requests


# =============================================================================
# TEST 1: SeriesClient.list() - List all series
# =============================================================================


@pytest.mark.integration
def test_list_all_series(api_key: str) -> None:
    """Test SeriesClient.list() without filters."""
    client = IfpaClient(api_key=api_key)

    result = client.series.list()

    # Validate response structure
    assert isinstance(result, SeriesListResponse)
    assert hasattr(result, "series")
    assert isinstance(result.series, list)

    # Verify we got series data
    assert len(result.series) > 0, "Expected at least one series"

    # Check first series structure
    first_series = result.series[0]
    assert hasattr(first_series, "series_code")
    assert hasattr(first_series, "series_name")

    logger.info(f"✓ list() returned {len(result.series)} series")
    logger.info(f"  Sample series: {first_series.series_code} - {first_series.series_name}")


@pytest.mark.integration
def test_list_active_only_true(api_key: str) -> None:
    """Test SeriesClient.list() with active_only=True."""
    client = IfpaClient(api_key=api_key)

    result = client.series.list(active_only=True)

    assert isinstance(result, SeriesListResponse)
    assert len(result.series) > 0, "Expected at least one active series"

    logger.info(f"✓ list(active_only=True) returned {len(result.series)} active series")


@pytest.mark.integration
def test_list_active_only_false(api_key: str) -> None:
    """Test SeriesClient.list() with active_only=False."""
    client = IfpaClient(api_key=api_key)

    result = client.series.list(active_only=False)

    assert isinstance(result, SeriesListResponse)
    assert len(result.series) > 0

    logger.info(f"✓ list(active_only=False) returned {len(result.series)} total series")


# =============================================================================
# TEST 2: SeriesHandle.standings() - CRITICAL ENDPOINT PATH INVESTIGATION
# =============================================================================


@pytest.mark.integration
def test_standings_endpoint_path_investigation(api_key: str) -> None:
    """Test overall_standings endpoint - returns region overviews, not player standings.

    The standings() method calls /overall_standings and returns SeriesStandingsResponse
    with overall_results field containing region overviews.
    """
    client = IfpaClient(api_key=api_key)

    series_code = "NACS"  # North American Championship Series
    try:
        result = client.series_handle(series_code).standings()

        logger.info("=" * 80)
        logger.info("🚨 CRITICAL: standings() test")
        logger.info(f"Series code: {series_code}")
        logger.info(f"SDK method: client.series_handle('{series_code}').standings()")
        logger.info(f"Actual SDK endpoint: /series/{series_code}/overall_standings")
        logger.info("=" * 80)

        # Validate response
        assert isinstance(result, SeriesStandingsResponse)
        assert hasattr(result, "overall_results")
        assert isinstance(result.overall_results, list)
        assert len(result.overall_results) > 0

        logger.info(f"✓ standings() returned {len(result.overall_results)} region overviews")
        logger.info(f"  Series: {result.series_code} ({result.year})")
        logger.info(f"  Championship Prize Fund: ${result.championship_prize_fund}")

    except IfpaApiError as e:
        logger.error(f"❌ standings() failed: {e}")
        logger.error(f"Status code: {e.status_code}")
        logger.error(f"Response: {e.response_body}")
        raise


@pytest.mark.integration
def test_standings_with_pagination(api_key: str) -> None:
    """Test standings() with pagination parameters (note: API may not use these)."""
    client = IfpaClient(api_key=api_key)

    result = client.series_handle("NACS").standings(start_pos=0, count=10)

    assert isinstance(result, SeriesStandingsResponse)
    assert hasattr(result, "overall_results")

    logger.info(
        f"✓ standings(start_pos=0, count=10) "
        f"returned {len(result.overall_results)} region overviews"
    )


# =============================================================================
# TEST 2B: SeriesHandle.region_standings() - Region-specific player standings
# =============================================================================


@pytest.mark.integration
def test_region_standings_basic(api_key: str) -> None:
    """Test region_standings() to get detailed player standings for a region."""
    client = IfpaClient(api_key=api_key)

    result = client.series_handle("NACS").region_standings(region_code="OH")

    assert isinstance(result, SeriesRegionStandingsResponse)
    assert hasattr(result, "standings")
    assert isinstance(result.standings, list)
    assert len(result.standings) > 0

    logger.info(f"✓ region_standings('OH') returned {len(result.standings)} player standings")
    logger.info(f"  Region: {result.region_name}")
    logger.info(f"  Prize Fund: {result.prize_fund}")


@pytest.mark.integration
def test_region_standings_with_pagination(api_key: str) -> None:
    """Test region_standings() with pagination parameters (note: API may ignore these)."""
    client = IfpaClient(api_key=api_key)

    result = client.series_handle("NACS").region_standings(region_code="OH", start_pos=0, count=5)

    assert isinstance(result, SeriesRegionStandingsResponse)
    # Note: API appears to ignore pagination parameters and returns all results
    assert len(result.standings) > 0

    logger.info(
        f"✓ region_standings('OH', start_pos=0, count=5) returned {len(result.standings)} standings"
    )
    logger.info("  (Note: API may ignore pagination parameters)")


# =============================================================================
# TEST 3: SeriesHandle.player_card() - Player series card
# =============================================================================


@pytest.mark.integration
def test_player_card_basic(api_key: str) -> None:
    """Test player_card() with required parameters only."""
    client = IfpaClient(api_key=api_key)

    # Use a known player ID (Josh Sharpe) and region
    player_id = 14
    region_code = "OH"

    result = client.series_handle("NACS").player_card(player_id, region_code)

    assert isinstance(result, SeriesPlayerCard)
    assert result.player_id == player_id

    logger.info(f"✓ player_card({player_id}, {region_code}) successful")
    logger.info(f"  Player: {result.player_name}")
    logger.info(f"  Events: {len(result.player_card)} events")


@pytest.mark.integration
def test_player_card_with_year(api_key: str) -> None:
    """Test player_card() with year parameter."""
    client = IfpaClient(api_key=api_key)

    player_id = 14
    region_code = "OH"
    year = 2023

    result = client.series_handle("NACS").player_card(player_id, region_code, year=year)

    assert isinstance(result, SeriesPlayerCard)
    assert result.player_id == player_id

    logger.info(f"✓ player_card({player_id}, {region_code}, year={year}) successful")


@pytest.mark.integration
def test_player_card_different_region(api_key: str) -> None:
    """Test player_card() with different region codes."""
    client = IfpaClient(api_key=api_key)

    player_id = 14
    region_code = "IL"  # Different region

    result = client.series_handle("NACS").player_card(player_id, region_code)

    assert isinstance(result, SeriesPlayerCard)

    logger.info(f"✓ player_card with region {region_code} successful")


# =============================================================================
# TEST 4: SeriesHandle.regions() - List series regions
# =============================================================================


@pytest.mark.integration
def test_regions(api_key: str) -> None:
    """Test regions() method - requires region_code and year parameters."""
    client = IfpaClient(api_key=api_key)

    # regions() now requires region_code and year
    result = client.series_handle("NACS").regions(region_code="OH", year=2025)

    assert isinstance(result, SeriesRegionsResponse)
    assert hasattr(result, "active_regions")
    assert isinstance(result.active_regions, list)

    if len(result.active_regions) > 0:
        first_region = result.active_regions[0]
        assert hasattr(first_region, "region_code")
        assert hasattr(first_region, "region_name")

        logger.info(
            f"✓ regions(region_code='OH', year=2025) returned {len(result.active_regions)} regions"
        )
        logger.info(f"  Sample: {first_region.region_code} - {first_region.region_name}")
    else:
        logger.warning("⚠️  regions() returned empty list")


# =============================================================================
# TEST 5: SeriesHandle.region_reps() - Region representatives
# =============================================================================


@pytest.mark.integration
def test_region_reps(api_key: str) -> None:
    """Test region_reps() method."""
    client = IfpaClient(api_key=api_key)

    result = client.series_handle("NACS").region_reps()

    assert isinstance(result, RegionRepsResponse)
    assert hasattr(result, "representative")
    assert isinstance(result.representative, list)

    if len(result.representative) > 0:
        first_rep = result.representative[0]
        assert hasattr(first_rep, "player_id")
        assert hasattr(first_rep, "name")
        assert hasattr(first_rep, "region_code")

        logger.info(f"✓ region_reps() returned {len(result.representative)} reps")
        logger.info(f"  Sample: {first_rep.name} ({first_rep.region_name})")
    else:
        logger.warning("⚠️  region_reps() returned empty list")


# =============================================================================
# TEST 6: SeriesHandle.stats() - Series statistics
# =============================================================================


@pytest.mark.integration
def test_stats(api_key: str) -> None:
    """Test stats() method - requires region_code parameter."""
    client = IfpaClient(api_key=api_key)

    # stats() now requires region_code parameter
    result = client.series_handle("NACS").stats(region_code="OH")

    assert isinstance(result, SeriesStats)
    assert hasattr(result, "series_code")

    logger.info("✓ stats(region_code='OH') successful")
    logger.info(f"  Total events: {result.total_events}")
    logger.info(f"  Total players: {result.total_players}")


# =============================================================================
# TEST 7-9: Verify deleted methods raise AttributeError
# =============================================================================


@pytest.mark.integration
def test_overview_method_removed(api_key: str) -> None:
    """Verify overview() method was removed from Phase 1 implementation."""
    client = IfpaClient(api_key=api_key)

    try:
        client.series_handle("NACS").overview()  # type: ignore[attr-defined]
        raise AssertionError("overview() should not exist")
    except AttributeError:
        logger.info("✓ overview() correctly raises AttributeError (method removed)")


@pytest.mark.integration
def test_rules_method_removed(api_key: str) -> None:
    """Verify rules() method was removed from Phase 1 implementation."""
    client = IfpaClient(api_key=api_key)

    try:
        client.series_handle("NACS").rules()  # type: ignore[attr-defined]
        raise AssertionError("rules() should not exist")
    except AttributeError:
        logger.info("✓ rules() correctly raises AttributeError (method removed)")


@pytest.mark.integration
def test_schedule_method_removed(api_key: str) -> None:
    """Verify schedule() method was removed from Phase 1 implementation."""
    client = IfpaClient(api_key=api_key)

    try:
        client.series_handle("NACS").schedule()  # type: ignore[attr-defined]
        raise AssertionError("schedule() should not exist")
    except AttributeError:
        logger.info("✓ schedule() correctly raises AttributeError (method removed)")


# =============================================================================
# TEST 10: Test tournaments endpoint - requires region_code
# =============================================================================


@pytest.mark.integration
def test_tournaments_endpoint(api_key: str) -> None:
    """Test tournaments() method - requires region_code parameter."""
    client = IfpaClient(api_key=api_key)

    # tournaments() now requires region_code parameter
    result = client.series_handle("NACS").tournaments(region_code="OH")

    assert isinstance(result, SeriesTournamentsResponse)
    assert hasattr(result, "tournaments")
    assert isinstance(result.tournaments, list)

    logger.info("✓ tournaments(region_code='OH') successful")
    logger.info(f"  Found {len(result.tournaments)} tournaments")

    if len(result.tournaments) > 0:
        first_tournament = result.tournaments[0]
        logger.info(f"  Sample: {first_tournament.tournament_name}")


# =============================================================================
# TEST 11: Direct HTTP endpoint verification
# =============================================================================


@pytest.mark.integration
def test_direct_http_endpoint_verification(
    api_key: str,
) -> dict[str, dict[str, int | list[str] | None | bool]]:
    """Use direct HTTP calls to verify all series endpoints.

    This test bypasses the SDK to directly test each endpoint against the API.
    """
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
    logger.info("🔍 DIRECT HTTP ENDPOINT VERIFICATION")
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
                logger.warning(f"❌ {endpoint} - NOT FOUND (404)")
            else:
                logger.warning(f"⚠️  {endpoint} - {response.status_code}")

        except Exception as e:
            logger.error(f"❌ {endpoint} - ERROR: {str(e)}")
            results[endpoint] = {"status": -1, "exists": False, "keys": None}

    logger.info("=" * 80)

    # Log summary
    existing_endpoints = [ep for ep, info in results.items() if info.get("exists")]
    missing_endpoints = [ep for ep, info in results.items() if not info.get("exists")]

    logger.info(f"\n✓ EXISTING ENDPOINTS ({len(existing_endpoints)}):")
    for ep in existing_endpoints:
        logger.info(f"  - {ep}")

    logger.info(f"\n❌ MISSING ENDPOINTS ({len(missing_endpoints)}):")
    for ep in missing_endpoints:
        logger.info(f"  - {ep}")

    return results


# =============================================================================
# TEST 12: Multiple series codes
# =============================================================================


@pytest.mark.integration
def test_multiple_series_codes(api_key: str) -> None:
    """Test series methods with different series codes."""
    client = IfpaClient(api_key=api_key)

    # Get list of series first
    series_list = client.series.list(active_only=True)
    assert len(series_list.series) > 0

    # Test with first few series codes
    test_codes = [s.series_code for s in series_list.series[:3]]

    logger.info(f"Testing with series codes: {test_codes}")

    for code in test_codes:
        try:
            _ = client.series_handle(code).standings(count=5)
            logger.info(f"✓ Series '{code}' standings accessible")
        except IfpaApiError as e:
            logger.warning(f"⚠️  Series '{code}' standings failed: {e.status_code}")
