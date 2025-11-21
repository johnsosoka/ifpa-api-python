"""Async director context for individual director operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ifpa_api.core.async_base import AsyncBaseResourceContext
from ifpa_api.core.deprecation import issue_deprecation_warning
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import Director, DirectorTournamentsResponse

if TYPE_CHECKING:
    pass


class AsyncDirectorContext(AsyncBaseResourceContext[int | str]):
    """Async context for interacting with a specific tournament director.

    This internal class provides async resource-specific methods for a director
    identified by their director ID. Instances are returned by calling
    AsyncDirectorClient with a director ID.

    Attributes:
        _http: The async HTTP client instance
        _resource_id: The director's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    async def details(self) -> Director:
        """Get detailed information about this director (deprecated).

        .. deprecated:: 0.4.0
            Use :meth:`AsyncDirectorClient.get` instead. For example, use
            ``await client.director.get(1533)`` instead of
            ``await client.director(1533).details()``.
            This method will be removed in version 1.0.0.

        Returns:
            Director information including statistics and profile

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Deprecated usage
            async with AsyncIfpaClient() as client:
                director = await client.director(1533).details()

            # Preferred usage
            async with AsyncIfpaClient() as client:
                director = await client.director.get(1533)
            ```
        """
        issue_deprecation_warning(
            old_name="director(id).details()",
            new_name="director.get(id)",
            version="1.0.0",
            additional_info="The new get() method provides a more direct API.",
        )
        response = await self._http._request("GET", f"/director/{self._resource_id}")
        return Director.model_validate(response)

    async def tournaments(self, time_period: TimePeriod) -> DirectorTournamentsResponse:
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
            async with AsyncIfpaClient() as client:
                past = await client.director(1533).tournaments(TimePeriod.PAST)
                for tournament in past.tournaments:
                    print(f"{tournament.tournament_name} - {tournament.event_date}")

            # Get upcoming tournaments
            async with AsyncIfpaClient() as client:
                future = await client.director(1533).tournaments(TimePeriod.FUTURE)
            ```
        """
        # Convert enum to value
        period_value = time_period.value if isinstance(time_period, TimePeriod) else time_period

        response = await self._http._request(
            "GET", f"/director/{self._resource_id}/tournaments/{period_value}"
        )
        return DirectorTournamentsResponse.model_validate(response)
