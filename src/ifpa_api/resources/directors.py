"""Directors resource client and handle.

Provides access to tournament director information, their tournament history,
and search capabilities.
"""

from typing import TYPE_CHECKING

from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import (
    CountryDirectorsResponse,
    Director,
    DirectorSearchResponse,
    DirectorTournamentsResponse,
)

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class DirectorHandle:
    """Handle for interacting with a specific tournament director.

    This class provides methods for accessing information about a specific
    director identified by their director ID.

    Attributes:
        _http: The HTTP client instance
        _director_id: The director's unique identifier
        _validate_requests: Whether to validate request parameters
    """

    def __init__(
        self, http: "_HttpClient", director_id: int | str, validate_requests: bool
    ) -> None:
        """Initialize a director handle.

        Args:
            http: The HTTP client instance
            director_id: The director's unique identifier
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._director_id = director_id
        self._validate_requests = validate_requests

    def get(self) -> Director:
        """Get detailed information about this director.

        Returns:
            Director information including statistics and profile

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            director = client.director(1000).get()
            print(f"Director: {director.name}")
            print(f"Tournaments: {director.stats.tournament_count}")
            ```
        """
        response = self._http._request("GET", f"/director/{self._director_id}")
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
            "GET", f"/director/{self._director_id}/tournaments/{period_value}"
        )
        return DirectorTournamentsResponse.model_validate(response)


class DirectorsClient:
    """Client for directors collection-level operations.

    This client provides methods for searching directors and accessing
    collection-level director information.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the directors client.

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
    ) -> DirectorSearchResponse:
        """Search for tournament directors.

        Args:
            name: Director name to search for (partial match)
            city: Filter by city
            stateprov: Filter by state/province
            country: Filter by country code

        Returns:
            List of matching directors

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Search by name
            results = client.directors.search(name="Josh")

            # Search by location
            results = client.directors.search(city="Chicago", stateprov="IL")
            ```
        """
        params = {}
        if name is not None:
            params["name"] = name
        if city is not None:
            params["city"] = city
        if stateprov is not None:
            params["stateprov"] = stateprov
        if country is not None:
            params["country"] = country

        response = self._http._request("GET", "/director/search", params=params)
        return DirectorSearchResponse.model_validate(response)

    def country_directors(self) -> CountryDirectorsResponse:
        """Get list of IFPA country directors.

        Returns:
            List of country directors with their assigned countries

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            country_dirs = client.directors.country_directors()
            for director in country_dirs.country_directors:
                print(f"{director.name} - {director.country_name}")
            ```
        """
        response = self._http._request("GET", "/director/country")
        return CountryDirectorsResponse.model_validate(response)
