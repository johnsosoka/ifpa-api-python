"""Players resource client with callable pattern.

Provides access to player profiles, rankings, tournament results, and
head-to-head comparisons.
"""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Self

from ifpa_api.exceptions import IfpaApiError, PlayersNeverMetError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    MultiPlayerResponse,
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)
from ifpa_api.query_builder import QueryBuilder

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class _PlayerContext:
    """Context for interacting with a specific player.

    This internal class provides resource-specific methods for a player
    identified by their player ID. Instances are returned by calling
    PlayerClient with a player ID.

    Attributes:
        _http: The HTTP client instance
        _player_id: The player's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: _HttpClient, player_id: int | str, validate_requests: bool) -> None:
        """Initialize a player context.

        Args:
            http: The HTTP client instance
            player_id: The player's unique identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._player_id = player_id
        self._validate_requests = validate_requests

    def details(self) -> Player:
        """Get detailed information about this player.

        Returns:
            Player information including profile and rankings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            player = client.player(12345).details()
            print(f"{player.first_name} {player.last_name}")
            print(f"Country: {player.country_name}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}")
        # API returns {"player": [player_object]}
        if isinstance(response, dict) and "player" in response:
            player_data = response["player"]
            if isinstance(player_data, list) and len(player_data) > 0:
                return Player.model_validate(player_data[0])
        return Player.model_validate(response)

    def pvp_all(self) -> PvpAllCompetitors:
        """Get summary of all players this player has competed against.

        Returns:
            PvpAllCompetitors containing total count and metadata

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            summary = client.player(2643).pvp_all()
            print(f"Competed against {summary.total_competitors} players")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/pvp")
        return PvpAllCompetitors.model_validate(response)

    def pvp(self, opponent_id: int | str) -> PvpComparison:
        """Get head-to-head comparison between this player and another player.

        Returns detailed head-to-head statistics including wins, losses, ties, and
        a list of all tournaments where these players have competed against each other.

        Args:
            opponent_id: ID of the opponent player to compare against.

        Returns:
            PvpComparison with head-to-head statistics and tournament history.

        Raises:
            PlayersNeverMetError: If the two players have never competed in the same tournament.
                Note: This exception is raised by the client to provide a clearer error message
                when the IFPA API returns a 404 indicating no head-to-head data exists.
            IfpaApiError: If the API request fails for other reasons.

        Example:
            ```python
            from ifpa_api.exceptions import PlayersNeverMetError

            try:
                # Compare two players
                pvp = client.player(12345).pvp(67890)
                print(f"Player 1 wins: {pvp.player1_wins}")
                print(f"Player 2 wins: {pvp.player2_wins}")
                print(f"Total meetings: {pvp.total_meetings}")

                # List tournaments where they met
                for tourney in pvp.tournaments:
                    print(f"  {tourney.event_name}: Winner was player {tourney.winner_player_id}")
            except PlayersNeverMetError:
                print("These players have never competed together")
            ```
        """

        try:
            response = self._http._request("GET", f"/player/{self._player_id}/pvp/{opponent_id}")

            # Check for error response (API returns HTTP 200 with error payload)
            if isinstance(response, dict) and response.get("code") == "404":
                raise PlayersNeverMetError(self._player_id, opponent_id)

            return PvpComparison.model_validate(response)
        except IfpaApiError as e:
            # Check if this is a 404 indicating players never met
            if e.status_code == 404:
                raise PlayersNeverMetError(self._player_id, opponent_id) from e
            # Re-raise for other API errors
            raise

    def results(
        self,
        ranking_system: RankingSystem,
        result_type: ResultType,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> PlayerResultsResponse:
        """Get player's tournament results.

        Both ranking_system and result_type are required by the API endpoint.

        Args:
            ranking_system: Filter by ranking system (Main, Women, Youth, etc.) - REQUIRED
            result_type: Filter by result activity (active, nonactive, inactive) - REQUIRED
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of tournament results

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get all active results
            results = client.player(12345).results(
                ranking_system=RankingSystem.MAIN,
                result_type=ResultType.ACTIVE
            )

            # Get paginated results
            results = client.player(12345).results(
                ranking_system=RankingSystem.MAIN,
                result_type=ResultType.ACTIVE,
                start_pos=0,
                count=50
            )
            ```
        """
        # Both parameters are required - build path directly
        system_value = (
            ranking_system.value if isinstance(ranking_system, RankingSystem) else ranking_system
        )
        type_value = result_type.value if isinstance(result_type, ResultType) else result_type

        path = f"/player/{self._player_id}/results/{system_value}/{type_value}"

        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", path, params=params)
        return PlayerResultsResponse.model_validate(response)

    def history(self) -> RankingHistory:
        """Get player's WPPR ranking and rating history over time.

        Returns:
            Historical ranking data with separate rank_history and rating_history arrays

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            history = client.player(12345).history()
            for entry in history.rank_history:
                print(f"{entry.rank_date}: Rank {entry.rank_position}")
            for entry in history.rating_history:
                print(f"{entry.rating_date}: Rating {entry.rating}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/rank_history")
        return RankingHistory.model_validate(response)


class PlayerQueryBuilder(QueryBuilder[PlayerSearchResponse]):
    """Fluent query builder for player search operations.

    This class implements an immutable query builder pattern for searching players.
    Each method returns a new instance, allowing safe query composition and reuse.

    Attributes:
        _http: The HTTP client instance
        _params: Accumulated query parameters

    Example:
        ```python
        # Simple query
        results = client.player.query("John").get()

        # Chained filters with immutability
        us_query = client.player.query().country("US")
        wa_players = us_query.state("WA").limit(25).get()
        or_players = us_query.state("OR").limit(25).get()  # base unchanged!

        # Complex query
        results = (client.player.query("Smith")
            .country("CA")
            .tournament("PAPA")
            .position(1)
            .limit(50)
            .get())
        ```
    """

    def __init__(self, http: _HttpClient) -> None:
        """Initialize the player query builder.

        Args:
            http: The HTTP client instance
        """
        super().__init__()
        self._http = http

    def query(self, name: str) -> Self:
        """Set the player name to search for.

        Args:
            name: Player name to search for (partial match, not case sensitive)

        Returns:
            New PlayerQueryBuilder instance with the name parameter set

        Example:
            ```python
            results = client.player.query("John").get()
            ```
        """
        clone = self._clone()
        clone._params["name"] = name
        return clone

    def state(self, state_code: str) -> Self:
        """Filter by state/province.

        Args:
            state_code: 2-digit state or province code (e.g., "WA", "BC")

        Returns:
            New PlayerQueryBuilder instance with the state filter applied

        Example:
            ```python
            results = client.player.query("John").state("WA").get()
            ```
        """
        clone = self._clone()
        clone._params["stateprov"] = state_code
        return clone

    def country(self, country_code: str) -> Self:
        """Filter by country.

        Args:
            country_code: Country name or 2-digit country code (e.g., "US", "CA")

        Returns:
            New PlayerQueryBuilder instance with the country filter applied

        Example:
            ```python
            results = client.player.query().country("US").get()
            ```
        """
        clone = self._clone()
        clone._params["country"] = country_code
        return clone

    def tournament(self, tournament_name: str) -> Self:
        """Filter by tournament participation.

        Args:
            tournament_name: Tournament name (partial strings accepted)

        Returns:
            New PlayerQueryBuilder instance with the tournament filter applied

        Example:
            ```python
            results = client.player.query().tournament("PAPA").get()
            ```
        """
        clone = self._clone()
        clone._params["tournament"] = tournament_name
        return clone

    def position(self, finish_position: int) -> Self:
        """Filter by finishing position in tournament.

        Must be used with tournament() filter.

        Args:
            finish_position: Tournament finishing position to filter by

        Returns:
            New PlayerQueryBuilder instance with the position filter applied

        Example:
            ```python
            # Find all players who won PAPA
            results = client.player.query().tournament("PAPA").position(1).get()
            ```
        """
        clone = self._clone()
        clone._params["tourpos"] = finish_position
        return clone

    def offset(self, start_position: int) -> Self:
        """Set pagination offset.

        Args:
            start_position: Starting position for pagination (0-based)

        Returns:
            New PlayerQueryBuilder instance with the offset set

        Example:
            ```python
            # Get second page of results
            results = client.player.query("Smith").offset(25).limit(25).get()
            ```
        """
        clone = self._clone()
        clone._params["start_pos"] = start_position
        return clone

    def limit(self, count: int) -> Self:
        """Set maximum number of results to return.

        Args:
            count: Maximum number of results

        Returns:
            New PlayerQueryBuilder instance with the limit set

        Example:
            ```python
            results = client.player.query("John").limit(50).get()
            ```
        """
        clone = self._clone()
        clone._params["count"] = count
        return clone

    def get(self) -> PlayerSearchResponse:
        """Execute the query and return results.

        Returns:
            PlayerSearchResponse containing matching players

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.player.query("John").country("US").get()
            print(f"Found {len(results.search)} players")
            for player in results.search:
                print(f"{player.first_name} {player.last_name}")
            ```
        """
        response = self._http._request("GET", "/player/search", params=self._params)
        return PlayerSearchResponse.model_validate(response)


class PlayerClient:
    """Callable client for player operations.

    This client provides both collection-level methods (search, get_multiple) and
    resource-level access via the callable pattern. Call with a player ID to get
    a context for player-specific operations.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters

    Example:
        ```python
        # Collection-level operations
        results = client.player.search(name="John")
        players = client.player.get_multiple([123, 456])

        # Resource-level operations
        player = client.player(12345).details()
        pvp = client.player(12345).pvp(67890)
        results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
        ```
    """

    def __init__(self, http: _HttpClient, validate_requests: bool) -> None:
        """Initialize the player client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

    def __call__(self, player_id: int | str) -> _PlayerContext:
        """Get a context for a specific player.

        Args:
            player_id: The player's unique identifier

        Returns:
            _PlayerContext instance for accessing player-specific operations

        Example:
            ```python
            # Get player context and access methods
            player = client.player(12345).details()
            pvp = client.player(12345).pvp(67890)
            history = client.player(12345).history()
            ```
        """
        return _PlayerContext(self._http, player_id, self._validate_requests)

    def query(self, name: str = "") -> PlayerQueryBuilder:
        """Create a fluent query builder for searching players.

        This is the recommended way to search for players, providing a type-safe
        and composable interface. The returned builder can be reused and composed
        thanks to its immutable pattern.

        Args:
            name: Optional player name to search for (can also be set via .query() on builder)

        Returns:
            PlayerQueryBuilder instance for building the search query

        Example:
            ```python
            # Simple name search
            results = client.player.query("John").get()

            # Chained filters
            results = (client.player.query("Smith")
                .country("US")
                .state("WA")
                .limit(25)
                .get())

            # Query reuse (immutable pattern)
            us_base = client.player.query().country("US")
            wa_players = us_base.state("WA").get()
            or_players = us_base.state("OR").get()  # base unchanged!

            # Empty query to start with filters
            results = (client.player.query()
                .tournament("PAPA")
                .position(1)
                .get())
            ```
        """
        builder = PlayerQueryBuilder(self._http)
        if name:
            return builder.query(name)
        return builder

    def search(
        self,
        name: str | None = None,
        stateprov: str | None = None,
        country: str | None = None,
        tournament: str | None = None,
        tourpos: int | None = None,
        start_pos: int | str | None = None,
        count: int | str | None = None,
    ) -> PlayerSearchResponse:
        """Search for players.

        .. deprecated:: 0.2.0
            Use :meth:`query` instead for a more fluent and type-safe interface.
            This method will be removed in version 1.0.0.

            Migration example:
                Old: ``client.player.search(name="John", country="US", count=25)``

                New: ``client.player.query("John").country("US").limit(25).get()``

        Args:
            name: Player name to search for (partial match, not case sensitive)
            stateprov: Filter by state/province (2-digit code)
            country: Filter by country name or 2-digit code
            tournament: Filter by tournament name (partial strings accepted)
            tourpos: Filter by finishing position in tournament
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of matching players

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # DEPRECATED - Use query() instead
            # Search by name
            results = client.player.search(name="John")

            # Search by location
            results = client.player.search(stateprov="WA", country="US")

            # Search by tournament participation
            results = client.player.search(tournament="PAPA", tourpos=1)

            # Paginated search
            results = client.player.search(name="Smith", start_pos=0, count=25)
            ```
        """
        warnings.warn(
            "PlayerClient.search() is deprecated and will be removed in version 1.0.0. "
            "Use PlayerClient.query() for a more fluent and type-safe interface. "
            "Example: client.player.query('John').country('US').limit(25).get()",
            DeprecationWarning,
            stacklevel=2,
        )
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if stateprov is not None:
            params["stateprov"] = stateprov
        if country is not None:
            params["country"] = country
        if tournament is not None:
            params["tournament"] = tournament
        if tourpos is not None:
            params["tourpos"] = tourpos
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", "/player/search", params=params)
        return PlayerSearchResponse.model_validate(response)

    def get_multiple(self, player_ids: list[int | str]) -> MultiPlayerResponse:
        """Fetch multiple players in a single request.

        .. deprecated:: 0.2.0
            This method will be removed in version 1.0.0. Use the callable pattern
            with individual player IDs instead.

            Migration example:
                Old: ``result = client.player.get_multiple([123, 456])``

                New: ``player1 = client.player(123).details()``
                     ``player2 = client.player(456).details()``

        Args:
            player_ids: List of player IDs (max 50)

        Returns:
            MultiPlayerResponse containing the requested players

        Raises:
            IfpaClientValidationError: If more than 50 player IDs provided
            IfpaApiError: If the API request fails

        Example:
            ```python
            # DEPRECATED - Use callable pattern instead
            # Fetch multiple players efficiently
            result = client.player.get_multiple([123, 456, 789])
            if isinstance(result.player, list):
                for player in result.player:
                    print(f"{player.first_name} {player.last_name}")
            ```
        """
        warnings.warn(
            "PlayerClient.get_multiple() is deprecated and will be removed in version 1.0.0. "
            "Use the callable pattern instead: client.player(player_id).details()",
            DeprecationWarning,
            stacklevel=2,
        )
        from ifpa_api.exceptions import IfpaClientValidationError

        if len(player_ids) > 50:
            raise IfpaClientValidationError("Maximum 50 player IDs allowed per request")

        # Join IDs with commas
        players_param = ",".join(str(pid) for pid in player_ids)
        params = {"players": players_param}

        response = self._http._request("GET", "/player", params=params)
        return MultiPlayerResponse.model_validate(response)
