"""Players resource client and handle.

Provides access to player profiles, rankings, tournament results, and
head-to-head comparisons.
"""

from typing import TYPE_CHECKING, Any

from ifpa_sdk.models.common import RankingSystem, ResultType
from ifpa_sdk.models.player import (
    Player,
    PlayerCard,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpComparison,
    RankingHistory,
)

if TYPE_CHECKING:
    from ifpa_sdk.http import _HttpClient


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

    def rankings(self) -> list[dict[str, str | int | float | None]]:
        """Get player's rankings across all ranking systems.

        Returns:
            List of rankings in different systems (Main, Women, Youth, etc.)

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            rankings = client.player(12345).rankings()
            for ranking in rankings:
                print(f"{ranking['system']}: Rank {ranking['rank']}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/rankings")
        return response if isinstance(response, list) else []

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
        ranking_system: RankingSystem | None = None,
        result_type: ResultType | None = None,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> PlayerResultsResponse:
        """Get player's tournament results.

        Args:
            ranking_system: Filter by ranking system (Main, Women, Youth, etc.)
            result_type: Filter by result activity (active, nonactive, inactive)
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
            results = client.player(12345).results(start_pos=0, count=50)
            ```
        """
        # Build path with optional ranking system and type
        path_parts = [f"/player/{self._player_id}/results"]

        if ranking_system is not None:
            system_value = (
                ranking_system.value
                if isinstance(ranking_system, RankingSystem)
                else ranking_system
            )
            path_parts.append(system_value)

            if result_type is not None:
                type_value = (
                    result_type.value if isinstance(result_type, ResultType) else result_type
                )
                path_parts.append(type_value)

        path = "/".join(path_parts)

        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", path, params=params)
        return PlayerResultsResponse.model_validate(response)

    def history(self) -> RankingHistory:
        """Get player's WPPR ranking history over time.

        Returns:
            Historical ranking data

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            history = client.player(12345).history()
            for entry in history.history:
                print(f"{entry.date}: Rank {entry.rank}, WPPR {entry.rating}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/rank_history")
        return RankingHistory.model_validate(response)

    def cards(self) -> PlayerCard:
        """Get player's achievement cards and badges.

        Returns:
            Player cards and achievements

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            cards = client.player(12345).cards()
            print(f"Cards earned: {len(cards.cards)}")
            ```
        """
        response = self._http._request("GET", f"/player/{self._player_id}/cards")
        return PlayerCard.model_validate(response)


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
        first_name: str | None = None,
        last_name: str | None = None,
        city: str | None = None,
        stateprov: str | None = None,
        country: str | None = None,
        start_pos: int | str | None = None,
        count: int | str | None = None,
    ) -> PlayerSearchResponse:
        """Search for players.

        Args:
            name: Player name to search for (partial match)
            first_name: Filter by first name
            last_name: Filter by last name
            city: Filter by city
            stateprov: Filter by state/province
            country: Filter by country code
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

            # Paginated search
            results = client.players.search(name="Smith", start_pos=0, count=25)
            ```
        """
        params: dict[str, Any] = {}
        if name is not None:
            params["q"] = name
        if first_name is not None:
            params["first_name"] = first_name
        if last_name is not None:
            params["last_name"] = last_name
        if city is not None:
            params["city"] = city
        if stateprov is not None:
            params["stateprov"] = stateprov
        if country is not None:
            params["country"] = country
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", "/player/search", params=params)
        return PlayerSearchResponse.model_validate(response)
