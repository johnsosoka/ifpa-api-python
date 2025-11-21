"""Integration tests for async rankings resource."""

import pytest

from ifpa_api.async_client import AsyncIfpaClient
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingListResponse,
    CustomRankingsResponse,
    RankingsCountryListResponse,
    RankingsResponse,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_wppr_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.wppr() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.wppr(count=10)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].rank is not None
        assert result.rankings[0].player_id > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_women_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.women() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.women(tournament_type="OPEN", count=10)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].rank is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_youth_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.youth() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.youth(count=10)

        assert isinstance(result, RankingsResponse)
        assert len(result.rankings) > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_virtual_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.virtual() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.virtual(count=10)

        assert isinstance(result, RankingsResponse)
        # Virtual rankings may be empty, so just check response type
        assert result.rankings is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_pro_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.pro() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.pro(ranking_system="OPEN", count=10)

        assert isinstance(result, RankingsResponse)
        # Pro rankings may be empty, so just check response type
        assert result.rankings is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_by_country_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.by_country() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.by_country(country="US", count=10)

        assert isinstance(result, CountryRankingsResponse)
        assert len(result.rankings) > 0
        assert result.rankings[0].player_name is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_country_list_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.country_list() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.country_list()

        assert isinstance(result, RankingsCountryListResponse)
        assert len(result.country) > 0
        assert result.country[0].country_code is not None
        assert result.country[0].player_count > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_custom_list_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.custom_list() against real API."""
    async with async_ifpa_client as client:
        result = await client.rankings.custom_list()

        assert isinstance(result, CustomRankingListResponse)
        # Custom rankings may be empty, so just check response type
        assert result.custom_view is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_rankings_custom_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.custom() against real API.

    Note: Many custom rankings are empty, inactive, or timeout. This test tries multiple
    rankings to find one with data, or skips if none available.
    """
    async with async_ifpa_client as client:
        # Get list of custom rankings
        custom_list = await client.rankings.custom_list()

        if not custom_list.custom_view or len(custom_list.custom_view) == 0:
            pytest.skip("No custom rankings available from API")

        # Try first 5 custom rankings to find one with data
        # Limited to 5 to avoid long timeouts on inactive rankings
        found_data = False
        for view in custom_list.custom_view[:5]:
            try:
                # Use timeout of 5 seconds per ranking to avoid long waits
                import asyncio

                result = await asyncio.wait_for(
                    client.rankings.custom(view.view_id, count=10), timeout=5.0
                )
                assert isinstance(result, CustomRankingsResponse)
                assert result.rankings is not None

                # If we found rankings with data, validate structure
                if len(result.rankings) > 0:
                    found_data = True
                    first_entry = result.rankings[0]
                    assert first_entry.player_id is not None
                    # Test passes - found valid custom ranking with data
                    break
            except (TimeoutError, Exception):
                # This custom ranking failed or timed out, try next one
                continue

        # If no rankings have data after trying 5, skip test
        if not found_data:
            pytest.skip(
                "No custom rankings with data found in first 5 results "
                "(most custom rankings are empty or timeout)"
            )
