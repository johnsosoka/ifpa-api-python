"""Async rankings resource client.

Provides async access to various IFPA ranking systems including WPPR, Women's,
Youth, Pro, and custom rankings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceClient
from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingListResponse,
    CustomRankingsResponse,
    RankingsCountryListResponse,
    RankingsResponse,
)

if TYPE_CHECKING:
    pass


class AsyncRankingsClient(AsyncBaseResourceClient):
    """Async client for rankings queries.

    This client provides async access to various ranking systems maintained by IFPA,
    including overall WPPR, women's rankings, youth rankings, and more.

    Attributes:
        _http: The async HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Get top 100 players asynchronously
        async with AsyncIfpaClient() as client:
            rankings = await client.rankings.wppr(start_pos=0, count=100)
            for entry in rankings.rankings:
                print(f"{entry.rank}. {entry.player_name}: {entry.rating}")
        ```
    """

    async def wppr(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
        region: str | None = None,
    ) -> RankingsResponse:
        """Get main WPPR (World Pinball Player Rankings) asynchronously.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code
            region: Filter by region code

        Returns:
            List of ranked players in the main WPPR system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get top 100 players
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.wppr(start_pos=0, count=100)
                for entry in rankings.rankings:
                    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

            # Get rankings for a specific country
            async with AsyncIfpaClient() as client:
                us_rankings = await client.rankings.wppr(country="US")
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country
        if region is not None:
            params["region"] = region

        response = await self._http._request("GET", "/rankings/wppr", params=params)
        return RankingsResponse.model_validate(response)

    async def women(
        self,
        tournament_type: str = "OPEN",
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get women's rankings asynchronously.

        Args:
            tournament_type: Tournament type filter - "OPEN" for all tournaments or
                "WOMEN" for women-only tournaments
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the women's system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get women's rankings from all tournaments
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.women(
                    tournament_type="OPEN", start_pos=0, count=50
                )

            # Get women's rankings from women-only tournaments
            async with AsyncIfpaClient() as client:
                women_only = await client.rankings.women(tournament_type="WOMEN", count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = await self._http._request(
            "GET", f"/rankings/women/{tournament_type.lower()}", params=params
        )
        return RankingsResponse.model_validate(response)

    async def youth(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get youth rankings asynchronously.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the youth system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.youth(start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = await self._http._request("GET", "/rankings/youth", params=params)
        return RankingsResponse.model_validate(response)

    async def virtual(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get virtual tournament rankings asynchronously.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the virtual system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.virtual(start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = await self._http._request("GET", "/rankings/virtual", params=params)
        return RankingsResponse.model_validate(response)

    async def pro(
        self,
        ranking_system: str = "OPEN",
        start_pos: int | None = None,
        count: int | None = None,
    ) -> RankingsResponse:
        """Get professional circuit rankings asynchronously.

        Args:
            ranking_system: Ranking system filter - "OPEN" for open division or
                "WOMEN" for women's division
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)

        Returns:
            List of ranked players in the pro circuit

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get open division pro rankings
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.pro(ranking_system="OPEN", start_pos=0, count=50)

            # Get women's division pro rankings
            async with AsyncIfpaClient() as client:
                women_pro = await client.rankings.pro(ranking_system="WOMEN", count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = await self._http._request(
            "GET", f"/rankings/pro/{ranking_system.lower()}", params=params
        )
        return RankingsResponse.model_validate(response)

    async def by_country(
        self,
        country: str,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> CountryRankingsResponse:
        """Get country rankings filtered by country code or name asynchronously.

        Args:
            country: Country code (e.g., "US") or country name (e.g., "United States")
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of countries ranked by various metrics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Using country code
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.by_country(country="US", count=25)
                for entry in rankings.country_rankings:
                    print(f"{entry.rank}. {entry.country_name}: {entry.total_players} players")

            # Using country name
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.by_country(country="United States", count=10)
            ```
        """
        params = {"country": country}
        if start_pos is not None:
            params["start_pos"] = str(start_pos)
        if count is not None:
            params["count"] = str(count)

        response = await self._http._request("GET", "/rankings/country", params=params)
        return CountryRankingsResponse.model_validate(response)

    async def custom(
        self,
        ranking_id: str | int,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> CustomRankingsResponse:
        """Get custom ranking system results asynchronously.

        Args:
            ranking_id: Custom ranking system identifier
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of players in the custom ranking system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                rankings = await client.rankings.custom("regional-2024", start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = await self._http._request("GET", f"/rankings/custom/{ranking_id}", params=params)
        return CustomRankingsResponse.model_validate(response)

    async def country_list(self) -> RankingsCountryListResponse:
        """Get list of all countries with player counts asynchronously.

        Returns a list of countries that have players in the IFPA rankings system,
        including the number of ranked players per country. This is useful for
        discovering valid country codes before calling by_country().

        Returns:
            RankingsCountryListResponse with list of countries and their player counts.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get all countries with player counts
            async with AsyncIfpaClient() as client:
                countries = await client.rankings.country_list()

                # Find US player count
                us = next(c for c in countries.country if c.country_code == "US")
                print(f"US has {us.player_count} ranked players")

                # Get top 5 countries by player count
                top5 = sorted(countries.country, key=lambda c: c.player_count, reverse=True)[:5]
                for country in top5:
                    print(f"{country.country_name}: {country.player_count} players")
            ```
        """
        response = await self._http._request("GET", "/rankings/country_list")
        return RankingsCountryListResponse.model_validate(response)

    async def custom_list(self) -> CustomRankingListResponse:
        """Get list of all custom ranking systems asynchronously.

        Returns a list of all available custom ranking systems with their IDs, titles,
        and descriptions. This is useful for discovering valid ranking IDs before
        calling custom().

        Returns:
            CustomRankingListResponse with list of custom ranking systems.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get all custom rankings
            async with AsyncIfpaClient() as client:
                custom_rankings = await client.rankings.custom_list()

                # Find a specific ranking by title
                retro = next(
                    c for c in custom_rankings.custom_view
                    if "retro" in c.title.lower()
                )
                print(f"Found: {retro.title} (ID: {retro.view_id})")

                # Get rankings for that system
                rankings = await client.rankings.custom(retro.view_id)
            ```
        """
        response = await self._http._request("GET", "/rankings/custom/list")
        return CustomRankingListResponse.model_validate(response)
