"""Stats resource client.

Provides access to IFPA statistical data including country/state player counts,
tournament metrics, player activity over time periods, and overall IFPA statistics.
"""

from typing import Any

from ifpa_api.core.base import BaseResourceClient
from ifpa_api.models.common import MajorTournament, StatsRankType, SystemCode
from ifpa_api.models.stats import (
    CountryPlayersResponse,
    EventsAttendedPeriodResponse,
    EventsByYearResponse,
    LargestTournamentsResponse,
    LucrativeTournamentsResponse,
    OverallStatsResponse,
    PlayersByYearResponse,
    PointsGivenPeriodResponse,
    StatePlayersResponse,
    StateTournamentsResponse,
)

# ============================================================================
# Stats Resource Client - IFPA Statistical Data Access
# ============================================================================


class StatsClient(BaseResourceClient):
    """Client for IFPA statistical data queries.

    This client provides access to various statistical endpoints maintained by IFPA,
    including player counts by region, tournament metrics, historical trends,
    and overall system statistics.

    All endpoints were verified operational as of 2025-11-19. Note that many count
    fields are returned as strings by the API and are automatically coerced to
    integers/decimals by the Pydantic models.

    Attributes:
        _http: The HTTP client instance
        _validate_requests: Whether to validate request parameters
    """

    def country_players(self, rank_type: StatsRankType | str = "OPEN") -> CountryPlayersResponse:
        """Get player count statistics by country.

        Returns comprehensive list of all countries with registered players,
        sorted by player count descending.

        Args:
            rank_type: Ranking type - "OPEN" for all players or "WOMEN" for
                women's rankings. Accepts StatsRankType enum or string. Defaults to "OPEN".

        Returns:
            CountryPlayersResponse with player counts for each country.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get all countries with player counts (using enum)
            stats = client.stats.country_players(rank_type=StatsRankType.OPEN)
            for country in stats.stats[:5]:
                print(f"{country.country_name}: {country.player_count} players")

            # Get women's rankings by country (using string for backwards compatibility)
            women_stats = client.stats.country_players(rank_type="WOMEN")
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value

        response = self._http._request("GET", "/stats/country_players", params=params)
        return CountryPlayersResponse.model_validate(response)

    def state_players(self, rank_type: StatsRankType | str = "OPEN") -> StatePlayersResponse:
        """Get player count statistics by state/province.

        Returns player counts for North American states and provinces. Includes
        an "Unknown" entry for players without location data.

        Args:
            rank_type: Ranking type - "OPEN" for all players or "WOMEN" for
                women's rankings. Accepts StatsRankType enum or string. Defaults to "OPEN".

        Returns:
            StatePlayersResponse with player counts for each state/province.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get all states with player counts
            stats = client.stats.state_players(rank_type=StatsRankType.OPEN)
            for state in stats.stats[:5]:
                print(f"{state.stateprov}: {state.player_count} players")

            # Filter to specific region via post-processing
            west_coast = [s for s in stats.stats if s.stateprov in ["WA", "OR", "CA"]]
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value

        response = self._http._request("GET", "/stats/state_players", params=params)
        return StatePlayersResponse.model_validate(response)

    def state_tournaments(
        self, rank_type: StatsRankType | str = "OPEN"
    ) -> StateTournamentsResponse:
        """Get tournament count and points statistics by state/province.

        Returns detailed financial/points analysis by state including total
        WPPR points awarded and tournament values.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".

        Returns:
            StateTournamentsResponse with tournament counts and point totals.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get tournament statistics by state
            stats = client.stats.state_tournaments(rank_type=StatsRankType.OPEN)
            for state in stats.stats[:5]:
                print(f"{state.stateprov}: {state.tournament_count} tournaments")
                print(f"  Total Points: {state.total_points_all}")
                print(f"  Tournament Value: {state.total_points_tournament_value}")
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value

        response = self._http._request("GET", "/stats/state_tournaments", params=params)
        return StateTournamentsResponse.model_validate(response)

    def events_by_year(
        self,
        rank_type: StatsRankType | str = "OPEN",
        country_code: str | None = None,
    ) -> EventsByYearResponse:
        """Get statistics about number of events per year.

        Shows yearly growth trends in international pinball competition including
        country participation, tournament counts, and player activity.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".
            country_code: Optional country code to filter by (e.g., "US", "CA").

        Returns:
            EventsByYearResponse with yearly statistics, sorted by year descending.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get global events by year
            stats = client.stats.events_by_year(rank_type=StatsRankType.OPEN)
            for year in stats.stats[:5]:
                print(f"{year.year}: {year.tournament_count} tournaments")
                print(f"  Countries: {year.country_count}")
                print(f"  Players: {year.player_count}")

            # Get US-specific data
            us_stats = client.stats.events_by_year(country_code="US")
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value
        if country_code is not None:
            params["country_code"] = country_code

        response = self._http._request("GET", "/stats/events_by_year", params=params)
        return EventsByYearResponse.model_validate(response)

    def players_by_year(self) -> PlayersByYearResponse:
        """Get statistics about number of players per year.

        This unique endpoint tracks player retention across multiple years,
        showing how many players were active in consecutive years. Great for
        analyzing player retention trends.

        Returns:
            PlayersByYearResponse with yearly player retention statistics.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            # Get player retention statistics
            stats = client.stats.players_by_year()
            for year in stats.stats[:5]:
                print(f"{year.year}:")
                print(f"  Current year: {year.current_year_count} players")
                print(f"  Also active previous year: {year.previous_year_count}")
                print(f"  Also active 2 years prior: {year.previous_2_year_count}")

            # Calculate retention rate
            recent = stats.stats[0]
            retention = (recent.previous_year_count / recent.current_year_count) * 100
            print(f"Year-over-year retention: {retention:.1f}%")
            ```
        """
        response = self._http._request("GET", "/stats/players_by_year")
        return PlayersByYearResponse.model_validate(response)

    def largest_tournaments(
        self,
        rank_type: StatsRankType | str = "OPEN",
        country_code: str | None = None,
    ) -> LargestTournamentsResponse:
        """Get top 25 tournaments by player count.

        Returns the largest tournaments in IFPA history, sorted by number of
        participants.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".
            country_code: Optional country code to filter by (e.g., "US", "CA").

        Returns:
            LargestTournamentsResponse with top 25 tournaments by player count.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get largest tournaments globally
            stats = client.stats.largest_tournaments(rank_type=StatsRankType.OPEN)
            for tourney in stats.stats[:10]:
                print(f"{tourney.tournament_name} ({tourney.tournament_date})")
                print(f"  {tourney.player_count} players")
                print(f"  {tourney.country_name}")

            # Get largest US tournaments
            us_stats = client.stats.largest_tournaments(country_code="US")
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value
        if country_code is not None:
            params["country_code"] = country_code

        response = self._http._request("GET", "/stats/largest_tournaments", params=params)
        return LargestTournamentsResponse.model_validate(response)

    def lucrative_tournaments(
        self,
        rank_type: StatsRankType | str = "OPEN",
        major: MajorTournament | str = "Y",
        country_code: str | None = None,
    ) -> LucrativeTournamentsResponse:
        """Get top 25 tournaments by tournament value (WPPR rating).

        Returns the highest-value tournaments, which typically correlate with
        the most competitive and prestigious events.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".
            major: Filter by major tournament status - "Y" for major tournaments
                only (default), "N" for non-major tournaments. Accepts MajorTournament
                enum or string.
            country_code: Optional country code to filter by (e.g., "US", "CA").

        Returns:
            LucrativeTournamentsResponse with top 25 tournaments by value.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType, MajorTournament

            # Get highest-value major tournaments (using enums)
            stats = client.stats.lucrative_tournaments(
                rank_type=StatsRankType.OPEN,
                major=MajorTournament.YES
            )
            for tourney in stats.stats[:10]:
                print(f"{tourney.tournament_name} ({tourney.tournament_date})")
                print(f"  Value: {tourney.tournament_value}")
                print(f"  {tourney.country_name}")

            # Get highest-value non-major tournaments (using strings)
            non_major = client.stats.lucrative_tournaments(major="N")

            # Filter by country
            us_major = client.stats.lucrative_tournaments(country_code="US")
            ```
        """
        # Extract enum values if enums passed, otherwise use strings directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type
        major_value = major.value if isinstance(major, MajorTournament) else major

        params: dict[str, Any] = {}
        if major_value != "Y":
            params["major"] = major_value
        if rank_value != "OPEN":
            params["rank_type"] = rank_value
        if country_code is not None:
            params["country_code"] = country_code

        response = self._http._request("GET", "/stats/lucrative_tournaments", params=params)
        return LucrativeTournamentsResponse.model_validate(response)

    def points_given_period(
        self,
        rank_type: StatsRankType | str = "OPEN",
        country_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> PointsGivenPeriodResponse:
        """Get players with total accumulative points over a time period.

        Returns top point earners for a date range, useful for identifying
        the most successful players during specific time windows.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".
            country_code: Optional country code to filter by (e.g., "US", "CA").
            start_date: Start date in YYYY-MM-DD format. If not provided, API
                uses a default lookback period.
            end_date: End date in YYYY-MM-DD format. If not provided, API uses
                current date.
            limit: Maximum number of results to return. API default applies if
                not specified.

        Returns:
            PointsGivenPeriodResponse with top point earners for the period.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get top point earners for 2024
            stats = client.stats.points_given_period(
                rank_type=StatsRankType.OPEN,
                start_date="2024-01-01",
                end_date="2024-12-31",
                limit=25
            )
            for player in stats.stats:
                print(f"{player.first_name} {player.last_name}: {player.wppr_points} pts")

            # Get top US point earners
            us_stats = client.stats.points_given_period(
                country_code="US",
                start_date="2024-01-01",
                limit=10
            )
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value
        if country_code is not None:
            params["country_code"] = country_code
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/points_given_period", params=params)
        return PointsGivenPeriodResponse.model_validate(response)

    def events_attended_period(
        self,
        rank_type: StatsRankType | str = "OPEN",
        country_code: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int | None = None,
    ) -> EventsAttendedPeriodResponse:
        """Get players with total accumulative events over a time period.

        Returns most active players by tournament attendance for a date range,
        useful for identifying the most dedicated competitors.

        Args:
            rank_type: Ranking type - "OPEN" for all tournaments or "WOMEN" for
                women's tournaments. Accepts StatsRankType enum or string. Defaults to "OPEN".
            country_code: Optional country code to filter by (e.g., "US", "CA").
            start_date: Start date in YYYY-MM-DD format. If not provided, API
                uses a default lookback period.
            end_date: End date in YYYY-MM-DD format. If not provided, API uses
                current date.
            limit: Maximum number of results to return. API default applies if
                not specified.

        Returns:
            EventsAttendedPeriodResponse with most active players for the period.

        Raises:
            IfpaApiError: If the API request fails.

        Example:
            ```python
            from ifpa_api import StatsRankType

            # Get most active players in 2024
            stats = client.stats.events_attended_period(
                rank_type=StatsRankType.OPEN,
                start_date="2024-01-01",
                end_date="2024-12-31",
                limit=25
            )
            for player in stats.stats:
                name = f"{player.first_name} {player.last_name}"
                print(f"{name}: {player.tournament_count} tournaments")

            # Get most active US players
            us_stats = client.stats.events_attended_period(
                country_code="US",
                start_date="2024-01-01",
                limit=10
            )
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        rank_value = rank_type.value if isinstance(rank_type, StatsRankType) else rank_type

        params: dict[str, Any] = {}
        if rank_value != "OPEN":
            params["rank_type"] = rank_value
        if country_code is not None:
            params["country_code"] = country_code
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if limit is not None:
            params["limit"] = limit

        response = self._http._request("GET", "/stats/events_attended_period", params=params)
        return EventsAttendedPeriodResponse.model_validate(response)

    def overall(self, system_code: SystemCode | str = "OPEN") -> OverallStatsResponse:
        """Get overall WPPR system statistics.

        Returns aggregate statistics about the entire IFPA system including
        total player counts, tournament counts, and age distribution.

        Note that this endpoint returns proper numeric types (int/float) unlike
        other stats endpoints which return strings.

        Args:
            system_code: Ranking system - "OPEN" for open division or "WOMEN"
                for women's division. Accepts SystemCode enum or string. Defaults to "OPEN".

        Returns:
            OverallStatsResponse with comprehensive IFPA system statistics.

        Raises:
            IfpaApiError: If the API request fails.

        Note:
            As of 2025-11-19, the API appears to have a bug where system_code="WOMEN"
            returns OPEN data. This is an API limitation, not a client issue.

        Example:
            ```python
            from ifpa_api import SystemCode

            # Get overall IFPA statistics (using enum)
            stats = client.stats.overall(system_code=SystemCode.OPEN)
            print(f"Total players: {stats.stats.overall_player_count}")
            print(f"Active players: {stats.stats.active_player_count}")
            print(f"Total tournaments: {stats.stats.tournament_count}")
            print(f"Tournaments this year: {stats.stats.tournament_count_this_year}")
            print(f"Avg players/tournament: {stats.stats.tournament_player_count_average}")

            # Age distribution
            age = stats.stats.age
            print(f"Under 18: {age.age_under_18}%")
            print(f"18-29: {age.age_18_to_29}%")
            print(f"30-39: {age.age_30_to_39}%")
            print(f"40-49: {age.age_40_to_49}%")
            print(f"50+: {age.age_50_to_99}%")
            ```
        """
        # Extract enum value if enum passed, otherwise use string directly
        system_value = system_code.value if isinstance(system_code, SystemCode) else system_code

        params: dict[str, Any] = {}
        if system_value != "OPEN":
            params["system_code"] = system_value

        response = self._http._request("GET", "/stats/overall", params=params)
        return OverallStatsResponse.model_validate(response)
