"""Integration tests for RankingsClient.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.models.rankings import CountryRankingsResponse, RankingsResponse
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestRankingsClientIntegration:
    """Integration tests for RankingsClient."""

    def test_wppr_rankings(self, api_key: str) -> None:
        """Test getting WPPR rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.wppr(start_pos=0, count=10)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None
        # Should have some rankings
        assert len(rankings.rankings) > 0
        # Verify structure
        first_entry = rankings.rankings[0]
        assert first_entry.player_id > 0
        assert first_entry.rank is not None

    def test_women_rankings(self, api_key: str) -> None:
        """Test getting women's rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.women(count=5)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None

    def test_youth_rankings(self, api_key: str) -> None:
        """Test getting youth rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.youth(count=5)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None

    def test_country_rankings(self, api_key: str) -> None:
        """Test getting country rankings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.by_country(count=10)

        assert isinstance(rankings, CountryRankingsResponse)
        assert rankings.country_rankings is not None
        # Should have some countries
        if len(rankings.country_rankings) > 0:
            first_country = rankings.country_rankings[0]
            assert first_country.rank > 0
            assert first_country.country_code is not None

    def test_wppr_with_country_filter(self, api_key: str) -> None:
        """Test WPPR rankings filtered by country with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        rankings = client.rankings.wppr(country="US", count=5)

        assert isinstance(rankings, RankingsResponse)
        assert rankings.rankings is not None
        # If results exist, verify they match filter
        if len(rankings.rankings) > 0:
            for entry in rankings.rankings:
                if entry.country_code:
                    assert entry.country_code == "US"
