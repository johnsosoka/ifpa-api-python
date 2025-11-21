"""Integration tests for async series resource."""

import pytest

from ifpa_api.async_client import AsyncIfpaClient
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


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_list_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.list() against real API."""
    async with async_ifpa_client as client:
        result = await client.series.list()

        assert isinstance(result, SeriesListResponse)
        assert len(result.series) > 0
        assert result.series[0].series_code is not None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid active series code from API")
async def test_async_series_standings_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.standings() against real API."""
    async with async_ifpa_client as client:
        # First get list of series
        series_list = await client.series.list(active_only=True)
        if series_list.series and len(series_list.series) > 0:
            series_code = series_list.series[0].series_code
            result = await client.series(series_code).standings()

            assert isinstance(result, SeriesStandingsResponse)
            assert result.series_code == series_code


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid series code and region from API")
async def test_async_series_region_standings_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async series.region_standings() against real API."""
    async with async_ifpa_client as client:
        # Would need valid series code and region code
        result = await client.series("NACS").region_standings("OH")

        assert isinstance(result, SeriesRegionStandingsResponse)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid player/series/region combination from API")
async def test_async_series_player_card_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.player_card() against real API."""
    async with async_ifpa_client as client:
        # Would need valid player_id, series code, and region code
        result = await client.series("PAPA").player_card(12345, "OH")

        assert isinstance(result, SeriesPlayerCard)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid series code and region from API")
async def test_async_series_regions_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.regions() against real API."""
    async with async_ifpa_client as client:
        result = await client.series("NACS").regions("OH", 2024)

        assert isinstance(result, SeriesRegionsResponse)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid series code and region from API")
async def test_async_series_stats_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.stats() against real API."""
    async with async_ifpa_client as client:
        result = await client.series("NACS").stats("OH")

        assert isinstance(result, SeriesStats)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid series code and region from API")
async def test_async_series_tournaments_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.tournaments() against real API."""
    async with async_ifpa_client as client:
        result = await client.series("NACS").tournaments("OH")

        assert isinstance(result, SeriesTournamentsResponse)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip(reason="Requires valid series code from API")
async def test_async_series_region_reps_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async series.region_reps() against real API."""
    async with async_ifpa_client as client:
        result = await client.series("PAPA").region_reps()

        assert isinstance(result, RegionRepsResponse)
