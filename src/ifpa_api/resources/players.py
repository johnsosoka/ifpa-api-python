"""Players resource client and handle.

Provides access to player profiles, rankings, tournament results, and
head-to-head comparisons.
"""

from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class PlayerHandle:
    """Handle for interacting with a specific player.

    This class provides methods for accessing information about a specific
    player identified by their player ID.

    Attributes:
        _http: The HTTP client instance
        _player_id: The player's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", player_id: int | str, validate_requests: bool) -> None:
        """Initialize a player handle.

        Args:
            http: The HTTP client instance
            player_id: The player's unique identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._player_id = player_id
        self._validate_requests = validate_requests

    def get(self) -> Player:
        """Get detailed information about this player.

        Returns:
            Player information including profile and rankings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            player = client.player(12345).get()
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

    def pvp(self, other_player_id: int | str) -> PvpComparison:
        """Get head-to-head comparison with another player.

        Args:
            other_player_id: The ID of the player to compare against

        Returns:
            Head-to-head comparison data

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            comparison = client.player(12345).pvp(67890)
            print(f"Wins: {comparison.player1_wins}")
            print(f"Losses: {comparison.player2_wins}")
            print(f"Ties: {comparison.ties}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/pvp/{other_player_id}")
        return PvpComparison.model_validate(response)

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


class PlayersClient:
    """Client for players collection-level operations.

    This client provides methods for searching players and accessing
    collection-level player information.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the players client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

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
            # Search by name
            results = client.players.search(name="John")

            # Search by location
            results = client.players.search(city="Seattle", stateprov="WA")

            # Search by tournament participation
            results = client.players.search(tournament="PAPA", tourpos=1)

            # Paginated search
            results = client.players.search(name="Smith", start_pos=0, count=25)
            ```
        """
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

        Args:
            player_ids: List of player IDs (max 50)

        Returns:
            MultiPlayerResponse containing the requested players

        Raises:
            IfpaClientValidationError: If more than 50 player IDs provided
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Fetch multiple players efficiently
            result = client.players.get_multiple([123, 456, 789])
            if isinstance(result.player, list):
                for player in result.player:
                    print(f"{player.first_name} {player.last_name}")
            ```
        """
        from ifpa_api.exceptions import IfpaClientValidationError

        if len(player_ids) > 50:
            raise IfpaClientValidationError("Maximum 50 player IDs allowed per request")

        # Join IDs with commas
        players_param = ",".join(str(pid) for pid in player_ids)
        params = {"players": players_param}

        response = self._http._request("GET", "/player", params=params)
        return MultiPlayerResponse.model_validate(response)
