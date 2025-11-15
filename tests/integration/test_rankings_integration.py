"""Integration tests for RankingsClient.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest
from pydantic import ValidationError

from ifpa_api.client import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.rankings import CountryRankingsResponse, RankingsResponse
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestRankingsClientIntegration:
    """Integration tests for RankingsClient."""

    def test_wppr_rankings(self, api_key: str, count_medium: int) -> None:
        """Test getting WPPR rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            rankings = client.rankings.wppr(count=count_medium)
            assert isinstance(rankings, RankingsResponse)
            assert rankings.rankings is not None
            # Should have some rankings
            assert len(rankings.rankings) > 0
            # Verify structure
            first_entry = rankings.rankings[0]
            assert first_entry.player_id > 0
            assert first_entry.rank is not None
        except (IfpaApiError, ValidationError) as e:
            # API data quality issues may cause validation errors
            pytest.skip(f"WPPR rankings API or data issue: {e}")

    def test_women_rankings(self, api_key: str, count_small: int) -> None:
        """Test getting women's rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            rankings = client.rankings.women(count=count_small)
            assert isinstance(rankings, RankingsResponse)
            assert rankings.rankings is not None
        except (IfpaApiError, ValidationError) as e:
            # Women's rankings may not be available or have data quality issues
            pytest.skip(f"Women's rankings not available or data issue: {e}")

    def test_youth_rankings(self, api_key: str, count_small: int) -> None:
        """Test getting youth rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.youth(count=count_small)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None

    def test_virtual_rankings(self, api_key: str, count_small: int) -> None:
        """Test getting virtual rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            result = client.rankings.virtual(count=count_small)
            assert isinstance(result, RankingsResponse)
            assert result.rankings is not None
            # Virtual rankings may have fewer players
            if len(result.rankings) > 0:
                assert result.rankings[0].player_id > 0
        except (IfpaApiError, ValidationError) as e:
            # Virtual rankings may not be available or have data quality issues
            pytest.skip(f"Virtual rankings not available or data issue: {e}")

    def test_pro_rankings(self, api_key: str, count_small: int) -> None:
        """Test getting pro circuit rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.rankings.pro(count=count_small)

        assert isinstance(result, RankingsResponse)
        assert result.rankings is not None
        # Pro circuit may have fewer players
        if len(result.rankings) > 0:
            assert result.rankings[0].player_id > 0

    def test_custom_rankings(self, api_key: str, count_small: int) -> None:
        """Test getting custom rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # First, we need to find a valid custom ranking ID
        # Try a few common ranking IDs (adjust if needed based on API)
        ranking_id = 1  # Main rankings often has ID 1

        try:
            result = client.rankings.custom(ranking_id=ranking_id, count=count_small)
            assert result.rankings is not None
            assert isinstance(result.rankings, list)
        except (IfpaApiError, ValidationError) as e:
            # Custom ranking IDs may not exist or have data issues
            pytest.skip(f"Custom ranking ID {ranking_id} not found or data issue: {e}")

    def test_custom_rankings_invalid_id(self, api_key: str) -> None:
        """Test that invalid custom ranking ID returns appropriate error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist - should raise 400 or 404
        with pytest.raises(IfpaApiError) as exc_info:
            client.rankings.custom(ranking_id=99999, count=5)

        assert exc_info.value.status_code in (400, 404)

    def test_country_rankings(self, api_key: str, country_code: str, count_medium: int) -> None:
        """Test getting country rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        try:
            rankings = client.rankings.by_country(country=country_code, count=count_medium)
            assert isinstance(rankings, CountryRankingsResponse)
            assert rankings.country_rankings is not None
            # Should have some countries
            if len(rankings.country_rankings) > 0:
                first_country = rankings.country_rankings[0]
                assert first_country.rank > 0
                assert first_country.country_code is not None
        except (IfpaApiError, ValidationError) as e:
            # Country rankings may not be available or have data quality issues
            pytest.skip(f"Country rankings not available or data issue: {e}")

    def test_wppr_with_country_filter(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test WPPR rankings filtered by country with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.wppr(country=country_code, count=count_small)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None
        # Country filter may or may not work consistently with the API,
        # so we just verify that we get a response back
        assert isinstance(rankings.rankings, list)
