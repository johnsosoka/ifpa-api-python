"""Main async IFPA SDK client facade.

This module provides the primary async entry point for interacting with the IFPA API
through a clean, typed, async interface using httpx and asyncio.
"""

from typing import Any

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.resources.director.async_client import AsyncDirectorClient
from ifpa_api.resources.player.async_client import AsyncPlayerClient
from ifpa_api.resources.rankings.async_client import AsyncRankingsClient
from ifpa_api.resources.reference.async_client import AsyncReferenceClient
from ifpa_api.resources.series.async_client import AsyncSeriesClient
from ifpa_api.resources.stats.async_client import AsyncStatsClient
from ifpa_api.resources.tournament.async_client import AsyncTournamentClient


class AsyncIfpaClient:
    """Main async client for interacting with the IFPA API.

    This async client provides access to all IFPA resources including players,
    tournaments, rankings, series, and statistics. It manages authentication,
    async HTTP sessions, and provides a clean async interface for SDK users.

    Attributes:
        _config: Configuration settings including API key and base URL
        _http: Internal async HTTP client for making requests

    Example:
        ```python
        from ifpa_api import AsyncIfpaClient, TimePeriod
        import asyncio

        async def main():
            # Initialize with API key from environment variable
            async with AsyncIfpaClient() as client:
                # Access resources with await
                player = await client.player.get(12345)
                rankings = await client.rankings.wppr(start_pos=0, count=100)

                # Callable pattern (deprecated, still works)
                director = await client.director(1000).details()
                tourneys = await client.director(1000).tournaments(TimePeriod.PAST)

                # Query builders
                results = await client.player.search("Smith").country("US").get()

            # Automatically closed when exiting context

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 10.0,
        validate_requests: bool = True,
    ) -> None:
        """Initialize the async IFPA API client.

        Args:
            api_key: Optional API key. If not provided, will attempt to read from
                IFPA_API_KEY environment variable.
            base_url: Optional base URL override. Defaults to https://api.ifpapinball.com
            timeout: Request timeout in seconds. Defaults to 10.0.
            validate_requests: Whether to validate request parameters using Pydantic.
                Defaults to True.

        Raises:
            MissingApiKeyError: If no API key is provided and IFPA_API_KEY env var
                is not set.

        Important:
            Always use the client as an async context manager (``async with``) or
            explicitly call ``await client.close()`` when done. Failing to close
            the client will leak HTTP connections and may cause ResourceWarnings.

        Example:
            ```python
            # RECOMMENDED: Use async context manager
            async with AsyncIfpaClient() as client:
                player = await client.player.get(12345)
            # Automatically closed

            # ALTERNATIVE: Manual cleanup
            client = AsyncIfpaClient()
            try:
                player = await client.player.get(12345)
            finally:
                await client.close()  # Must close manually
            ```
        """
        self._config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            validate_requests=validate_requests,
        )
        self._http = _AsyncHttpClient(self._config)

        # Initialize resource clients (lazy-loaded via properties)
        self._director_client: AsyncDirectorClient | None = None
        self._player_client: AsyncPlayerClient | None = None
        self._rankings_client: AsyncRankingsClient | None = None
        self._reference_client: AsyncReferenceClient | None = None
        self._tournament_client: AsyncTournamentClient | None = None
        self._series_client: AsyncSeriesClient | None = None
        self._stats_client: AsyncStatsClient | None = None

    @property
    def director(self) -> AsyncDirectorClient:
        """Access the async director resource client.

        Returns:
            AsyncDirectorClient instance for async director operations
            (both collection and resource level)

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Collection-level: Query for directors
                results = await client.director.search("Josh").get()

                # Collection-level: Query with filters
                results = await client.director.search("Josh").country("US").state("IL").get()

                # Collection-level: Get country directors
                country_dirs = await client.director.country_directors()

                # Resource-level: Get director details
                director = await client.director.get(1000)

                # Resource-level: Get director's tournaments (deprecated pattern)
                past = await client.director(1000).tournaments(TimePeriod.PAST)
            ```
        """
        if self._director_client is None:
            self._director_client = AsyncDirectorClient(self._http, self._config.validate_requests)
        return self._director_client

    @property
    def player(self) -> AsyncPlayerClient:
        """Access the async player resource client.

        Returns:
            AsyncPlayerClient instance for async player operations
            (both collection and resource level)

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Collection-level: Search for players
                results = await client.player.search("John").get()

                # Collection-level: Search with filters
                results = await client.player.search("John").state("WA").country("US").get()

                # Resource-level: Get player details
                player = await client.player.get(12345)

                # Resource-level: Check if player exists
                exists = await client.player.exists(12345)

                # Resource-level: Get PVP comparison (deprecated pattern)
                pvp = await client.player(12345).pvp(67890)
            ```
        """
        if self._player_client is None:
            self._player_client = AsyncPlayerClient(self._http, self._config.validate_requests)
        return self._player_client

    @property
    def rankings(self) -> AsyncRankingsClient:
        """Access the async rankings resource client.

        Returns:
            AsyncRankingsClient instance for accessing various ranking systems

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Get WPPR rankings
                wppr = await client.rankings.wppr(start_pos=0, count=100)

                # Get women's rankings
                women = await client.rankings.women(country="US")

                # Get country rankings
                countries = await client.rankings.by_country()
            ```
        """
        if self._rankings_client is None:
            self._rankings_client = AsyncRankingsClient(self._http, self._config.validate_requests)
        return self._rankings_client

    @property
    def reference(self) -> AsyncReferenceClient:
        """Access async reference data endpoints.

        Provides access to lookup/reference data such as countries and states/provinces.

        Returns:
            AsyncReferenceClient for accessing reference data.

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Get all countries
                countries = await client.reference.countries()

                # Get states/provinces
                state_provs = await client.reference.state_provs()
            ```
        """
        if self._reference_client is None:
            self._reference_client = AsyncReferenceClient(
                self._http, self._config.validate_requests
            )
        return self._reference_client

    @property
    def tournament(self) -> AsyncTournamentClient:
        """Access the async tournament resource client.

        Returns:
            AsyncTournamentClient instance for async tournament operations
            (both collection and resource level)

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Collection-level: Search for tournaments
                results = await client.tournament.search("Pinball").get()

                # Collection-level: Search with filters
                results = (
                    await client.tournament.search("Pinball")
                    .city("Portland")
                    .state("OR")
                    .get()
                )

                # Collection-level: List tournament formats
                formats = await client.tournament.list_formats()

                # Resource-level: Get tournament details
                tournament = await client.tournament.get(12345)

                # Resource-level: Get tournament results (deprecated pattern)
                results = await client.tournament(12345).results()
            ```
        """
        if self._tournament_client is None:
            self._tournament_client = AsyncTournamentClient(
                self._http, self._config.validate_requests
            )
        return self._tournament_client

    @property
    def series(self) -> AsyncSeriesClient:
        """Access the async series resource client.

        Returns:
            AsyncSeriesClient instance for async series operations
            (both collection and resource level)

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Collection-level: List all series
                all_series = await client.series.list()
                active = await client.series.list(active_only=True)

                # Resource-level: Get series standings
                standings = await client.series("NACS").standings()

                # Resource-level: Get player's series card
                card = await client.series("PAPA").player_card(12345, "OH")

                # Resource-level: Get region standings
                region = await client.series("NACS").region_standings("OH")
            ```
        """
        if self._series_client is None:
            self._series_client = AsyncSeriesClient(self._http, self._config.validate_requests)
        return self._series_client

    @property
    def stats(self) -> AsyncStatsClient:
        """Access the async stats resource client.

        Returns:
            AsyncStatsClient instance for accessing statistical data and metrics

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                # Get player counts by country
                country_stats = await client.stats.country_players(rank_type="OPEN")

                # Get state/province statistics
                state_stats = await client.stats.state_players()

                # Get overall IFPA statistics
                overall = await client.stats.overall()
                print(f"Total players: {overall.stats.overall_player_count}")

                # Get points given in a period
                points = await client.stats.points_given_period(
                    start_date="2024-01-01",
                    end_date="2024-12-31",
                    limit=25
                )
            ```
        """
        if self._stats_client is None:
            self._stats_client = AsyncStatsClient(self._http, self._config.validate_requests)
        return self._stats_client

    async def close(self) -> None:
        """Close the async HTTP client session.

        This should be called when the client is no longer needed to properly
        clean up resources. Alternatively, use the client as an async context manager.

        Example:
            ```python
            client = AsyncIfpaClient()
            try:
                # Use client
                player = await client.player.get(12345)
            finally:
                await client.close()
            ```
        """
        await self._http.close()

    async def __aenter__(self) -> "AsyncIfpaClient":
        """Support async context manager protocol.

        Example:
            ```python
            async with AsyncIfpaClient() as client:
                player = await client.player.get(12345)
                rankings = await client.rankings.wppr(count=100)
            # Automatically closed
            ```
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close client when exiting async context manager."""
        await self.close()
