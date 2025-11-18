"""Main IFPA SDK client facade.

This module provides the primary entry point for interacting with the IFPA API
through a clean, typed interface.
"""

from typing import Any

from ifpa_api.core.config import Config
from ifpa_api.core.http import _HttpClient
from ifpa_api.resources.director import DirectorClient
from ifpa_api.resources.player import PlayerClient
from ifpa_api.resources.rankings import RankingsClient
from ifpa_api.resources.reference import ReferenceClient
from ifpa_api.resources.series import SeriesClient
from ifpa_api.resources.tournament import TournamentClient


class IfpaClient:
    """Main client for interacting with the IFPA API.

    This client provides access to all IFPA resources including players,
    tournaments, rankings, series, and statistics. It manages authentication,
    HTTP sessions, and provides a clean interface for SDK users.

    Attributes:
        _config: Configuration settings including API key and base URL
        _http: Internal HTTP client for making requests

    Example:
        ```python
        from ifpa_api import IfpaClient, TimePeriod

        # Initialize with API key from environment variable
        client = IfpaClient()

        # Or provide API key explicitly
        client = IfpaClient(api_key="your-api-key")

        # Access resources
        player = client.player(12345).details()
        rankings = client.rankings.wppr(start_pos=0, count=100)
        director = client.director(1000).details()
        director_tourneys = client.director(1000).tournaments(TimePeriod.PAST)
        tournament = client.tournament(12345).details()

        # Close when done (or use context manager)
        client.close()
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
        """Initialize the IFPA API client.

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

        Example:
            ```python
            # Use environment variable
            client = IfpaClient()

            # Explicit API key
            client = IfpaClient(api_key="your-key")

            # Custom configuration
            client = IfpaClient(
                api_key="your-key",
                timeout=30.0,
                validate_requests=False
            )
            ```
        """
        self._config = Config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            validate_requests=validate_requests,
        )
        self._http = _HttpClient(self._config)

        # Initialize resource clients (lazy-loaded via properties)
        self._director_client: DirectorClient | None = None
        self._player_client: PlayerClient | None = None
        self._rankings_client: RankingsClient | None = None
        self._reference_client: ReferenceClient | None = None
        self._tournament_client: TournamentClient | None = None
        self._series_client: SeriesClient | None = None

    @property
    def director(self) -> DirectorClient:
        """Access the director resource client.

        Returns:
            DirectorClient instance for director operations (both collection and resource level)

        Example:
            ```python
            # Collection-level: Query for directors
            results = client.director.query("Josh").get()

            # Collection-level: Query with filters
            results = client.director.query("Josh").country("US").state("IL").get()

            # Collection-level: Get country directors
            country_dirs = client.director.country_directors()

            # Resource-level: Get director details
            director = client.director(1000).details()

            # Resource-level: Get director's tournaments
            past = client.director(1000).tournaments(TimePeriod.PAST)
            ```
        """
        if self._director_client is None:
            self._director_client = DirectorClient(self._http, self._config.validate_requests)
        return self._director_client

    @property
    def player(self) -> PlayerClient:
        """Access the player resource client.

        Returns:
            PlayerClient instance for player operations (both collection and resource level)

        Example:
            ```python
            # Collection-level: Query for players
            results = client.player.query("John").get()

            # Collection-level: Query with filters
            results = client.player.query("John").state("WA").country("US").get()

            # Resource-level: Get player details
            player = client.player(12345).details()

            # Resource-level: Get PVP comparison
            pvp = client.player(12345).pvp(67890)
            ```
        """
        if self._player_client is None:
            self._player_client = PlayerClient(self._http, self._config.validate_requests)
        return self._player_client

    @property
    def rankings(self) -> RankingsClient:
        """Access the rankings resource client.

        Returns:
            RankingsClient instance for accessing various ranking systems

        Example:
            ```python
            # Get WPPR rankings
            wppr = client.rankings.wppr(start_pos=0, count=100)

            # Get women's rankings
            women = client.rankings.women(country="US")

            # Get country rankings
            countries = client.rankings.by_country()
            ```
        """
        if self._rankings_client is None:
            self._rankings_client = RankingsClient(self._http, self._config.validate_requests)
        return self._rankings_client

    @property
    def reference(self) -> ReferenceClient:
        """Access reference data endpoints.

        Provides access to lookup/reference data such as countries and states/provinces.

        Returns:
            ReferenceClient for accessing reference data.

        Example:
            ```python
            # Get all countries
            countries = client.reference.countries()

            # Get states/provinces
            state_provs = client.reference.state_provs()
            ```
        """
        if self._reference_client is None:
            self._reference_client = ReferenceClient(self._http, self._config.validate_requests)
        return self._reference_client

    @property
    def tournament(self) -> TournamentClient:
        """Access the tournament resource client.

        Returns:
            TournamentClient instance for tournament operations (both collection and resource level)

        Example:
            ```python
            # Collection-level: Query for tournaments
            results = client.tournament.query("Pinball").get()

            # Collection-level: Query with filters
            results = client.tournament.query("Pinball").city("Portland").state("OR").get()

            # Collection-level: List tournament formats
            formats = client.tournament.list_formats()

            # Resource-level: Get tournament details
            tournament = client.tournament(12345).details()

            # Resource-level: Get tournament results
            results = client.tournament(12345).results()
            ```
        """
        if self._tournament_client is None:
            self._tournament_client = TournamentClient(self._http, self._config.validate_requests)
        return self._tournament_client

    @property
    def series(self) -> SeriesClient:
        """Access the series resource client.

        Returns:
            SeriesClient instance for series operations (both collection and resource level)

        Example:
            ```python
            # Collection-level: List all series
            all_series = client.series.list()
            active = client.series.list(active_only=True)

            # Resource-level: Get series standings
            standings = client.series("NACS").standings()

            # Resource-level: Get player's series card
            card = client.series("PAPA").player_card(12345, "OH")

            # Resource-level: Get region standings
            region = client.series("NACS").region_standings("OH")
            ```
        """
        if self._series_client is None:
            self._series_client = SeriesClient(self._http, self._config.validate_requests)
        return self._series_client

    def close(self) -> None:
        """Close the HTTP client session.

        This should be called when the client is no longer needed to properly
        clean up resources. Alternatively, use the client as a context manager.

        Example:
            ```python
            client = IfpaClient()
            try:
                # Use client
                player = client.player(12345).details()
            finally:
                client.close()
            ```
        """
        self._http.close()

    def __enter__(self) -> "IfpaClient":
        """Support context manager protocol.

        Example:
            ```python
            with IfpaClient() as client:
                player = client.player(12345).details()
                rankings = client.rankings.wppr(count=100)
            # Automatically closed
            ```
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close client when exiting context manager."""
        self.close()
