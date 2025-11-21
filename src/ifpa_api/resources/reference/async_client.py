"""Async reference data resource client."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.models.reference import CountryListResponse, StateProvListResponse

if TYPE_CHECKING:
    pass


class AsyncReferenceClient(AsyncBaseResourceClient):
    """Async client for IFPA reference/lookup data endpoints.

    Provides async access to reference data such as countries and states/provinces
    that are used for filtering and validation across other endpoints.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        from ifpa_api import AsyncIfpaClient

        # Get all countries asynchronously
        async with AsyncIfpaClient() as client:
            countries = await client.reference.countries()
            for country in countries.country:
                print(f"{country.country_name} ({country.country_code})")

        # Get states/provinces
        async with AsyncIfpaClient() as client:
            state_provs = await client.reference.state_provs()
            for country_region in state_provs.stateprov:
                print(f"{country_region.country_name}:")
                for region in country_region.regions:
                    print(f"  - {region.region_name} ({region.region_code})")
        ```
    """

    async def countries(self) -> CountryListResponse:
        """Get list of all countries in the IFPA system asynchronously.

        Returns a list of countries with their IDs, names, codes, and active status.
        This is useful for validating country filters in other endpoints and building
        UI dropdowns.

        Returns:
            CountryListResponse with list of all countries (typically 62).

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                countries = await client.reference.countries()

                # Find US country code
                us = next(c for c in countries.country if c.country_name == "United States")
                print(us.country_code)  # "US"

                # Get all active countries
                active = [c for c in countries.country if c.active_flag == "Y"]
                print(f"Active countries: {len(active)}")
            ```
        """
        response = await self._http._request("GET", "/countries")
        return CountryListResponse.model_validate(response)

    async def state_provs(self) -> StateProvListResponse:
        """Get list of states/provinces organized by country asynchronously.

        Returns states and provinces for countries that have regional subdivisions
        in the IFPA system (Australia, Canada, United States). This is useful for
        building cascading location dropdowns and validating stateprov filters.

        Returns:
            StateProvListResponse with countries and their regions (typically 67 total regions
            across 3 countries).

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                state_provs = await client.reference.state_provs()

                # Find US states
                us_regions = next(c for c in state_provs.stateprov if c.country_code == "US")
                print(f"US has {len(us_regions.regions)} states")

                # Get all region codes for a country
                us_codes = [r.region_code for r in us_regions.regions]
                print(us_codes)  # ["AL", "AK", "AZ", ...]
            ```
        """
        response = await self._http._request("GET", "/stateprovs")
        return StateProvListResponse.model_validate(response)
