"""Comprehensive audit tests for Rankings resource against live IFPA API.

This test suite audits all 7 implemented Rankings methods and investigates
2 potentially missing endpoints (country_list, custom_list).

Test Categories:
1. RankingsClient.wppr() - Main WPPR rankings
2. RankingsClient.women() - Women's rankings (OPEN/WOMEN)
3. RankingsClient.youth() - Youth rankings
4. RankingsClient.virtual() - Virtual rankings
5. RankingsClient.pro() - Pro circuit rankings (MAIN/WOMEN)
6. RankingsClient.by_country() - Country rankings
7. RankingsClient.custom() - Custom rankings
8. Missing Endpoints Investigation - country_list, custom_list
"""

import pytest
import requests

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingsResponse,
    RankingsResponse,
)

# ============================================================================
# Test Class 1: wppr() - Main WPPR Rankings
# ============================================================================


class TestWpprRankings:
    """Test RankingsClient.wppr() method."""

    @pytest.mark.integration
    def test_wppr_default(self, api_key: str) -> None:
        """Test wppr() with default parameters (top 100)."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr()

        assert isinstance(result, RankingsResponse)
        assert result.rankings is not None
        assert len(result.rankings) > 0
        assert result.rankings[0].player_id is not None
        assert result.rankings[0].rank is not None
        assert result.rankings[0].rating is not None

        print(f"\n✓ WPPR default returned {len(result.rankings)} rankings")
        print(f"  Top player: #{result.rankings[0].rank} {result.rankings[0].player_name}")
        print(f"  Rating: {result.rankings[0].rating}")

    @pytest.mark.integration
    def test_wppr_pagination_start_pos(self, api_key: str) -> None:
        """Test wppr() with start_pos parameter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr(start_pos=10, count=10)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 10
        # Verify we're getting results starting from position 10+
        assert result.rankings[0].rank is not None
        assert result.rankings[0].rank >= 10

        print(f"\n✓ WPPR pagination returned {len(result.rankings)} rankings")
        print(f"  Starting from rank: {result.rankings[0].rank}")

    @pytest.mark.integration
    def test_wppr_count_limit(self, api_key: str) -> None:
        """Test wppr() with count parameter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr(count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 25

        print(f"\n✓ WPPR count limit returned {len(result.rankings)} rankings (requested 25)")

    @pytest.mark.integration
    def test_wppr_250_max_limit(self, api_key: str) -> None:
        """Test wppr() 250 max count limit enforcement."""
        client = IfpaClient(api_key=api_key)
        # Request 250 (should work)
        result = client.rankings.wppr(count=250)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 250

        print(f"\n✓ WPPR max limit (250) returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_wppr_country_filter(self, api_key: str) -> None:
        """Test wppr() with country filter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr(country="CA", count=50)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        # Verify all results are from Canada
        for entry in result.rankings[:5]:  # Check first 5
            assert entry.country_code == "CA" or entry.country_code is None

        print(f"\n✓ WPPR country filter (CA) returned {len(result.rankings)} rankings")
        print(f"  Top CA player: {result.rankings[0].player_name}")

    @pytest.mark.integration
    def test_wppr_response_fields(self, api_key: str) -> None:
        """Test wppr() response field validation."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr(count=5)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0

        # Verify all expected fields on first entry
        entry = result.rankings[0]
        assert entry.player_id is not None
        assert entry.rank is not None  # Mapped from current_rank
        assert entry.player_name is not None  # Mapped from name
        assert entry.rating is not None  # Mapped from rating_value

        print("\n✓ WPPR response fields validated:")
        print(f"  player_id: {entry.player_id}")
        print(f"  rank (from current_rank): {entry.rank}")
        print(f"  player_name (from name): {entry.player_name}")
        print(f"  rating (from rating_value): {entry.rating}")
        print(f"  country_code: {entry.country_code}")


# ============================================================================
# Test Class 2: women() - Women's Rankings
# ============================================================================


class TestWomenRankings:
    """Test RankingsClient.women() method."""

    @pytest.mark.integration
    def test_women_open_tournaments(self, api_key: str) -> None:
        """Test women() with OPEN tournament type."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.women(tournament_type="OPEN", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].player_id is not None

        print(f"\n✓ Women's OPEN rankings returned {len(result.rankings)} rankings")
        print(f"  Top player: {result.rankings[0].player_name}")

    @pytest.mark.integration
    def test_women_women_only_tournaments(self, api_key: str) -> None:
        """Test women() with WOMEN tournament type."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.women(tournament_type="WOMEN", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0

        print(f"\n✓ Women's WOMEN-only rankings returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_women_pagination(self, api_key: str) -> None:
        """Test women() with pagination parameters."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.women(tournament_type="OPEN", start_pos=5, count=10)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 10

        print(f"\n✓ Women's rankings pagination returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_women_country_filter(self, api_key: str) -> None:
        """Test women() with country filter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.women(tournament_type="OPEN", country="US", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0

        print(f"\n✓ Women's rankings country filter (US) returned {len(result.rankings)} rankings")


# ============================================================================
# Test Class 3: youth() - Youth Rankings
# ============================================================================


class TestYouthRankings:
    """Test RankingsClient.youth() method."""

    @pytest.mark.integration
    def test_youth_default(self, api_key: str) -> None:
        """Test youth() with default parameters."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.youth()

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].player_id is not None

        print(f"\n✓ Youth rankings default returned {len(result.rankings)} rankings")
        print(f"  Top youth player: {result.rankings[0].player_name}")

    @pytest.mark.integration
    def test_youth_pagination(self, api_key: str) -> None:
        """Test youth() with pagination."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.youth(start_pos=5, count=15)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 15

        print(f"\n✓ Youth rankings pagination returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_youth_country_filter(self, api_key: str) -> None:
        """Test youth() with country filter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.youth(country="US", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0

        print(f"\n✓ Youth rankings country filter (US) returned {len(result.rankings)} rankings")


# ============================================================================
# Test Class 4: virtual() - Virtual Rankings
# ============================================================================


class TestVirtualRankings:
    """Test RankingsClient.virtual() method."""

    @pytest.mark.integration
    def test_virtual_default(self, api_key: str) -> None:
        """Test virtual() with default parameters."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.virtual()

        assert isinstance(result, RankingsResponse)
        # Virtual rankings may be empty or populated
        print(f"\n✓ Virtual rankings returned {len(result.rankings)} rankings")
        if len(result.rankings) > 0:
            print(f"  Top virtual player: {result.rankings[0].player_name}")
        else:
            print("  Note: Virtual rankings are empty")

    @pytest.mark.integration
    def test_virtual_pagination(self, api_key: str) -> None:
        """Test virtual() with pagination."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.virtual(start_pos=0, count=25)

        assert isinstance(result, RankingsResponse)
        print(f"\n✓ Virtual rankings pagination returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_virtual_country_filter(self, api_key: str) -> None:
        """Test virtual() with country filter."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.virtual(country="US", count=25)

        assert isinstance(result, RankingsResponse)
        print(f"\n✓ Virtual rankings country filter (US) returned {len(result.rankings)} rankings")


# ============================================================================
# Test Class 5: pro() - Pro Circuit Rankings
# ============================================================================


class TestProRankings:
    """Test RankingsClient.pro() method."""

    @pytest.mark.integration
    def test_pro_main_system(self, api_key: str) -> None:
        """Test pro() with MAIN ranking system."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.pro(ranking_system="OPEN", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].player_id is not None

        print(f"\n✓ Pro OPEN rankings returned {len(result.rankings)} rankings")
        print(f"  Top pro: {result.rankings[0].player_name}")

    @pytest.mark.integration
    def test_pro_women_system(self, api_key: str) -> None:
        """Test pro() with WOMEN ranking system."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.pro(ranking_system="WOMEN", count=25)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0

        print(f"\n✓ Pro WOMEN rankings returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_pro_pagination(self, api_key: str) -> None:
        """Test pro() with pagination."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.pro(ranking_system="OPEN", start_pos=5, count=15)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 15

        print(f"\n✓ Pro rankings pagination returned {len(result.rankings)} rankings")


# ============================================================================
# Test Class 6: by_country() - Country Rankings
# ============================================================================


class TestCountryRankings:
    """Test RankingsClient.by_country() method."""

    @pytest.mark.integration
    def test_by_country_code(self, api_key: str) -> None:
        """Test by_country() with country code."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.by_country(country="US", count=25)

        assert isinstance(result, CountryRankingsResponse)
        assert result.rankings is not None
        assert len(result.rankings) > 0

        # Verify structure - this endpoint returns player rankings for a specific country
        entry = result.rankings[0]
        assert entry.rank is not None
        assert entry.player_id is not None
        assert entry.player_name is not None
        assert entry.country_code is not None
        assert entry.country_name is not None

        print(f"\n✓ Country rankings by code (US) returned {len(result.rankings)} players")
        print(f"  Top player: #{entry.rank} {entry.player_name}")
        print(f"  Country: {entry.country_name}")

    @pytest.mark.integration
    def test_by_country_name(self, api_key: str) -> None:
        """Test by_country() with country name."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.by_country(country="Canada", count=25)

        assert isinstance(result, CountryRankingsResponse)
        assert len(result.rankings) > 0

        print(f"\n✓ Country rankings by name (Canada) returned {len(result.rankings)} players")

    @pytest.mark.integration
    def test_by_country_pagination(self, api_key: str) -> None:
        """Test by_country() with pagination."""
        client = IfpaClient(api_key=api_key)
        # Note: API uses 1-based indexing for start_pos (start_pos=0 causes SQL error)
        result = client.rankings.by_country(country="US", start_pos=1, count=10)

        assert isinstance(result, CountryRankingsResponse)
        assert len(result.rankings) > 0
        assert len(result.rankings) <= 10

        print(f"\n✓ Country rankings pagination returned {len(result.rankings)} players")

    @pytest.mark.integration
    def test_by_country_response_fields(self, api_key: str) -> None:
        """Test by_country() response field validation."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.by_country(country="US", count=5)

        assert len(result.rankings) > 0

        # Verify all expected fields on first entry (player ranking fields)
        entry = result.rankings[0]
        assert entry.rank is not None
        assert entry.player_id is not None
        assert entry.player_name is not None
        assert entry.country_code is not None
        assert entry.country_name is not None

        print("\n✓ Country rankings response fields validated:")
        print(f"  rank: {entry.rank}")
        print(f"  player_id: {entry.player_id}")
        print(f"  player_name: {entry.player_name}")
        print(f"  country_code: {entry.country_code}")
        print(f"  country_name: {entry.country_name}")
        print(f"  wppr_points: {entry.wppr_points}")
        print(f"  rating: {entry.rating}")


# ============================================================================
# Test Class 7: custom() - Custom Rankings
# ============================================================================


class TestCustomRankings:
    """Test RankingsClient.custom() method."""

    @pytest.mark.integration
    def test_custom_valid_ranking_id(self, api_key: str) -> None:
        """Test custom() with a valid custom ranking ID.

        Note: We need to discover valid custom ranking IDs.
        This test will attempt common ones or fail gracefully.
        """
        client = IfpaClient(api_key=api_key)

        # Try a few potential custom ranking IDs
        test_ids = ["1", "100", "regional-2024", "custom"]

        found_valid = False
        for ranking_id in test_ids:
            try:
                result = client.rankings.custom(ranking_id, count=25)
                if isinstance(result, CustomRankingsResponse):
                    found_valid = True
                    print(
                        f"\n✓ Custom rankings (ID: {ranking_id}) "
                        f"returned {len(result.rankings)} rankings"
                    )
                    if result.ranking_name:
                        print(f"  Ranking name: {result.ranking_name}")
                    break
            except IfpaApiError:
                continue

        if not found_valid:
            print("\n⚠️ Could not find valid custom ranking ID to test")
            print("   Tried IDs: " + ", ".join(test_ids))
            pytest.skip("No valid custom ranking ID found for testing")

    @pytest.mark.integration
    def test_custom_invalid_ranking_id(self, api_key: str) -> None:
        """Test custom() with invalid ranking ID."""
        client = IfpaClient(api_key=api_key)

        with pytest.raises(IfpaApiError) as exc_info:
            client.rankings.custom("invalid-999999", count=10)

        assert exc_info.value.status_code is not None
        print("\n✓ Custom rankings invalid ID correctly raised IfpaApiError")
        print(f"  Status code: {exc_info.value.status_code}")

    @pytest.mark.integration
    def test_custom_pagination(self, api_key: str) -> None:
        """Test custom() with pagination parameters.

        This test depends on finding a valid custom ranking ID.
        """
        client = IfpaClient(api_key=api_key)

        # Try to find a valid ID first
        test_ids = ["1", "100"]
        valid_id = None

        for ranking_id in test_ids:
            try:
                result = client.rankings.custom(ranking_id, count=5)
                if isinstance(result, CustomRankingsResponse) and len(result.rankings) > 0:
                    valid_id = ranking_id
                    break
            except IfpaApiError:
                continue

        if valid_id:
            result = client.rankings.custom(valid_id, start_pos=0, count=10)
            assert isinstance(result, CustomRankingsResponse)
            assert len(result.rankings) <= 10
            print(
                f"\n✓ Custom rankings pagination (ID: {valid_id}) "
                f"returned {len(result.rankings)} rankings"
            )
        else:
            pytest.skip("No valid custom ranking ID found for pagination test")


# ============================================================================
# Test Class 8: Missing Endpoints Investigation
# ============================================================================


class TestMissingEndpoints:
    """Investigate potentially missing endpoints: country_list and custom_list."""

    @pytest.mark.integration
    def test_investigate_country_list_endpoint(self, api_key: str) -> None:
        """Test if /rankings/country_list endpoint exists in live API."""
        base_url = "https://api.ifpapinball.com"
        endpoint = "/rankings/country_list"

        response = requests.get(f"{base_url}{endpoint}", headers={"X-API-Key": api_key})

        print(f"\n=== Investigating {endpoint} ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✓ Endpoint EXISTS!")
            try:
                data = response.json()
                print("\nResponse Structure:")
                print(f"  Keys: {list(data.keys())}")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"  {key}: list with {len(value)} items")
                            print(f"    First item: {value[0]}")
                        else:
                            print(f"  {key}: {type(value).__name__}")
            except Exception as e:
                print(f"Could not parse JSON: {e}")
                print(f"Raw response: {response.text[:500]}")
        elif response.status_code == 404:
            print("❌ Endpoint NOT FOUND (404)")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    @pytest.mark.integration
    def test_investigate_custom_list_endpoint(self, api_key: str) -> None:
        """Test if /rankings/custom/list endpoint exists in live API."""
        base_url = "https://api.ifpapinball.com"
        endpoint = "/rankings/custom/list"

        response = requests.get(f"{base_url}{endpoint}", headers={"X-API-Key": api_key})

        print(f"\n=== Investigating {endpoint} ===")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✓ Endpoint EXISTS!")
            try:
                data = response.json()
                print("\nResponse Structure:")
                print(f"  Keys: {list(data.keys())}")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"  {key}: list with {len(value)} items")
                            print(f"    First item: {value[0]}")
                        else:
                            print(f"  {key}: {type(value).__name__}")
            except Exception as e:
                print(f"Could not parse JSON: {e}")
                print(f"Raw response: {response.text[:500]}")
        elif response.status_code == 404:
            print("❌ Endpoint NOT FOUND (404)")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")

    @pytest.mark.integration
    def test_investigate_custom_endpoint_alternatives(self, api_key: str) -> None:
        """Test alternative custom rankings endpoints."""
        base_url = "https://api.ifpapinball.com"
        alternatives = [
            "/rankings/custom",
            "/rankings/custom_list",
            "/rankings/customlist",
            "/custom/rankings",
        ]

        print("\n=== Testing Alternative Custom Ranking Endpoints ===")

        for endpoint in alternatives:
            response = requests.get(f"{base_url}{endpoint}", headers={"X-API-Key": api_key})
            print(f"{endpoint}: {response.status_code}")

            if response.status_code == 200:
                print(f"  ✓ EXISTS! Response keys: {list(response.json().keys())}")


# ============================================================================
# Test Class 9: Cross-Method Validation
# ============================================================================


class TestCrossMethodValidation:
    """Test data consistency across different ranking methods."""

    @pytest.mark.integration
    def test_wppr_vs_country_rankings_consistency(self, api_key: str) -> None:
        """Verify data consistency between wppr() and by_country()."""
        client = IfpaClient(api_key=api_key)

        # Get US rankings from wppr
        wppr_result = client.rankings.wppr(country="US", count=10)

        # Get country rankings (player rankings for a specific country)
        country_result = client.rankings.by_country(country="US", count=5)

        assert len(wppr_result.rankings) > 0
        assert len(country_result.rankings) > 0

        print("\n✓ WPPR and country rankings both returned data for US")
        print(f"  WPPR US players: {len(wppr_result.rankings)}")
        print(f"  Country rankings (US players): {len(country_result.rankings)}")

    @pytest.mark.integration
    def test_ranking_field_mapping(self, api_key: str) -> None:
        """Verify field name mappings work correctly (current_rank -> rank, etc.)."""
        client = IfpaClient(api_key=api_key)
        result = client.rankings.wppr(count=5)

        assert len(result.rankings) > 0

        for entry in result.rankings:
            # Verify mapped fields are accessible
            assert entry.rank is not None  # Mapped from current_rank
            assert entry.player_name is not None  # Mapped from name
            assert entry.rating is not None  # Mapped from rating_value

        print("\n✓ Field mappings verified:")
        print("  rank (from current_rank) ✓")
        print("  player_name (from name) ✓")
        print("  rating (from rating_value) ✓")


# ============================================================================
# Test Class 10: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCasesAndErrors:
    """Test edge cases and error handling for rankings methods."""

    @pytest.mark.integration
    def test_wppr_large_pagination(self, api_key: str) -> None:
        """Test wppr() with very large start_pos."""
        client = IfpaClient(api_key=api_key)

        # Request rankings starting at position 10000
        result = client.rankings.wppr(start_pos=10000, count=10)

        assert isinstance(result, RankingsResponse)
        # May return empty if no rankings at that position
        print(
            f"\n✓ WPPR large pagination (start_pos=10000) returned {len(result.rankings)} rankings"
        )

    @pytest.mark.integration
    def test_country_filter_invalid_code(self, api_key: str) -> None:
        """Test rankings with invalid country code."""
        client = IfpaClient(api_key=api_key)

        # Use invalid country code
        result = client.rankings.wppr(country="ZZ", count=10)

        assert isinstance(result, RankingsResponse)
        # May return empty results
        print(f"\n✓ WPPR invalid country code (ZZ) returned {len(result.rankings)} rankings")

    @pytest.mark.integration
    def test_count_over_250_limit(self, api_key: str) -> None:
        """Test wppr() with count over 250 (should be handled by API)."""
        client = IfpaClient(api_key=api_key)

        # Request more than 250 (API should cap it)
        result = client.rankings.wppr(count=500)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) <= 250

        print(f"\n✓ WPPR count=500 capped to {len(result.rankings)} rankings")
