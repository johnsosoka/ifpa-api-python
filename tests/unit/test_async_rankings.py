"""Unit tests for async rankings resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingListResponse,
    CustomRankingsResponse,
    RankingsCountryListResponse,
    RankingsResponse,
)
from ifpa_api.resources.rankings.async_client import AsyncRankingsClient


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_rankings_client(async_http_client: _AsyncHttpClient) -> AsyncRankingsClient:
    """Create async rankings client for testing."""
    return AsyncRankingsClient(async_http_client, validate_requests=False)


# AsyncRankingsClient tests


@pytest.mark.asyncio
async def test_rankings_wppr(async_rankings_client: AsyncRankingsClient, respx_mock: Any) -> None:
    """Test AsyncRankingsClient.wppr() method."""
    rankings_data = {
        "rankings": [
            {
                "player_id": 1,
                "first_name": "John",
                "last_name": "Doe",
                "current_rank": 1,
                "rating_value": "100.00",
                "country_name": "United States",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/wppr?count=10").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.wppr(count=10)

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].player_id == 1
    assert result.rankings[0].rank == 1


@pytest.mark.asyncio
async def test_rankings_wppr_with_all_params(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.wppr() with all parameters."""
    rankings_data: dict[str, Any] = {"rankings": []}

    respx_mock.get(
        "https://api.ifpapinball.com/rankings/wppr?start_pos=0&count=25&country=US&region=WA"
    ).mock(return_value=Response(200, json=rankings_data))

    result = await async_rankings_client.wppr(start_pos=0, count=25, country="US", region="WA")

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 0


@pytest.mark.asyncio
async def test_rankings_women_open(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.women() with OPEN tournament type."""
    rankings_data = {
        "rankings": [
            {
                "player_id": 2,
                "first_name": "Jane",
                "last_name": "Smith",
                "current_rank": 1,
                "rating_value": "85.50",
                "country_name": "Canada",
                "country_code": "CA",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/women/open?count=50").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.women(tournament_type="OPEN", count=50)

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].player_id == 2


@pytest.mark.asyncio
async def test_rankings_women_women_only(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.women() with WOMEN tournament type."""
    rankings_data: dict[str, Any] = {"rankings": []}

    respx_mock.get("https://api.ifpapinball.com/rankings/women/women").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.women(tournament_type="WOMEN")

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 0


@pytest.mark.asyncio
async def test_rankings_youth(async_rankings_client: AsyncRankingsClient, respx_mock: Any) -> None:
    """Test AsyncRankingsClient.youth() method."""
    rankings_data = {
        "rankings": [
            {
                "player_id": 3,
                "first_name": "Young",
                "last_name": "Player",
                "current_rank": 1,
                "rating_value": "45.00",
                "country_name": "United States",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/youth?start_pos=0&count=50").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.youth(start_pos=0, count=50)

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].first_name == "Young"


@pytest.mark.asyncio
async def test_rankings_virtual(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.virtual() method."""
    rankings_data = {
        "rankings": [
            {
                "player_id": 4,
                "first_name": "Virtual",
                "last_name": "Wizard",
                "current_rank": 1,
                "rating_value": "30.00",
                "country_name": "United Kingdom",
                "country_code": "UK",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/virtual?country=UK").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.virtual(country="UK")

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].country_code == "UK"


@pytest.mark.asyncio
async def test_rankings_pro_open(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.pro() with OPEN ranking system."""
    rankings_data = {
        "rankings": [
            {
                "player_id": 5,
                "first_name": "Pro",
                "last_name": "Player",
                "current_rank": 1,
                "rating_value": "95.00",
                "country_name": "United States",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/pro/open?start_pos=0&count=50").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.pro(ranking_system="OPEN", start_pos=0, count=50)

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].player_id == 5


@pytest.mark.asyncio
async def test_rankings_pro_women(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.pro() with WOMEN ranking system."""
    rankings_data: dict[str, Any] = {"rankings": []}

    respx_mock.get("https://api.ifpapinball.com/rankings/pro/women").mock(
        return_value=Response(200, json=rankings_data)
    )

    result = await async_rankings_client.pro(ranking_system="WOMEN")

    assert isinstance(result, RankingsResponse)
    assert len(result.rankings) == 0


@pytest.mark.asyncio
async def test_rankings_by_country(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.by_country() method."""
    country_data = {
        "rankings": [
            {
                "player_id": 100,
                "current_rank": 1,
                "first_name": "John",
                "last_name": "Doe",
                "country_name": "United States",
                "country_code": "US",
                "rating_value": "500.00",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/country?country=US&count=25").mock(
        return_value=Response(200, json=country_data)
    )

    result = await async_rankings_client.by_country(country="US", count=25)

    assert isinstance(result, CountryRankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].country_code == "US"


@pytest.mark.asyncio
async def test_rankings_custom(async_rankings_client: AsyncRankingsClient, respx_mock: Any) -> None:
    """Test AsyncRankingsClient.custom() method."""
    custom_data = {
        "custom_view": [
            {"rank": 1, "player_id": 6, "player_name": "Regional Champ", "value": 80.00}
        ],
        "title": "Regional Rankings 2024",
        "description": "Custom regional ranking system",
    }

    respx_mock.get(
        "https://api.ifpapinball.com/rankings/custom/regional-2024?start_pos=0&count=50"
    ).mock(return_value=Response(200, json=custom_data))

    result = await async_rankings_client.custom("regional-2024", start_pos=0, count=50)

    assert isinstance(result, CustomRankingsResponse)
    assert len(result.rankings) == 1
    assert result.rankings[0].player_id == 6


@pytest.mark.asyncio
async def test_rankings_country_list(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.country_list() method."""
    country_list_data = {
        "country": [
            {"country_code": "US", "country_name": "United States", "player_count": 5000},
            {"country_code": "CA", "country_name": "Canada", "player_count": 1500},
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/country_list").mock(
        return_value=Response(200, json=country_list_data)
    )

    result = await async_rankings_client.country_list()

    assert isinstance(result, RankingsCountryListResponse)
    assert len(result.country) == 2
    assert result.country[0].country_code == "US"
    assert result.country[0].player_count == 5000


@pytest.mark.asyncio
async def test_rankings_custom_list(
    async_rankings_client: AsyncRankingsClient, respx_mock: Any
) -> None:
    """Test AsyncRankingsClient.custom_list() method."""
    custom_list_data = {
        "custom_view": [
            {
                "view_id": 1,
                "title": "Regional Rankings 2024",
                "description": "Regional",
            },
            {"view_id": 2, "title": "Retro Rankings 2024", "description": "Retro games"},
        ],
        "total_count": 2,
    }

    respx_mock.get("https://api.ifpapinball.com/rankings/custom/list").mock(
        return_value=Response(200, json=custom_list_data)
    )

    result = await async_rankings_client.custom_list()

    assert isinstance(result, CustomRankingListResponse)
    assert len(result.custom_view) == 2
    assert result.custom_view[0].view_id == 1
    assert result.custom_view[1].title == "Retro Rankings 2024"


@pytest.mark.asyncio
async def test_rankings_client_cleanup(async_http_client: _AsyncHttpClient) -> None:
    """Test that async HTTP client can be closed properly."""
    await async_http_client.close()
    # If we get here without error, cleanup worked
    assert True
