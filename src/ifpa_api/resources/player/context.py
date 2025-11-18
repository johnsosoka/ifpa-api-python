"""Player context for individual player operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceContext
from ifpa_api.core.exceptions import IfpaApiError, PlayersNeverMetError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    Player,
    PlayerResultsResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)

if TYPE_CHECKING:
    pass


class _PlayerContext(BaseResourceContext[int | str]):
    """Context for interacting with a specific player.

    This internal class provides resource-specific methods for a player
    identified by their player ID. Instances are returned by calling
    PlayerClient with a player ID.

    Attributes:
        _http: The HTTP client instance
        _resource_id: The player's unique identifier
        _validate_requests: Whether to validate request parameters
    """

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
        response = self._http._request("GET", f"/player/{self._resource_id}")
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
        response = self._http._request("GET", f"/player/{self._resource_id}/pvp")
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
            response = self._http._request("GET", f"/player/{self._resource_id}/pvp/{opponent_id}")

            # Check for error response (API returns HTTP 200 with error payload)
            if isinstance(response, dict) and response.get("code") == "404":
                raise PlayersNeverMetError(self._resource_id, opponent_id)

            return PvpComparison.model_validate(response)
        except IfpaApiError as e:
            # Check if this is a 404 indicating players never met
            if e.status_code == 404:
                raise PlayersNeverMetError(self._resource_id, opponent_id) from e
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

        path = f"/player/{self._resource_id}/results/{system_value}/{type_value}"

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
        response = self._http._request("GET", f"/player/{self._resource_id}/rank_history")
        return RankingHistory.model_validate(response)
