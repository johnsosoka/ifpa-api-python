"""Director resource context for individual director operations.

Provides methods for accessing information about a specific tournament director.
"""

from __future__ import annotations

from ifpa_api.core.base import BaseResourceContext
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import Director, DirectorTournamentsResponse


class _DirectorContext(BaseResourceContext[int | str]):
    """Context for interacting with a specific tournament director.

    This internal class provides resource-specific methods for a director
    identified by their director ID. Instances are returned by calling
    DirectorClient with a director ID.

    Attributes:
        _http: The HTTP client instance
        _resource_id: The director's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def details(self) -> Director:
        """Get detailed information about this director.

        Returns:
            Director information including statistics and profile

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            director = client.director(1000).details()
            print(f"Director: {director.name}")
            print(f"Tournaments: {director.stats.tournament_count}")
            ```
        """
        response = self._http._request("GET", f"/director/{self._resource_id}")
        return Director.model_validate(response)

    def tournaments(self, time_period: TimePeriod) -> DirectorTournamentsResponse:
        """Get tournaments directed by this director.

        Args:
            time_period: Whether to get past or future tournaments

        Returns:
            List of tournaments with details

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get past tournaments
            past = client.director(1000).tournaments(TimePeriod.PAST)
            for tournament in past.tournaments:
                print(f"{tournament.tournament_name} - {tournament.event_date}")

            # Get upcoming tournaments
            future = client.director(1000).tournaments(TimePeriod.FUTURE)
            ```
        """
        # Convert enum to value
        period_value = time_period.value if isinstance(time_period, TimePeriod) else time_period

        response = self._http._request(
            "GET", f"/director/{self._resource_id}/tournaments/{period_value}"
        )
        return DirectorTournamentsResponse.model_validate(response)
