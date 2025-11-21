"""Unit tests for async stats resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
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
from ifpa_api.resources.stats.async_client import AsyncStatsClient


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_stats_client(async_http_client: _AsyncHttpClient) -> AsyncStatsClient:
    """Create async stats client for testing."""
    return AsyncStatsClient(async_http_client, validate_requests=False)


# AsyncStatsClient tests


@pytest.mark.asyncio
async def test_stats_country_players(async_stats_client: AsyncStatsClient, respx_mock: Any) -> None:
    """Test AsyncStatsClient.country_players() method."""
    stats_data = {
        "type": "country_players",
        "rank_type": "OPEN",
        "stats": [
            {
                "country_name": "United States",
                "country_code": "US",
                "player_count": "5000",
                "stats_rank": 1,
            },
            {
                "country_name": "Canada",
                "country_code": "CA",
                "player_count": "1500",
                "stats_rank": 2,
            },
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/country_players").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.country_players(rank_type="OPEN")

    assert isinstance(result, CountryPlayersResponse)
    assert len(result.stats) == 2
    assert result.stats[0].country_code == "US"
    assert result.stats[0].player_count == 5000


@pytest.mark.asyncio
async def test_stats_state_players(async_stats_client: AsyncStatsClient, respx_mock: Any) -> None:
    """Test AsyncStatsClient.state_players() method."""
    stats_data = {
        "type": "state_players",
        "rank_type": "OPEN",
        "stats": [
            {"stateprov": "WA", "player_count": "500", "stats_rank": 1},
            {"stateprov": "OR", "player_count": "400", "stats_rank": 2},
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/state_players").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.state_players(rank_type="OPEN")

    assert isinstance(result, StatePlayersResponse)
    assert len(result.stats) == 2
    assert result.stats[0].stateprov == "WA"
    assert result.stats[0].player_count == 500


@pytest.mark.asyncio
async def test_stats_state_tournaments(
    async_stats_client: AsyncStatsClient, respx_mock: Any
) -> None:
    """Test AsyncStatsClient.state_tournaments() method."""
    stats_data = {
        "type": "state_tournaments",
        "rank_type": "OPEN",
        "stats": [
            {
                "stateprov": "WA",
                "tournament_count": "100",
                "total_points_all": "5000.50",
                "total_points_tournament_value": "3000.25",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/state_tournaments").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.state_tournaments(rank_type="OPEN")

    assert isinstance(result, StateTournamentsResponse)
    assert len(result.stats) == 1
    assert result.stats[0].stateprov == "WA"
    assert result.stats[0].tournament_count == 100


@pytest.mark.asyncio
async def test_stats_events_by_year(async_stats_client: AsyncStatsClient, respx_mock: Any) -> None:
    """Test AsyncStatsClient.events_by_year() method."""
    stats_data = {
        "type": "events_by_year",
        "rank_type": "OPEN",
        "stats": [
            {
                "year": "2024",
                "tournament_count": "1500",
                "country_count": "50",
                "player_count": "10000",
                "stats_rank": 1,
            },
            {
                "year": "2023",
                "tournament_count": "1400",
                "country_count": "48",
                "player_count": "9500",
                "stats_rank": 2,
            },
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/events_by_year").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.events_by_year(rank_type="OPEN")

    assert isinstance(result, EventsByYearResponse)
    assert len(result.stats) == 2
    assert result.stats[0].year == "2024"
    assert result.stats[0].tournament_count == 1500


@pytest.mark.asyncio
async def test_stats_players_by_year(async_stats_client: AsyncStatsClient, respx_mock: Any) -> None:
    """Test AsyncStatsClient.players_by_year() method."""
    stats_data = {
        "type": "players_by_year",
        "rank_type": "OPEN",
        "stats": [
            {
                "year": "2024",
                "current_year_count": "10000",
                "previous_year_count": "8000",
                "previous_2_year_count": "6000",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/players_by_year").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.players_by_year()

    assert isinstance(result, PlayersByYearResponse)
    assert len(result.stats) == 1
    assert result.stats[0].year == "2024"
    assert result.stats[0].current_year_count == 10000


@pytest.mark.asyncio
async def test_stats_largest_tournaments(
    async_stats_client: AsyncStatsClient, respx_mock: Any
) -> None:
    """Test AsyncStatsClient.largest_tournaments() method."""
    stats_data = {
        "type": "largest_tournaments",
        "rank_type": "OPEN",
        "stats": [
            {
                "tournament_id": 12345,
                "tournament_name": "Big Tournament",
                "event_name": "Main Event",
                "tournament_date": "2024-06-15",
                "player_count": "500",
                "country_name": "United States",
                "country_code": "US",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/largest_tournaments").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.largest_tournaments(rank_type="OPEN")

    assert isinstance(result, LargestTournamentsResponse)
    assert len(result.stats) == 1
    assert result.stats[0].tournament_name == "Big Tournament"
    assert result.stats[0].player_count == 500


@pytest.mark.asyncio
async def test_stats_lucrative_tournaments(
    async_stats_client: AsyncStatsClient, respx_mock: Any
) -> None:
    """Test AsyncStatsClient.lucrative_tournaments() method."""
    stats_data = {
        "type": "lucrative_tournaments",
        "rank_type": "OPEN",
        "stats": [
            {
                "tournament_id": 12345,
                "tournament_name": "High Value Tournament",
                "event_name": "Main Event",
                "tournament_date": "2024-06-15",
                "tournament_value": 50.00,
                "country_name": "United States",
                "country_code": "US",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/stats/lucrative_tournaments").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.lucrative_tournaments(major="Y", rank_type="OPEN")

    assert isinstance(result, LucrativeTournamentsResponse)
    assert len(result.stats) == 1
    assert result.stats[0].tournament_name == "High Value Tournament"


@pytest.mark.asyncio
async def test_stats_points_given_period(
    async_stats_client: AsyncStatsClient, respx_mock: Any
) -> None:
    """Test AsyncStatsClient.points_given_period() method."""
    stats_data = {
        "type": "points_given_period",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "return_count": 1,
        "rank_type": "OPEN",
        "stats": [
            {
                "player_id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "wppr_points": "100.50",
                "country_name": "United States",
                "country_code": "US",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get(
        "https://api.ifpapinball.com/stats/points_given_period?start_date=2024-01-01&end_date=2024-12-31&limit=25"
    ).mock(return_value=Response(200, json=stats_data))

    result = await async_stats_client.points_given_period(
        start_date="2024-01-01", end_date="2024-12-31", limit=25
    )

    assert isinstance(result, PointsGivenPeriodResponse)
    assert len(result.stats) == 1
    assert result.stats[0].player_id == 12345


@pytest.mark.asyncio
async def test_stats_events_attended_period(
    async_stats_client: AsyncStatsClient, respx_mock: Any
) -> None:
    """Test AsyncStatsClient.events_attended_period() method."""
    stats_data = {
        "type": "events_attended_period",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "return_count": 1,
        "stats": [
            {
                "player_id": "12345",
                "first_name": "John",
                "last_name": "Doe",
                "tournament_count": "50",
                "country_name": "United States",
                "country_code": "US",
                "stats_rank": 1,
            }
        ],
    }

    respx_mock.get(
        "https://api.ifpapinball.com/stats/events_attended_period?start_date=2024-01-01&limit=10"
    ).mock(return_value=Response(200, json=stats_data))

    result = await async_stats_client.events_attended_period(start_date="2024-01-01", limit=10)

    assert isinstance(result, EventsAttendedPeriodResponse)
    assert len(result.stats) == 1
    assert result.stats[0].tournament_count == 50


@pytest.mark.asyncio
async def test_stats_overall(async_stats_client: AsyncStatsClient, respx_mock: Any) -> None:
    """Test AsyncStatsClient.overall() method."""
    stats_data = {
        "type": "overall",
        "system_code": "OPEN",
        "stats": {
            "overall_player_count": 10000,
            "active_player_count": 5000,
            "tournament_count": 2000,
            "tournament_count_last_month": 100,
            "tournament_count_this_year": 150,
            "tournament_player_count": 50000,
            "tournament_player_count_average": 25.5,
            "age": {
                "age_under_18": 5.0,
                "age_18_to_29": 25.0,
                "age_30_to_39": 30.0,
                "age_40_to_49": 25.0,
                "age_50_to_99": 15.0,
            },
        },
    }

    respx_mock.get("https://api.ifpapinball.com/stats/overall").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_stats_client.overall(system_code="OPEN")

    assert isinstance(result, OverallStatsResponse)
    assert result.stats.overall_player_count == 10000
    assert result.stats.active_player_count == 5000
    assert result.stats.age.age_under_18 == 5.0


@pytest.mark.asyncio
async def test_stats_client_cleanup(async_http_client: _AsyncHttpClient) -> None:
    """Test that async HTTP client can be closed properly."""
    await async_http_client.close()
    # If we get here without error, cleanup worked
    assert True
