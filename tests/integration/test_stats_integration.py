"""Integration tests for StatsClient.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration

IMPORTANT: These stats endpoints are NOT documented in the official IFPA API
OpenAPI specification (v2.1). This test suite validates whether these
undocumented endpoints actually exist and work in the live API.

NOTE: The Stats resource is not implemented in v0.1.0 and is planned for v0.2.0.
Type checking is disabled for this file to allow the test code to remain intact
for future implementation.
"""

import pytest

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
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
@pytest.mark.skip(
    reason="Stats resource not implemented in v0.1.0 - planned for v0.2.0 (see issue #2)"
)
class TestStatsClientIntegration:
    """Integration tests for StatsClient.

    WARNING: All endpoints tested here are NOT in the official IFPA API spec.
    These are either:
    - Undocumented experimental endpoints
    - Endpoints that don't exist (will return 404)
    - Future planned endpoints

    NOTE: This test class is skipped in v0.1.0. Stats endpoints are planned
    for implementation in v0.2.0.
    """

    def test_global_stats(self, api_key: str) -> None:
        """Test /stats/global endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.global_stats()  # type: ignore[attr-defined]
            assert isinstance(result, GlobalStats)
            # If successful, verify expected fields exist
            print(f"✅ /stats/global WORKS - Fields: {result.model_dump()}")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/global NOT FOUND (404) - Endpoint does not exist")
            else:
                print(f"⚠️ /stats/global ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_player_counts(self, api_key: str) -> None:
        """Test /stats/player_counts endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.player_counts()  # type: ignore[attr-defined]
            assert isinstance(result, PlayerCountStatsResponse)
            print(f"✅ /stats/player_counts WORKS - {len(result.stats)} stats returned")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/player_counts NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/player_counts ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_player_counts_with_period(self, api_key: str) -> None:
        """Test /stats/player_counts with period parameter (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.player_counts(period="year")  # type: ignore[attr-defined]
            assert isinstance(result, PlayerCountStatsResponse)
            print("✅ /stats/player_counts?period=year WORKS")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/player_counts?period=year NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/player_counts?period=year ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_tournament_counts(self, api_key: str) -> None:
        """Test /stats/tournament_counts endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.tournament_counts()  # type: ignore[attr-defined]
            assert isinstance(result, TournamentCountStatsResponse)
            print(f"✅ /stats/tournament_counts WORKS - {len(result.stats)} stats returned")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/tournament_counts NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/tournament_counts ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_top_countries(self, api_key: str) -> None:
        """Test /stats/top_countries endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.top_countries(limit=10)  # type: ignore[attr-defined]
            assert isinstance(result, TopCountriesResponse)
            print(f"✅ /stats/top_countries WORKS - {len(result.countries)} countries returned")
            # Verify structure if successful
            if len(result.countries) > 0:
                country = result.countries[0]
                print(f"  Sample country: {country.country_name}, players: {country.player_count}")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/top_countries NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/top_countries ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_top_tournaments(self, api_key: str) -> None:
        """Test /stats/top_tournaments endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.top_tournaments(  # type: ignore[attr-defined]
                criteria="size", limit=10
            )
            assert isinstance(result, TopTournamentsResponse)
            print(
                f"✅ /stats/top_tournaments WORKS - {len(result.tournaments)} tournaments returned"
            )
            if len(result.tournaments) > 0:
                tournament = result.tournaments[0]
                print(
                    f"  Sample tournament: {tournament.tournament_name}, "
                    f"players: {tournament.player_count}"
                )
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/top_tournaments NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/top_tournaments ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_recent_tournaments(self, api_key: str) -> None:
        """Test /stats/recent_tournaments endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.recent_tournaments(  # type: ignore[attr-defined]
                days=30, limit=20
            )
            assert isinstance(result, RecentTournamentsResponse)
            tournament_count = len(result.tournaments)
            print(
                f"✅ /stats/recent_tournaments WORKS - {tournament_count} tournaments " f"returned"
            )
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/recent_tournaments NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/recent_tournaments ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_machine_popularity(self, api_key: str) -> None:
        """Test /stats/machine_popularity endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.machine_popularity(  # type: ignore[attr-defined]
                period="year", limit=25
            )
            assert isinstance(result, MachinePopularityResponse)
            print(f"✅ /stats/machine_popularity WORKS - {len(result.machines)} machines returned")
            if len(result.machines) > 0:
                machine = result.machines[0]
                print(f"  Sample machine: {machine.machine_name}, usage: {machine.usage_count}")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/machine_popularity NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/machine_popularity ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_trends(self, api_key: str) -> None:
        """Test /stats/trends endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.trends(  # type: ignore[attr-defined]
                metric="players", period="year"
            )
            assert isinstance(result, TrendsResponse)
            print(f"✅ /stats/trends WORKS - {len(result.data_points)} data points returned")
            print(f"  Metric: {result.metric}, Trend: {result.trend_direction}")
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/trends NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/trends ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_historical(self, api_key: str) -> None:
        """Test /stats/historical endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.historical(  # type: ignore[attr-defined]
                start_year=2020, end_year=2024
            )
            assert isinstance(result, HistoricalStatsResponse)
            print(f"✅ /stats/historical WORKS - {len(result.stats)} years returned")
            if len(result.stats) > 0:
                year_stat = result.stats[0]
                print(
                    f"  Sample year: {year_stat.year}, players: {year_stat.total_players}, "
                    f"tournaments: {year_stat.total_tournaments}"
                )
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/historical NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/historical ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")

    def test_participation(self, api_key: str) -> None:
        """Test /stats/participation endpoint (NOT IN SPEC)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.stats.participation()  # type: ignore[attr-defined]
            assert isinstance(result, ParticipationStatsResponse)
            print(f"✅ /stats/participation WORKS - {len(result.stats)} categories returned")
            if len(result.stats) > 0:
                category = result.stats[0]
                print(
                    f"  Sample category: {category.category}, players: {category.player_count}, "
                    f"percentage: {category.percentage}%"
                )
        except IfpaApiError as e:
            if e.status_code == 404:
                print("❌ /stats/participation NOT FOUND (404)")
            else:
                print(f"⚠️ /stats/participation ERROR ({e.status_code}): {e}")
            pytest.skip(f"Endpoint not available: {e}")
