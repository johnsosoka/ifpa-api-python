"""Tournament context for individual tournament operations.

Provides resource-specific methods for a tournament identified by its tournament ID.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.base import BaseResourceContext
from ifpa_api.core.exceptions import IfpaApiError, TournamentNotLeagueError
from ifpa_api.models.tournaments import (
    RelatedTournamentsResponse,
    Tournament,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSubmissionsResponse,
)

if TYPE_CHECKING:
    pass


# ============================================================================
# Tournament Context - Individual Tournament Operations
# ============================================================================


class _TournamentContext(BaseResourceContext[int | str]):
    """Context for interacting with a specific tournament.

    This internal class provides resource-specific methods for a tournament
    identified by its tournament ID. Instances are returned by calling
    TournamentClient with a tournament ID.

    Attributes:
        _http: The HTTP client instance
        _resource_id: The tournament's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def details(self) -> Tournament:
        """Get detailed information about this tournament.

        Returns:
            Tournament information including venue, date, and details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            tournament = client.tournament(12345).details()
            print(f"Tournament: {tournament.tournament_name}")
            print(f"Players: {tournament.player_count}")
            print(f"Date: {tournament.event_date}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}")
        return Tournament.model_validate(response)

    def results(self) -> TournamentResultsResponse:
        """Get results for this tournament.

        Returns:
            List of player results and standings

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            results = client.tournament(12345).results()
            for result in results.results:
                print(f"{result.position}. {result.player_name}: {result.wppr_points} WPPR")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/results")
        return TournamentResultsResponse.model_validate(response)

    def formats(self) -> TournamentFormatsResponse:
        """Get format information for this tournament.

        Returns:
            List of formats used in the tournament

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            formats = client.tournament(12345).formats()
            for fmt in formats.formats:
                print(f"Format: {fmt.format_name}")
                print(f"Rounds: {fmt.rounds}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/formats")
        return TournamentFormatsResponse.model_validate(response)

    def league(self) -> TournamentLeagueResponse:
        """Get league information for this tournament (if applicable).

        Returns:
            League session data and format information

        Raises:
            TournamentNotLeagueError: If the tournament is not a league-format tournament
            IfpaApiError: If the API request fails for other reasons

        Example:
            ```python
            from ifpa_api.exceptions import TournamentNotLeagueError

            try:
                league = client.tournament(12345).league()
                print(f"Total sessions: {league.total_sessions}")
                for session in league.sessions:
                    print(f"{session.session_date}: {session.player_count} players")
            except TournamentNotLeagueError as e:
                print(f"Tournament {e.tournament_id} is not a league")
            ```
        """
        try:
            response = self._http._request("GET", f"/tournament/{self._resource_id}/league")
            return TournamentLeagueResponse.model_validate(response)
        except IfpaApiError as e:
            # Convert 404 to semantic exception
            if e.status_code == 404:
                raise TournamentNotLeagueError(self._resource_id) from e
            # Re-raise other API errors
            raise

    def submissions(self) -> TournamentSubmissionsResponse:
        """Get submission information for this tournament.

        Returns:
            List of tournament submissions

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            submissions = client.tournament(12345).submissions()
            for submission in submissions.submissions:
                print(f"{submission.submission_date}: {submission.status}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/submissions")
        return TournamentSubmissionsResponse.model_validate(response)

    def related(self) -> RelatedTournamentsResponse:
        """Get tournaments related to this tournament.

        Returns tournaments that are part of the same tournament series or held at
        the same venue. This is useful for finding recurring events and historical
        data for tournament series.

        Returns:
            RelatedTournamentsResponse with list of related tournaments.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get related tournaments
            tournament = client.tournament(12345).details()
            related = client.tournament(12345).related()

            print(f"Found {len(related.tournament)} related tournaments")
            for t in related.tournament:
                print(f"  {t.event_start_date}: {t.tournament_name}")
                if t.winner:
                    print(f"    Winner: {t.winner.name}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._resource_id}/related")
        return RelatedTournamentsResponse.model_validate(response)
