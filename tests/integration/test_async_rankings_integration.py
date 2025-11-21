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
@pytest.mark.skip(reason="Requires valid custom ranking ID from custom_list() endpoint")
async def test_async_rankings_custom_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async rankings.custom() against real API."""
    async with async_ifpa_client as client:
        # First get list of custom rankings
        custom_list = await client.rankings.custom_list()
        if custom_list.custom_view and len(custom_list.custom_view) > 0:
            ranking_id = custom_list.custom_view[0].view_id
            result = await client.rankings.custom(ranking_id, count=10)

            assert isinstance(result, CustomRankingsResponse)
            assert result.rankings is not None
