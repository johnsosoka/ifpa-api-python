"""Statistics resource client.

Provides access to global statistics, trends, and aggregate data across
the IFPA ecosystem.
"""

from typing import TYPE_CHECKING, Any

from ifpa_sdk.models.stats import (
    GlobalStats,
    HistoricalStatsResponse,
    MachinePopularityResponse,
    ParticipationStatsResponse,
    PlayerCountStatsResponse,
    RecentTournamentsResponse,
    TopCountriesResponse,
    TopTournamentsResponse,
    TournamentCountStatsResponse,
    TrendsResponse,
)

if TYPE_CHECKING:
    from ifpa_sdk.http import _HttpClient


class StatsClient:
    """Client for statistics queries.

    This client provides access to various statistical views of IFPA data,
    including global stats, trends, participation data, and more.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def __init__(self, http: "_HttpClient", validate_requests: bool) -> None:
        """Initialize the statistics client.

        Args:
            http: The HTTP client instance
            validate_requests: Whether to validate request parameters
        """
        self._http = http
        self._validate_requests = validate_requests

    def global_stats(self) -> GlobalStats:
        """Get global IFPA statistics.

        Returns:
            Global statistics including total players, tournaments, and aggregates

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.global_stats()
            print(f"Total Players: {stats.total_players}")
            print(f"Total Tournaments: {stats.total_tournaments}")
            print(f"Active Players: {stats.total_active_players}")
            ```
        """
        response = self._http._request("GET", "/stats/global")
        return GlobalStats.model_validate(response)

    def player_counts(
        self,
        period: str | None = None,
    ) -> PlayerCountStatsResponse:
        """Get player count statistics over time or by category.

        Args:
            period: Time period filter (e.g., "year", "month")

        Returns:
            Player count statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.player_counts(period="year")
            for stat in stats.stats:
                print(f"{stat.period}: {stat.player_count} players")
            ```
        """
        params = {}
        if period is not None:
            params["period"] = period

        response = self._http._request("GET", "/stats/player_counts", params=params)
        return PlayerCountStatsResponse.model_validate(response)

    def tournament_counts(
        self,
        period: str | None = None,
    ) -> TournamentCountStatsResponse:
        """Get tournament count statistics over time or by category.

        Args:
            period: Time period filter (e.g., "year", "month")

        Returns:
            Tournament count statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.tournament_counts(period="year")
            for stat in stats.stats:
                print(f"{stat.period}: {stat.tournament_count} tournaments")
            ```
        """
        params = {}
        if period is not None:
            params["period"] = period

        response = self._http._request("GET", "/stats/tournament_counts", params=params)
        return TournamentCountStatsResponse.model_validate(response)

    def top_countries(
        self,
        limit: int | None = None,
    ) -> TopCountriesResponse:
        """Get statistics for top countries.

        Args:
            limit: Number of countries to return

        Returns:
            Top countries by various metrics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.top_countries(limit=10)
            for country in stats.countries:
                print(f"{country.rank}. {country.country_name}: {country.player_count} players")
            ```
        """
        params = {}
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/top_countries", params=params)
        return TopCountriesResponse.model_validate(response)

    def top_tournaments(
        self,
        criteria: str | None = None,
        limit: int | str | None = None,
    ) -> TopTournamentsResponse:
        """Get statistics for top tournaments.

        Args:
            criteria: Ranking criteria (e.g., "size", "value", "recent")
            limit: Number of tournaments to return

        Returns:
            Top tournaments by specified criteria

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Top tournaments by size
            stats = client.stats.top_tournaments(criteria="size", limit=10)
            for tournament in stats.tournaments:
                print(
                    f"{tournament.rank}. {tournament.tournament_name}: "
                    f"{tournament.player_count} players"
                )
            ```
        """
        params: dict[str, Any] = {}
        if criteria is not None:
            params["criteria"] = criteria
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/top_tournaments", params=params)
        return TopTournamentsResponse.model_validate(response)

    def recent_tournaments(
        self,
        days: int | None = None,
        limit: int | None = None,
    ) -> RecentTournamentsResponse:
        """Get statistics for recent tournaments.

        Args:
            days: Number of days to look back
            limit: Number of tournaments to return

        Returns:
            Recent tournament statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            # Tournaments in last 30 days
            stats = client.stats.recent_tournaments(days=30, limit=50)
            for tournament in stats.tournaments:
                print(f"{tournament.tournament_name} ({tournament.days_ago} days ago)")
            ```
        """
        params = {}
        if days is not None:
            params["days"] = days
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/recent_tournaments", params=params)
        return RecentTournamentsResponse.model_validate(response)

    def machine_popularity(
        self,
        period: str | None = None,
        limit: int | str | None = None,
    ) -> MachinePopularityResponse:
        """Get machine/game popularity statistics.

        Args:
            period: Time period filter (e.g., "year", "all-time")
            limit: Number of machines to return

        Returns:
            Machine popularity statistics

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.machine_popularity(period="year", limit=25)
            for machine in stats.machines:
                print(f"{machine.rank}. {machine.machine_name}: {machine.usage_count} uses")
            ```
        """
        params: dict[str, Any] = {}
        if period is not None:
            params["period"] = period
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/machine_popularity", params=params)
        return MachinePopularityResponse.model_validate(response)

    def trends(
        self,
        metric: str,
        period: str | None = None,
    ) -> TrendsResponse:
        """Get trend statistics for a specific metric.

        Args:
            metric: Metric to analyze (e.g., "players", "tournaments", "wppr")
            period: Time period for trend analysis

        Returns:
            Trend data with time series points

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            trends = client.stats.trends(metric="players", period="year")
            print(f"Metric: {trends.metric}")
            print(f"Trend: {trends.trend_direction}")
            for point in trends.data_points:
                print(f"{point.date}: {point.value}")
            ```
        """
        params = {"metric": metric}
        if period is not None:
            params["period"] = period

        response = self._http._request("GET", "/stats/trends", params=params)
        return TrendsResponse.model_validate(response)

    def historical(
        self,
        start_year: int | None = None,
        end_year: int | None = None,
    ) -> HistoricalStatsResponse:
        """Get historical statistics by year.

        Args:
            start_year: Starting year for data
            end_year: Ending year for data

        Returns:
            Historical statistics year by year

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.historical(start_year=2010, end_year=2024)
            for year_stat in stats.stats:
                print(
                    f"{year_stat.year}: {year_stat.total_players} players, "
                    f"{year_stat.total_tournaments} tournaments"
                )
            ```
        """
        params = {}
        if start_year is not None:
            params["start_year"] = start_year
        if end_year is not None:
            params["end_year"] = end_year

        response = self._http._request("GET", "/stats/historical", params=params)
        return HistoricalStatsResponse.model_validate(response)

    def participation(
        self,
        category: str | None = None,
    ) -> ParticipationStatsResponse:
        """Get player participation statistics.

        Args:
            category: Participation category to analyze

        Returns:
            Participation statistics by category

        Raises:
            IfpaApiError: If the API request fails

        Example:
            ```python
            stats = client.stats.participation()
            for category in stats.stats:
                print(
                    f"{category.category}: {category.player_count} players "
                    f"({category.percentage}%)"
                )
            ```
        """
        params = {}
        if category is not None:
            params["category"] = category

        response = self._http._request("GET", "/stats/participation", params=params)
        return ParticipationStatsResponse.model_validate(response)
