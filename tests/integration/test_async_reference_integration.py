"""Integration tests for async reference resource."""

import pytest

from ifpa_api.async_client import AsyncIfpaClient
from ifpa_api.models.reference import CountryListResponse, StateProvListResponse


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_reference_countries_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async reference.countries() against real API."""
    async with async_ifpa_client as client:
        result = await client.reference.countries()

        assert isinstance(result, CountryListResponse)
        assert len(result.country) > 0
        assert result.country[0].country_code is not None
        assert result.country[0].country_name is not None

        # Verify we can find US
        us = next((c for c in result.country if c.country_code == "US"), None)
        assert us is not None
        assert us.country_name == "United States"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_async_reference_state_provs_integration(async_ifpa_client: AsyncIfpaClient) -> None:
    """Test async reference.state_provs() against real API."""
    async with async_ifpa_client as client:
        result = await client.reference.state_provs()

        assert isinstance(result, StateProvListResponse)
        assert len(result.stateprov) > 0

        # Verify we can find US states
        us_regions = next((c for c in result.stateprov if c.country_code == "US"), None)
        assert us_regions is not None
        assert len(us_regions.regions) > 0

        # Verify WA exists
        wa = next((r for r in us_regions.regions if r.region_code == "WA"), None)
        assert wa is not None
        assert wa.region_name == "Washington"
