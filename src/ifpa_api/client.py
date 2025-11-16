"""Main IFPA SDK client facade.

This module provides the primary entry point for interacting with the IFPA API
through a clean, typed interface.
"""

from typing import Any

from ifpa_api.config import Config
from ifpa_api.http import _HttpClient
from ifpa_api.resources.director import DirectorClient
from ifpa_api.resources.player import PlayerClient
from ifpa_api.resources.rankings import RankingsClient
from ifpa_api.resources.reference import ReferenceClient
from ifpa_api.resources.series import SeriesClient, SeriesHandle
from ifpa_api.resources.tournaments import TournamentHandle, TournamentsClient


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
        tournaments = client.director(1000).tournaments(TimePeriod.PAST)

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
        self._tournaments_client: TournamentsClient | None = None
        self._series_client: SeriesClient | None = None

    @property
    def director(self) -> DirectorClient:
        """Access the director resource client.

        Returns:
            DirectorClient instance for director operations (both collection and resource level)

        Example:
            ```python
            # Collection-level: Search for directors
            results = client.director.search(name="Josh")

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
            # Collection-level: Search for players
            results = client.player.search(name="John", stateprov="WA")

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
            self._reference_client = ReferenceClient(self._http)
        return self._reference_client

    @property
    def tournaments(self) -> TournamentsClient:
        """Access the tournaments resource client.

        Returns:
            TournamentsClient instance for searching tournaments

        Example:
            ```python
            # Search for tournaments
            results = client.tournaments.search(
                name="Pinball",
                city="Portland",
                stateprov="OR"
            )
            ```
        """
        if self._tournaments_client is None:
            self._tournaments_client = TournamentsClient(self._http, self._config.validate_requests)
        return self._tournaments_client

    @property
    def series(self) -> SeriesClient:
        """Access the series resource client.

        Returns:
            SeriesClient instance for accessing tournament series

        Example:
            ```python
            # List all series
            all_series = client.series.list()

            # Get active series only
            active = client.series.list(active_only=True)
            ```
        """
        if self._series_client is None:
            self._series_client = SeriesClient(self._http, self._config.validate_requests)
        return self._series_client

    def tournament(self, tournament_id: int | str) -> TournamentHandle:
        """Get a handle for a specific tournament.

        Args:
            tournament_id: The tournament's unique identifier

        Returns:
            TournamentHandle instance for accessing tournament-specific operations

        Example:
            ```python
            # Get tournament details
            tournament = client.tournament(12345).get()

            # Get tournament results
            results = client.tournament(12345).results()

            # Get tournament formats
            formats = client.tournament(12345).formats()

            # Get league information
            league = client.tournament(12345).league()
            ```
        """
        return TournamentHandle(self._http, tournament_id, self._config.validate_requests)

    def series_handle(self, series_code: str) -> SeriesHandle:
        """Get a handle for a specific tournament series.

        Args:
            series_code: The series code identifier

        Returns:
            SeriesHandle instance for accessing series-specific operations

        Example:
            ```python
            # Get series standings
            standings = client.series_handle("PAPA").standings()

            # Get player's series card
            card = client.series_handle("PAPA").player_card(12345)

            # Get series overview
            overview = client.series_handle("PAPA").overview()

            # Get series rules
            rules = client.series_handle("PAPA").rules()
            ```
        """
        return SeriesHandle(self._http, series_code, self._config.validate_requests)

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
