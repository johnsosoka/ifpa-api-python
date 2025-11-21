"""Integration tests for async stats resource."""

import pytest

from ifpa_api.async_client import AsyncIfpaClient
from ifpa_api.models.stats import (
    CountryPlayersResponse,
    EventsAttendedPeriodResponse,
    EventsByYearResponse,
    LargestTournamentsResponse,
    LucrativeTournamentsResponse,
    OverallStatsResponse,
    PlayersByYearResponse,
    PointsGivenPeriodResponse,
    StatePlayersResponse,
    StateTournamentsResponse,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_country_players_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async stats.country_players() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.country_players(rank_type="OPEN")

        assert isinstance(result, CountryPlayersResponse)
        assert len(result.stats) > 0
        assert result.stats[0].country_code is not None
        assert result.stats[0].player_count > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_state_players_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async stats.state_players() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.state_players(rank_type="OPEN")

        assert isinstance(result, StatePlayersResponse)
        assert len(result.stats) > 0
        assert result.stats[0].stateprov is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_state_tournaments_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async stats.state_tournaments() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.state_tournaments(rank_type="OPEN")

        assert isinstance(result, StateTournamentsResponse)
        assert len(result.stats) > 0
        assert result.stats[0].tournament_count > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_events_by_year_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async stats.events_by_year() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.events_by_year(rank_type="OPEN")

        assert isinstance(result, EventsByYearResponse)
        assert len(result.stats) > 0
        # Note: year is returned as a string, not an int
        assert int(result.stats[0].year) > 2000


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_players_by_year_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async stats.players_by_year() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.players_by_year()

        assert isinstance(result, PlayersByYearResponse)
        assert len(result.stats) > 0
        assert result.stats[0].current_year_count > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_largest_tournaments_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async stats.largest_tournaments() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.largest_tournaments(rank_type="OPEN")

        assert isinstance(result, LargestTournamentsResponse)
        assert len(result.stats) > 0
        assert result.stats[0].player_count > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_lucrative_tournaments_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async stats.lucrative_tournaments() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.lucrative_tournaments(major="Y", rank_type="OPEN")

        assert isinstance(result, LucrativeTournamentsResponse)
        assert len(result.stats) > 0
        assert result.stats[0].tournament_value is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_points_given_period_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async stats.points_given_period() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.points_given_period(
            start_date="2024-01-01", end_date="2024-12-31", limit=10
        )

        assert isinstance(result, PointsGivenPeriodResponse)
        # May have results, check response type only
        assert result.stats is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_events_attended_period_integration(
    async_ifpa_client: AsyncIfpaClient,
) -> None:
    """Test async stats.events_attended_period() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.events_attended_period(
            start_date="2024-01-01", end_date="2024-12-31", limit=10
        )

        assert isinstance(result, EventsAttendedPeriodResponse)
        # May have results, check response type only
        assert result.stats is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_stats_overall_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async stats.overall() against real API."""
    async with async_ifpa_client as client:
        result = await client.stats.overall(system_code="OPEN")

        assert isinstance(result, OverallStatsResponse)
        assert result.stats.overall_player_count > 0
        assert result.stats.tournament_count > 0
