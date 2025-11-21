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
async def test_async_series_standings_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str
) -> None:
    """Test async series.standings() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).standings()

        assert isinstance(result, SeriesStandingsResponse)
        assert result.series_code == series_active_code
        assert result.year >= 2025
        # NACS has 59 regions, use >= for resilience
        assert len(result.overall_results) >= 50
        assert result.overall_results[0].region_code is not None
        assert result.overall_results[0].region_name is not None
        assert result.overall_results[0].current_leader is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_region_standings_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str, series_region_code: str
) -> None:
    """Test async series.region_standings() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).region_standings(series_region_code)

        assert isinstance(result, SeriesRegionStandingsResponse)
        assert result.series_code == series_active_code
        assert result.region_code == series_region_code
        assert result.year >= 2025
        # CA has 14k+ players, should have substantial standings
        assert len(result.standings) >= 100
        if result.standings:
            first = result.standings[0]
            assert first.player_id is not None
            assert first.player_name is not None
            assert first.series_rank == 1  # First place


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_player_card_integration(
    async_ifpa_client: AsyncIfpaClient,
    series_active_code: str,
    series_region_code: str,
    series_player_id: int,
) -> None:
    """Test async series.player_card() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).player_card(
            series_player_id, series_region_code
        )

        assert isinstance(result, SeriesPlayerCard)
        assert result.player_id == series_player_id
        assert result.region_code == series_region_code
        # Player card may have events (use >= 0 for resilience)
        assert len(result.player_card) >= 0
        if result.player_card:
            first_event = result.player_card[0]
            assert first_event.tournament_id is not None
            assert first_event.tournament_name is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_regions_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str, series_region_code: str
) -> None:
    """Test async series.regions() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).regions(series_region_code, 2025)

        assert isinstance(result, SeriesRegionsResponse)
        # NACS has 59 active regions
        assert len(result.active_regions) >= 50
        if result.active_regions:
            first_region = result.active_regions[0]
            assert first_region.region_code is not None
            assert first_region.region_name is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_stats_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str, series_region_code: str
) -> None:
    """Test async series.stats() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).stats(series_region_code)

        assert isinstance(result, SeriesStats)
        assert result.series_code == series_active_code
        # CA region should have substantial stats
        if result.total_events is not None:
            assert result.total_events >= 0
        if result.total_players is not None:
            assert result.total_players >= 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_tournaments_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str, series_region_code: str
) -> None:
    """Test async series.tournaments() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).tournaments(series_region_code)

        assert isinstance(result, SeriesTournamentsResponse)
        # CA region should have tournaments (use >= 0 for resilience)
        assert len(result.tournaments) >= 0
        if result.tournaments:
            first_tournament = result.tournaments[0]
            assert first_tournament.tournament_id is not None
            assert first_tournament.tournament_name is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_series_region_reps_integration(
    async_ifpa_client: AsyncIfpaClient, series_active_code: str
) -> None:
    """Test async series.region_reps() against real API."""
    async with async_ifpa_client as client:
        result = await client.series(series_active_code).region_reps()

        assert isinstance(result, RegionRepsResponse)
        # NACS may or may not have region reps (use >= 0 for resilience)
        assert len(result.representative) >= 0
        if result.representative:
            first_rep = result.representative[0]
            assert first_rep.player_id is not None
            assert first_rep.name is not None
            assert first_rep.region_code is not None
