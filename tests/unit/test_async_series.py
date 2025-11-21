"""Unit tests for async series resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import SeriesPlayerNotFoundError
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
from ifpa_api.resources.series.async_client import AsyncSeriesClient
from ifpa_api.resources.series.async_context import AsyncSeriesContext


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_series_client(async_http_client: _AsyncHttpClient) -> AsyncSeriesClient:
    """Create async series client for testing."""
    return AsyncSeriesClient(async_http_client, validate_requests=False)


# AsyncSeriesClient tests


@pytest.mark.asyncio
async def test_series_client_callable_returns_context(
    async_series_client: AsyncSeriesClient,
) -> None:
    """Test that calling series client returns AsyncSeriesContext."""
    context = async_series_client("NACS")
    assert isinstance(context, AsyncSeriesContext)
    assert context._resource_id == "NACS"


@pytest.mark.asyncio
async def test_series_list(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesClient.list() method."""
    series_data = {
        "series": [
            {
                "code": "NACS",
                "title": "North American Championship Series",
                "active": "Y",
            },
            {"code": "PAPA", "title": "PAPA Circuit", "active": "Y"},
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/series/list").mock(
        return_value=Response(200, json=series_data)
    )

    result = await async_series_client.list()

    assert isinstance(result, SeriesListResponse)
    assert len(result.series) == 2
    assert result.series[0].series_code == "NACS"


@pytest.mark.asyncio
async def test_series_list_active_only(
    async_series_client: AsyncSeriesClient, respx_mock: Any
) -> None:
    """Test AsyncSeriesClient.list() with active_only filter."""
    series_data = {"series": [{"code": "NACS", "title": "NACS", "active": "Y"}]}

    respx_mock.get("https://api.ifpapinball.com/series/list?active_only=true").mock(
        return_value=Response(200, json=series_data)
    )

    result = await async_series_client.list(active_only=True)

    assert isinstance(result, SeriesListResponse)
    assert len(result.series) == 1


# AsyncSeriesContext tests


@pytest.mark.asyncio
async def test_series_standings(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.standings() method."""
    standings_data = {
        "series_code": "NACS",
        "year": 2024,
        "championship_prize_fund": 10000.0,
        "overall_results": [
            {
                "region_name": "Ohio",
                "region_code": "OH",
                "player_count": "50",
                "current_leader": {"player_name": "John Doe", "player_id": "12345"},
                "prize_fund": 1000.0,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/series/NACS/overall_standings").mock(
        return_value=Response(200, json=standings_data)
    )

    result = await async_series_client("NACS").standings()

    assert isinstance(result, SeriesStandingsResponse)
    assert result.series_code == "NACS"
    assert result.year == 2024


@pytest.mark.asyncio
async def test_series_region_standings(
    async_series_client: AsyncSeriesClient, respx_mock: Any
) -> None:
    """Test AsyncSeriesContext.region_standings() method."""
    region_data = {
        "series_code": "NACS",
        "region_name": "Ohio",
        "region_code": "OH",
        "prize_fund": "1000",
        "year": 2024,
        "standings": [
            {
                "player_id": 12345,
                "player_name": "John Doe",
                "series_rank": 1,
                "country_code": "US",
                "country_name": "United States",
                "wppr_points": 100.00,
                "event_count": 5,
                "win_count": 2,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/series/NACS/standings?region_code=OH").mock(
        return_value=Response(200, json=region_data)
    )

    result = await async_series_client("NACS").region_standings("OH")

    assert isinstance(result, SeriesRegionStandingsResponse)
    assert result.region_code == "OH"
    assert len(result.standings) == 1


@pytest.mark.asyncio
async def test_series_player_card(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.player_card() method."""
    card_data = {
        "series_code": "PAPA",
        "player_id": 12345,
        "player_name": "John Doe",
        "region_code": "OH",
        "current_position": 1,
        "total_points": 100.00,
        "player_card": [
            {
                "tournament_id": 1001,
                "tournament_name": "Test Tournament",
                "event_date": "2024-06-15",
                "points_earned": 25.00,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/series/PAPA/player_card/12345?region_code=OH").mock(
        return_value=Response(200, json=card_data)
    )

    result = await async_series_client("PAPA").player_card(12345, "OH")

    assert isinstance(result, SeriesPlayerCard)
    assert result.player_id == 12345
    assert result.current_position == 1


@pytest.mark.asyncio
async def test_series_player_card_not_found(
    async_series_client: AsyncSeriesClient, respx_mock: Any
) -> None:
    """Test AsyncSeriesContext.player_card() raises SeriesPlayerNotFoundError on 404."""
    respx_mock.get("https://api.ifpapinball.com/series/PAPA/player_card/99999?region_code=OH").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    with pytest.raises(SeriesPlayerNotFoundError) as exc_info:
        await async_series_client("PAPA").player_card(99999, "OH")

    assert exc_info.value.series_code == "PAPA"
    assert exc_info.value.player_id == 99999
    assert exc_info.value.region_code == "OH"


@pytest.mark.asyncio
async def test_series_regions(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.regions() method."""
    regions_data = {
        "active_regions": [
            {"region_code": "OH", "region_name": "Ohio"},
            {"region_code": "IL", "region_name": "Illinois"},
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/series/NACS/regions?region_code=OH&year=2024").mock(
        return_value=Response(200, json=regions_data)
    )

    result = await async_series_client("NACS").regions("OH", 2024)

    assert isinstance(result, SeriesRegionsResponse)
    assert len(result.active_regions) == 2


@pytest.mark.asyncio
async def test_series_stats(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.stats() method."""
    stats_data = {
        "series_code": "NACS",
        "total_events": 25,
        "average_event_size": 30.5,
    }

    respx_mock.get("https://api.ifpapinball.com/series/NACS/stats?region_code=OH").mock(
        return_value=Response(200, json=stats_data)
    )

    result = await async_series_client("NACS").stats("OH")

    assert isinstance(result, SeriesStats)
    assert result.total_events == 25


@pytest.mark.asyncio
async def test_series_tournaments(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.tournaments() method."""
    tournaments_data = {
        "tournaments": [
            {
                "tournament_id": 1001,
                "tournament_name": "Test Tournament",
                "event_date": "2024-06-15",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/series/NACS/tournaments?region_code=OH").mock(
        return_value=Response(200, json=tournaments_data)
    )

    result = await async_series_client("NACS").tournaments("OH")

    assert isinstance(result, SeriesTournamentsResponse)
    assert len(result.tournaments) == 1


@pytest.mark.asyncio
async def test_series_region_reps(async_series_client: AsyncSeriesClient, respx_mock: Any) -> None:
    """Test AsyncSeriesContext.region_reps() method."""
    reps_data = {
        "representative": [
            {"region_code": "OH", "region_name": "Ohio", "name": "John Doe", "player_id": 12345}
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/series/PAPA/region_reps").mock(
        return_value=Response(200, json=reps_data)
    )

    result = await async_series_client("PAPA").region_reps()

    assert isinstance(result, RegionRepsResponse)
    assert len(result.representative) == 1


@pytest.mark.asyncio
async def test_series_client_cleanup(async_http_client: _AsyncHttpClient) -> None:
    """Test that async HTTP client can be closed properly."""
    await async_http_client.close()
    # If we get here without error, cleanup worked
    assert True
