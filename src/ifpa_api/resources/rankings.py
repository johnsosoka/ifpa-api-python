"""Rankings resource client.

Provides access to various IFPA ranking systems including WPPR, Women's,
Youth, Pro, and custom rankings.
"""

from typing import TYPE_CHECKING

from ifpa_api.models.rankings import (
    CountryRankingsResponse,
    CustomRankingsResponse,
    RankingsResponse,
)

if TYPE_CHECKING:
    from ifpa_api.http import _HttpClient


class RankingsClient:
    """Client for rankings queries.

    This client provides access to various ranking systems maintained by IFPA,
    including overall WPPR, women's rankings, youth rankings, and more.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the rankings client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

    def wppr(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
        region: str | None = None,
    ) -> RankingsResponse:
        """Get main WPPR (World Pinball Player Rankings).

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code
            region: Filter by region code

        Returns:
            List of ranked players in the main WPPR system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get top 100 players
            rankings = client.rankings.wppr(start_pos=0, count=100)
            for entry in rankings.rankings:
                print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

            # Get rankings for a specific country
            us_rankings = client.rankings.wppr(country="US")
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country
        if region is not None:
            params["region"] = region

        response = self._http._request("GET", "/rankings/wppr", params=params)
        return RankingsResponse.model_validate(response)

    def women(
        self,
        tournament_type: str = "OPEN",
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get women's rankings.

        Args:
            tournament_type: Tournament type filter - "OPEN" for all tournaments or
                "WOMEN" for women-only tournaments
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the women's system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get women's rankings from all tournaments
            rankings = client.rankings.women(tournament_type="OPEN", start_pos=0, count=50)

            # Get women's rankings from women-only tournaments
            women_only = client.rankings.women(tournament_type="WOMEN", count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = self._http._request(
            "GET", f"/rankings/women/{tournament_type.lower()}", params=params
        )
        return RankingsResponse.model_validate(response)

    def youth(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get youth rankings.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the youth system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            rankings = client.rankings.youth(start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = self._http._request("GET", "/rankings/youth", params=params)
        return RankingsResponse.model_validate(response)

    def virtual(
        self,
        start_pos: int | str | None = None,
        count: int | str | None = None,
        country: str | None = None,
    ) -> RankingsResponse:
        """Get virtual tournament rankings.

        Args:
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)
            country: Filter by country code

        Returns:
            List of ranked players in the virtual system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            rankings = client.rankings.virtual(start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count
        if country is not None:
            params["country"] = country

        response = self._http._request("GET", "/rankings/virtual", params=params)
        return RankingsResponse.model_validate(response)

    def pro(
        self,
        ranking_system: str = "OPEN",
        start_pos: int | None = None,
        count: int | None = None,
    ) -> RankingsResponse:
        """Get professional circuit rankings.

        Args:
            ranking_system: Ranking system filter - "OPEN" for open division or
                "WOMEN" for women's division
            start_pos: Starting position for pagination
            count: Number of results to return (max 250)

        Returns:
            List of ranked players in the pro circuit

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Get open division pro rankings
            rankings = client.rankings.pro(ranking_system="OPEN", start_pos=0, count=50)

            # Get women's division pro rankings
            women_pro = client.rankings.pro(ranking_system="WOMEN", count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request(
            "GET", f"/rankings/pro/{ranking_system.lower()}", params=params
        )
        return RankingsResponse.model_validate(response)

    def by_country(
        self,
        country: str,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> CountryRankingsResponse:
        """Get country rankings filtered by country code or name.

        Args:
            country: Country code (e.g., "US") or country name (e.g., "United States")
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of countries ranked by various metrics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Using country code
            rankings = client.rankings.by_country(country="US", count=25)
            for entry in rankings.country_rankings:
                print(f"{entry.rank}. {entry.country_name}: {entry.total_players} players")

            # Using country name
            rankings = client.rankings.by_country(country="United States", count=10)
            ```
        """
        params = {"country": country}
        if start_pos is not None:
            params["start_pos"] = str(start_pos)
        if count is not None:
            params["count"] = str(count)

        response = self._http._request("GET", "/rankings/country", params=params)
        return CountryRankingsResponse.model_validate(response)

    def custom(
        self,
        ranking_id: str | int,
        start_pos: int | None = None,
        count: int | None = None,
    ) -> CustomRankingsResponse:
        """Get custom ranking system results.

        Args:
            ranking_id: Custom ranking system identifier
            start_pos: Starting position for pagination
            count: Number of results to return

        Returns:
            List of players in the custom ranking system

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            rankings = client.rankings.custom("regional-2024", start_pos=0, count=50)
            ```
        """
        params = {}
        if start_pos is not None:
            params["start_pos"] = start_pos
        if count is not None:
            params["count"] = count

        response = self._http._request("GET", f"/rankings/custom/{ranking_id}", params=params)
        return CustomRankingsResponse.model_validate(response)
