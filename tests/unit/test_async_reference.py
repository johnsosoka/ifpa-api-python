"""Unit tests for async reference resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.models.reference import CountryListResponse, StateProvListResponse
from ifpa_api.resources.reference.async_client import AsyncReferenceClient


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_reference_client(async_http_client: _AsyncHttpClient) -> AsyncReferenceClient:
    """Create async reference client for testing."""
    return AsyncReferenceClient(async_http_client, validate_requests=False)


# AsyncReferenceClient tests


@pytest.mark.asyncio
async def test_reference_countries(
    async_reference_client: AsyncReferenceClient, respx_mock: Any
) -> None:
    """Test AsyncReferenceClient.countries() method."""
    countries_data = {
        "country": [
            {
                "country_id": "1",
                "country_name": "United States",
                "country_code": "US",
                "active_flag": "Y",
            },
            {
                "country_id": "2",
                "country_name": "Canada",
                "country_code": "CA",
                "active_flag": "Y",
            },
            {
                "country_id": "3",
                "country_name": "United Kingdom",
                "country_code": "UK",
                "active_flag": "Y",
            },
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/countries").mock(
        return_value=Response(200, json=countries_data)
    )

    result = await async_reference_client.countries()

    assert isinstance(result, CountryListResponse)
    assert len(result.country) == 3
    assert result.country[0].country_code == "US"
    assert result.country[0].country_name == "United States"
    assert result.country[1].country_code == "CA"


@pytest.mark.asyncio
async def test_reference_state_provs(
    async_reference_client: AsyncReferenceClient, respx_mock: Any
) -> None:
    """Test AsyncReferenceClient.state_provs() method."""
    state_provs_data = {
        "stateprov": [
            {
                "country_id": "1",
                "country_name": "United States",
                "country_code": "US",
                "regions": [
                    {"region_code": "WA", "region_name": "Washington"},
                    {"region_code": "OR", "region_name": "Oregon"},
                    {"region_code": "CA", "region_name": "California"},
                ],
            },
            {
                "country_id": "2",
                "country_name": "Canada",
                "country_code": "CA",
                "regions": [
                    {"region_code": "BC", "region_name": "British Columbia"},
                    {"region_code": "ON", "region_name": "Ontario"},
                ],
            },
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/stateprovs").mock(
        return_value=Response(200, json=state_provs_data)
    )

    result = await async_reference_client.state_provs()

    assert isinstance(result, StateProvListResponse)
    assert len(result.stateprov) == 2
    assert result.stateprov[0].country_code == "US"
    assert len(result.stateprov[0].regions) == 3
    assert result.stateprov[0].regions[0].region_code == "WA"
    assert result.stateprov[1].country_code == "CA"
    assert len(result.stateprov[1].regions) == 2


@pytest.mark.asyncio
async def test_reference_client_cleanup(async_http_client: _AsyncHttpClient) -> None:
    """Test that async HTTP client can be closed properly."""
    await async_http_client.close()
    # If we get here without error, cleanup worked
    assert True
