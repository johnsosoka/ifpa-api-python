"""Tournaments resource client and handle.

Provides access to tournament information, results, formats, and submissions.
"""

from typing import TYPE_CHECKING, Any

from ifpa_api.models.tournaments import (
    Tournament,
    TournamentFormatsResponse,
    TournamentLeagueResponse,
    TournamentResultsResponse,
    TournamentSearchResponse,
    TournamentSubmissionsResponse,
)

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class TournamentHandle:
    """Handle for interacting with a specific tournament.

    This class provides methods for accessing information about a specific
    tournament identified by its tournament ID.

    Attributes:
        _http: The HTTP client instance
        _tournament_id: The tournament's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(
        self, http: "_HttpClient", tournament_id: int | str, validate_requests: bool
    ) -> None:
        """Initialize a tournament handle.

        Args:
            http: The HTTP client instance
            tournament_id: The tournament's unique identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._tournament_id = tournament_id
        self._validate_requests = validate_requests

    def get(self) -> Tournament:
        """Get detailed information about this tournament.

        Returns:
            Tournament information including venue, date, and details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            tournament = client.tournament(12345).get()
            print(f"Tournament: {tournament.tournament_name}")
            print(f"Players: {tournament.player_count}")
            print(f"Date: {tournament.event_date}")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._tournament_id}")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/results")
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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/formats")
        return TournamentFormatsResponse.model_validate(response)

    def league(self) -> TournamentLeagueResponse:
        """Get league information for this tournament (if applicable).

        Returns:
            League session data and format information

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            league = client.tournament(12345).league()
            print(f"Total sessions: {league.total_sessions}")
            for session in league.sessions:
                print(f"{session.session_date}: {session.player_count} players")
            ```
        """
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/league")
        return TournamentLeagueResponse.model_validate(response)

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
        response = self._http._request("GET", f"/tournament/{self._tournament_id}/submissions")
        return TournamentSubmissionsResponse.model_validate(response)


class TournamentsClient:
    """Client for tournaments collection-level operations.

    This client provides methods for searching tournaments and accessing
    collection-level tournament information.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the tournaments client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

    def search(
        self,
        name: str | None = None,
        city: str | None = None,
        stateprov: str | None = None,
        country: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        tournament_type: str | None = None,
        start_pos: int | str | None = None,
        count: int | str | None = None,
    ) -> TournamentSearchResponse:
        """Search for tournaments.

        Args:
            name: Tournament name to search for (partial match)
            city: Filter by city
            stateprov: Filter by state/province
            country: Filter by country code
            start_date: Filter by start date (YYYY-MM-DD)
            end_date: Filter by end date (YYYY-MM-DD)
            tournament_type: Filter by tournament type (open, women, etc.)
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of matching tournaments

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Search by name
            results = client.tournaments.search(name="Pinball")

            # Search by location and date range
            results = client.tournaments.search(
                city="Portland",
                stateprov="OR",
                start_date="2024-01-01",
                end_date="2024-12-31"
            )

            # Paginated search
            results = client.tournaments.search(
                country="US",
                start_pos=0,
                count=50
            )
            ```
        """
        params: dict[str, Any] = {}
        if name is not None:
            params["name"] = name
        if city is not None:
            params["city"] = city
        if stateprov is not None:
            params["stateprov"] = stateprov
        if country is not None:
            params["country"] = country
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if tournament_type is not None:
            params["tournament_type"] = tournament_type
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", "/tournament/search", params=params)
        return TournamentSearchResponse.model_validate(response)
