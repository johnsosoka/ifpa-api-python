"""Async series resource context for individual series operations.

Provides async methods for accessing information about a specific tournament series.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceContext
from ifpa_api.core.exceptions import IfpaApiError, SeriesPlayerNotFoundError
from ifpa_api.models.series import (
    RegionRepsResponse,
    SeriesPlayerCard,
    SeriesRegionsResponse,
    SeriesRegionStandingsResponse,
    SeriesStandingsResponse,
    SeriesStats,
    SeriesTournamentsResponse,
)

if TYPE_CHECKING:
    pass


class AsyncSeriesContext(AsyncBaseResourceContext[str]):
    """Internal async context for series-specific operations.

    This class provides async methods for accessing information about a specific
    series identified by its series code. It is returned by calling
    AsyncSeriesClient with a series code.

    Attributes:
        _http: The async HTTP client instance
        _resource_id: The series code identifier
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        async with AsyncIfpaClient() as client:
            # Get overall standings
            standings = await client.series("NACS").standings()

            # Get region standings
            region = await client.series("NACS").region_standings("OH")

            # Get player card
            card = await client.series("PAPA").player_card(12345, "OH")
        ```
    """

    async def standings(
        self,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> SeriesStandingsResponse:
        """Get overall standings for this series across all regions asynchronously.

        Returns an overview of standings for all regions in the series, including
        the current leader and prize fund for each region.

        Args:
            start_pos: Starting position for pagination (currently unused by API)
            count: Number of results to return (currently unused by API)

        Returns:
            Overall standings with region overviews

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                standings = await client.series("NACS").standings()
                print(f"Series: {standings.series_code} ({standings.year})")
                print(f"Total Prize Fund: ${standings.championship_prize_fund}")
                for region in standings.overall_results:
                    print(f"{region.region_name}: {region.player_count} players")
                    print(f"  Leader: {region.current_leader['player_name']}")
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = await self._http._request(
            "GET", f"/series/{self._resource_id}/overall_standings", params=params
        )
        return SeriesStandingsResponse.model_validate(response)

    async def region_standings(
        self,
        region_code: str,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> SeriesRegionStandingsResponse:
        """Get detailed player standings for a specific region in this series asynchronously.

        Returns the full standings list with individual player rankings for
        a specific region.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            Detailed region standings with player rankings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                standings = await client.series("NACS").region_standings("OH")
                print(f"Region: {standings.region_name}")
                print(f"Prize Fund: ${standings.prize_fund}")
                for player in standings.standings[:10]:
                    print(f"{player.series_rank}. {player.player_name}: {player.wppr_points} pts")
            ```
        """
        params: dict[str, str | int] = {"region_code": region_code}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = await self._http._request(
            "GET", f"/series/{self._resource_id}/standings", params=params
        )
        return SeriesRegionStandingsResponse.model_validate(response)

    async def player_card(
        self,
        player_id: int | str,
        region_code: str,
        year: int | None = None,
    ) -> SeriesPlayerCard:
        """Get a player's card for this series asynchronously.

        Args:
            player_id: The player's unique identifier
            region_code: Region code (e.g., "OH", "IL")
            year: Year to fetch card for (defaults to current year if not specified)

        Returns:
            Player's series card with event results and statistics

        Raises:
            SeriesPlayerNotFoundError: If the player has no results in the series/region
            IfpaApiError: If the API request fails for other reasons

        Example:
            ```python
            from ifpa_api.exceptions import SeriesPlayerNotFoundError

            # Get current year card for player in Ohio region
            async with AsyncIfpaClient() as client:
                try:
                    card = await client.series("PAPA").player_card(12345, "OH")
                    print(f"Position: {card.current_position}")
                    print(f"Points: {card.total_points}")
                except SeriesPlayerNotFoundError as e:
                    print(f"Player {e.player_id} has no results in {e.series_code}")

            # Get card for specific year
            async with AsyncIfpaClient() as client:
                card_2023 = await client.series("PAPA").player_card(12345, "OH", year=2023)
                for event in card_2023.events:
                    print(f"{event.tournament_name}: {event.points_earned} pts")
            ```
        """
        params: dict[str, str | int] = {"region_code": region_code}
        if year is not None:
            params["year"] = int(year)

        try:
            response = await self._http._request(
                "GET", f"/series/{self._resource_id}/player_card/{player_id}", params=params
            )
            return SeriesPlayerCard.model_validate(response)
        except IfpaApiError as e:
            # Convert 404 to semantic exception
            if e.status_code == 404:
                raise SeriesPlayerNotFoundError(self._resource_id, player_id, region_code) from e
            # Re-raise other API errors
            raise

    async def regions(self, region_code: str, year: int) -> SeriesRegionsResponse:
        """Get active regions in this series for a specific year asynchronously.

        Note: The region_code parameter is required by the API but the endpoint
        returns all active regions for the specified year regardless of the
        region_code value provided.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA") - required by API
                but not used for filtering
            year: Year to fetch regions for

        Returns:
            List of all active regions for the specified year

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                regions = await client.series("NACS").regions("OH", 2025)
                for region in regions.active_regions:
                    print(f"{region.region_name} ({region.region_code})")
            ```
        """
        params = {"region_code": region_code, "year": year}
        response = await self._http._request(
            "GET", f"/series/{self._resource_id}/regions", params=params
        )
        return SeriesRegionsResponse.model_validate(response)

    async def stats(self, region_code: str) -> SeriesStats:
        """Get statistics for a specific region in this series asynchronously.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")

        Returns:
            Series statistics including totals and averages for the region

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                stats = await client.series("NACS").stats("OH")
                print(f"Total Events: {stats.total_events}")
                print(f"Average Event Size: {stats.average_event_size}")
            ```
        """
        params = {"region_code": region_code}
        response = await self._http._request(
            "GET", f"/series/{self._resource_id}/stats", params=params
        )
        return SeriesStats.model_validate(response)

    async def tournaments(self, region_code: str) -> SeriesTournamentsResponse:
        """Get tournaments for a specific region in this series asynchronously.

        Args:
            region_code: Region code (e.g., "OH", "IL", "CA")

        Returns:
            List of tournaments in the specified region

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                tournaments = await client.series("NACS").tournaments("OH")
                for tournament in tournaments.tournaments:
                    print(f"{tournament.tournament_name} on {tournament.event_date}")
            ```
        """
        params = {"region_code": region_code}
        response = await self._http._request(
            "GET", f"/series/{self._resource_id}/tournaments", params=params
        )
        return SeriesTournamentsResponse.model_validate(response)

    async def region_reps(self) -> RegionRepsResponse:
        """Get region representatives for this series asynchronously.

        Returns:
            List of region representatives

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                reps = await client.series("PAPA").region_reps()
                for rep in reps.representative:
                    print(f"{rep.region_name}: {rep.name} (Player #{rep.player_id})")
            ```
        """
        response = await self._http._request("GET", f"/series/{self._resource_id}/region_reps")
        return RegionRepsResponse.model_validate(response)
