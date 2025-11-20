# Stats

The Stats resource provides access to IFPA statistical data including geographic player distributions, tournament metrics, historical trends, player activity over time periods, and overall IFPA system statistics.

## Quick Example

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import CountryPlayersResponse

client: IfpaClient = IfpaClient()

# Get player counts by country
stats: CountryPlayersResponse = client.stats.country_players()
```

## Geographic Statistics

### Player Counts by Country

Get comprehensive player count statistics for all countries with registered IFPA players:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import CountryPlayersResponse

client: IfpaClient = IfpaClient()

# Get all countries with player counts (OPEN rankings)
stats: CountryPlayersResponse = client.stats.country_players(rank_type="OPEN")

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nTop 5 Countries by Player Count:")

for country in stats.stats[:5]:
    print(f"{country.stats_rank}. {country.country_name} ({country.country_code})")
    print(f"   {country.player_count} players")

# Output:
# Type: Players by Country
# Rank Type: OPEN
#
# Top 5 Countries by Player Count:
# 1. United States (US)
#    47101 players
# 2. Canada (CA)
#    6890 players
# 3. United Kingdom (GB)
#    5021 players
```

You can also query women's rankings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import CountryPlayersResponse

client: IfpaClient = IfpaClient()

# Get women's rankings by country
women_stats: CountryPlayersResponse = client.stats.country_players(rank_type="WOMEN")

for country in women_stats.stats[:5]:
    print(f"{country.country_name}: {country.player_count} players")
```

### Player Counts by State/Province

Get player count statistics for North American states and provinces:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import StatePlayersResponse

client: IfpaClient = IfpaClient()

# Get all states with player counts
stats: StatePlayersResponse = client.stats.state_players(rank_type="OPEN")

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nTop 5 States/Provinces by Player Count:")

for state in stats.stats[:5]:
    print(f"{state.stats_rank}. {state.stateprov}")
    print(f"   {state.player_count} players")

# Filter to specific region via post-processing
west_coast = [s for s in stats.stats if s.stateprov in ["WA", "OR", "CA"]]
print(f"\nWest Coast States:")
for state in west_coast:
    print(f"  {state.stateprov}: {state.player_count} players")
```

### Tournament Counts by State/Province

Get detailed tournament statistics including counts and WPPR points awarded by state:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import StateTournamentsResponse

client: IfpaClient = IfpaClient()

# Get tournament statistics by state
stats: StateTournamentsResponse = client.stats.state_tournaments(rank_type="OPEN")

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nTop 5 States/Provinces by Tournament Activity:")

for state in stats.stats[:5]:
    print(f"{state.stats_rank}. {state.stateprov}")
    print(f"   Tournaments: {state.tournament_count}")
    print(f"   Total Points: {state.total_points_all}")
    print(f"   Tournament Value: {state.total_points_tournament_value}")
```

## Historical Trends

### Events by Year

Track yearly growth trends in international pinball competition:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import EventsByYearResponse

client: IfpaClient = IfpaClient()

# Get global events by year
stats: EventsByYearResponse = client.stats.events_by_year(rank_type="OPEN")

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nGlobal Tournament Activity (Most Recent 5 Years):")

for year in stats.stats[:5]:
    print(f"\n{year.year}:")
    print(f"  Tournaments: {year.tournament_count}")
    print(f"  Countries: {year.country_count}")
    print(f"  Players: {year.player_count}")

# Output:
# Type: Events Per Year
# Rank Type: OPEN
#
# Global Tournament Activity (Most Recent 5 Years):
#
# 2024:
#   Tournaments: 2847
#   Countries: 45
#   Players: 41203
```

You can filter by country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import EventsByYearResponse

client: IfpaClient = IfpaClient()

# Get US-specific tournament data by year
us_stats: EventsByYearResponse = client.stats.events_by_year(
    rank_type="OPEN",
    country_code="US"
)

for year in us_stats.stats[:5]:
    print(f"{year.year}: {year.tournament_count} tournaments, {year.player_count} players")
```

### Players by Year

Track player retention across multiple years to analyze community growth and retention:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import PlayersByYearResponse

client: IfpaClient = IfpaClient()

# Get player retention statistics
stats: PlayersByYearResponse = client.stats.players_by_year()

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nPlayer Retention Analysis (Most Recent 5 Years):")

for year in stats.stats[:5]:
    print(f"\n{year.year}:")
    print(f"  Active players: {year.current_year_count}")
    print(f"  Also active previous year: {year.previous_year_count}")
    print(f"  Also active 2 years prior: {year.previous_2_year_count}")

    # Calculate retention rate
    retention = (year.previous_year_count / year.current_year_count) * 100
    print(f"  Year-over-year retention: {retention:.1f}%")

# Output:
# Type: Players by Year
# Rank Type: OPEN
#
# Player Retention Analysis (Most Recent 5 Years):
#
# 2024:
#   Active players: 41203
#   Also active previous year: 27531
#   Also active 2 years prior: 21456
#   Year-over-year retention: 66.8%
```

## Tournament Rankings

### Largest Tournaments

Get the top 25 tournaments in IFPA history by player count:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import LargestTournamentsResponse

client: IfpaClient = IfpaClient()

# Get largest tournaments globally
stats: LargestTournamentsResponse = client.stats.largest_tournaments(rank_type="OPEN")

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nTop 10 Largest Tournaments in IFPA History:")

for tourney in stats.stats[:10]:
    print(f"{tourney.stats_rank}. {tourney.tournament_name} ({tourney.tournament_date})")
    print(f"   Event: {tourney.event_name}")
    print(f"   Players: {tourney.player_count}")
    print(f"   Location: {tourney.country_name}")

# Output:
# Type: Largest Tournaments
# Rank Type: OPEN
#
# Top 10 Largest Tournaments in IFPA History:
# 1. IFPA16 Main Tournament (2023-08-06)
#    Event: INDISC 2023
#    Players: 624
#    Location: United States
```

Filter by country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import LargestTournamentsResponse

client: IfpaClient = IfpaClient()

# Get largest US tournaments
us_stats: LargestTournamentsResponse = client.stats.largest_tournaments(
    rank_type="OPEN",
    country_code="US"
)
```

### Most Lucrative Tournaments

Get the top 25 tournaments by tournament value (WPPR rating), which correlates with competitive prestige:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import LucrativeTournamentsResponse

client: IfpaClient = IfpaClient()

# Get highest-value major tournaments
stats: LucrativeTournamentsResponse = client.stats.lucrative_tournaments(
    major="Y",
    rank_type="OPEN"
)

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"\nTop 10 Highest-Value Major Tournaments:")

for tourney in stats.stats[:10]:
    print(f"{tourney.stats_rank}. {tourney.tournament_name} ({tourney.tournament_date})")
    print(f"   Event: {tourney.event_name}")
    print(f"   Value: {tourney.tournament_value}")
    print(f"   Location: {tourney.country_name}")

# Output:
# Type: Lucrative Tournaments
# Rank Type: OPEN
#
# Top 10 Highest-Value Major Tournaments:
# 1. IFPA World Championship (2024-04-12)
#    Event: IFPA20 Main
#    Value: 422.84
#    Location: United States
```

Compare major vs non-major tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import LucrativeTournamentsResponse

client: IfpaClient = IfpaClient()

# Get highest-value major tournaments
major: LucrativeTournamentsResponse = client.stats.lucrative_tournaments(major="Y")

# Get highest-value non-major tournaments
non_major: LucrativeTournamentsResponse = client.stats.lucrative_tournaments(major="N")

print("Major Tournaments:")
for t in major.stats[:3]:
    print(f"  {t.tournament_name}: {t.tournament_value}")

print("\nNon-Major Tournaments:")
for t in non_major.stats[:3]:
    print(f"  {t.tournament_name}: {t.tournament_value}")
```

## Player Activity Over Time

### Top Point Earners (Period)

Get players with the most accumulated WPPR points over a specific time period:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import PointsGivenPeriodResponse

client: IfpaClient = IfpaClient()

# Get top point earners for 2024
stats: PointsGivenPeriodResponse = client.stats.points_given_period(
    rank_type="OPEN",
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=25
)

print(f"Type: {stats.type}")
print(f"Rank Type: {stats.rank_type}")
print(f"Period: {stats.start_date} to {stats.end_date}")
print(f"Results: {stats.return_count}")
print(f"\nTop 10 Point Earners in 2024:")

for player in stats.stats[:10]:
    print(f"{player.stats_rank}. {player.first_name} {player.last_name}")
    print(f"   WPPR Points: {player.wppr_points}")
    print(f"   Location: {player.city}, {player.stateprov}, {player.country_name}")

# Output:
# Type: Points Given - Time Period
# Rank Type: OPEN
# Period: 2024-01-01 to 2024-12-31
# Results: 25
#
# Top 10 Point Earners in 2024:
# 1. Raymond Davidson
#    WPPR Points: 1234.56
#    Location: Portland, OR, United States
```

Filter by country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import PointsGivenPeriodResponse

client: IfpaClient = IfpaClient()

# Get top US point earners for 2024
us_stats: PointsGivenPeriodResponse = client.stats.points_given_period(
    rank_type="OPEN",
    country_code="US",
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=10
)

for player in us_stats.stats:
    print(f"{player.first_name} {player.last_name}: {player.wppr_points} pts")
```

### Most Active Players (Period)

Get players who attended the most tournaments during a specific time period:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import EventsAttendedPeriodResponse

client: IfpaClient = IfpaClient()

# Get most active players in 2024
stats: EventsAttendedPeriodResponse = client.stats.events_attended_period(
    rank_type="OPEN",
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=25
)

print(f"Type: {stats.type}")
print(f"Period: {stats.start_date} to {stats.end_date}")
print(f"Results: {stats.return_count}")
print(f"\nTop 10 Most Active Players in 2024:")

for player in stats.stats[:10]:
    name = f"{player.first_name} {player.last_name}"
    print(f"{player.stats_rank}. {name}")
    print(f"   Tournaments: {player.tournament_count}")
    print(f"   Location: {player.city}, {player.stateprov}")

# Output:
# Type: Events Attended - Time Period
# Period: 2024-01-01 to 2024-12-31
# Results: 25
#
# Top 10 Most Active Players in 2024:
# 1. Erik Thoren
#    Tournaments: 156
#    Location: De Pere, WI
```

Filter by country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import EventsAttendedPeriodResponse

client: IfpaClient = IfpaClient()

# Get most active US players in 2024
us_stats: EventsAttendedPeriodResponse = client.stats.events_attended_period(
    rank_type="OPEN",
    country_code="US",
    start_date="2024-01-01",
    end_date="2024-12-31",
    limit=10
)
```

## Overall IFPA Statistics

Get comprehensive aggregate statistics about the entire IFPA system:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import OverallStatsResponse

client: IfpaClient = IfpaClient()

# Get overall IFPA statistics
stats: OverallStatsResponse = client.stats.overall(system_code="OPEN")

print(f"Type: {stats.type}")
print(f"System Code: {stats.system_code}")
print(f"\n=== Player Statistics ===")
print(f"Total players: {stats.stats.overall_player_count:,}")
print(f"Active players (last 2 years): {stats.stats.active_player_count:,}")

print(f"\n=== Tournament Statistics ===")
print(f"Total tournaments: {stats.stats.tournament_count:,}")
print(f"Tournaments this year: {stats.stats.tournament_count_this_year:,}")
print(f"Tournaments last month: {stats.stats.tournament_count_last_month:,}")
print(f"Total tournament players: {stats.stats.tournament_player_count:,}")
print(f"Avg players/tournament: {stats.stats.tournament_player_count_average:.2f}")

print(f"\n=== Age Distribution ===")
age = stats.stats.age
print(f"Under 18: {age.age_under_18:.1f}%")
print(f"18-29: {age.age_18_to_29:.1f}%")
print(f"30-39: {age.age_30_to_39:.1f}%")
print(f"40-49: {age.age_40_to_49:.1f}%")
print(f"50+: {age.age_50_to_99:.1f}%")

# Output:
# Type: Overall Stats
# System Code: OPEN
#
# === Player Statistics ===
# Total players: 123,456
# Active players (last 2 years): 45,678
#
# === Tournament Statistics ===
# Total tournaments: 67,890
# Tournaments this year: 2,847
# Tournaments last month: 234
# Total tournament players: 234,567
# Avg players/tournament: 18.45
#
# === Age Distribution ===
# Under 18: 2.3%
# 18-29: 18.7%
# 30-39: 28.4%
# 40-49: 31.2%
# 50+: 19.4%
```

!!! warning "API Bug: Women's System Code"
    As of 2025-11-19, the API has a bug where `system_code="WOMEN"` returns OPEN data.
    The API always returns `system_code="OPEN"` regardless of the parameter value.
    This is an API limitation, not a client issue.

## Complete Example: Tournament Trends Report

Here's a complete example that analyzes tournament trends across multiple dimensions:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.stats import (
    EventsByYearResponse,
    LargestTournamentsResponse,
    OverallStatsResponse,
    StatePlayersResponse,
)


def generate_tournament_trends_report() -> None:
    """Generate comprehensive tournament trends report."""
    client: IfpaClient = IfpaClient()

    try:
        print("=" * 80)
        print("IFPA TOURNAMENT TRENDS REPORT")
        print("=" * 80)

        # Overall statistics
        overall: OverallStatsResponse = client.stats.overall()
        print(f"\n=== Overall System Statistics ===")
        print(f"Total Players: {overall.stats.overall_player_count:,}")
        print(f"Total Tournaments: {overall.stats.tournament_count:,}")
        print(f"Tournaments This Year: {overall.stats.tournament_count_this_year:,}")
        print(f"Avg Players/Tournament: {overall.stats.tournament_player_count_average:.1f}")

        # Historical growth trend
        events: EventsByYearResponse = client.stats.events_by_year()
        print(f"\n=== Historical Growth (Last 5 Years) ===")
        for year in events.stats[:5]:
            print(f"{year.year}:")
            print(f"  Tournaments: {year.tournament_count:,}")
            print(f"  Players: {year.player_count:,}")
            print(f"  Countries: {year.country_count}")

        # Calculate year-over-year growth
        if len(events.stats) >= 2:
            recent = events.stats[0]
            previous = events.stats[1]
            tournament_growth = (
                (recent.tournament_count - previous.tournament_count)
                / previous.tournament_count * 100
            )
            player_growth = (
                (recent.player_count - previous.player_count)
                / previous.player_count * 100
            )
            print(f"\n=== Year-over-Year Growth ===")
            print(f"Tournament growth: {tournament_growth:+.1f}%")
            print(f"Player growth: {player_growth:+.1f}%")

        # Geographic distribution
        states: StatePlayersResponse = client.stats.state_players()
        print(f"\n=== Top 10 States/Provinces by Player Count ===")
        for state in states.stats[:10]:
            print(f"{state.stats_rank:2d}. {state.stateprov}: {state.player_count:,} players")

        # Largest tournaments
        largest: LargestTournamentsResponse = client.stats.largest_tournaments()
        print(f"\n=== Top 5 Largest Tournaments ===")
        for tourney in largest.stats[:5]:
            print(f"{tourney.stats_rank}. {tourney.tournament_name} ({tourney.tournament_date})")
            print(f"   {tourney.player_count} players - {tourney.country_name}")

        print(f"\n" + "=" * 80)

    except IfpaApiError as e:
        print(f"API Error: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")


if __name__ == "__main__":
    generate_tournament_trends_report()
```

## Best Practices

### Date Formats

Always use ISO 8601 date format (YYYY-MM-DD) for date parameters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import PointsGivenPeriodResponse

client: IfpaClient = IfpaClient()

# Correct date format
stats: PointsGivenPeriodResponse = client.stats.points_given_period(
    start_date="2024-01-01",  # ISO 8601 format
    end_date="2024-12-31",
    limit=10
)

# Incorrect - will cause errors
# stats = client.stats.points_given_period(
#     start_date="01/01/2024",  # Wrong format
#     end_date="12/31/2024",
# )
```

### Error Handling

Always handle potential API errors:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.stats import CountryPlayersResponse

client: IfpaClient = IfpaClient()

try:
    stats: CountryPlayersResponse = client.stats.country_players()
    print(f"Found {len(stats.stats)} countries")
except IfpaApiError as e:
    print(f"API error: {e}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
```

### Type Coercion

The API returns many count fields as strings. The SDK automatically coerces these to appropriate numeric types (int, float, Decimal):

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import StateTournamentsResponse
from decimal import Decimal

client: IfpaClient = IfpaClient()

stats: StateTournamentsResponse = client.stats.state_tournaments()

# These are already coerced to proper types
for state in stats.stats[:3]:
    assert isinstance(state.tournament_count, int)
    assert isinstance(state.total_points_all, Decimal)
    assert isinstance(state.total_points_tournament_value, Decimal)
```

### Caching Results

For frequently accessed statistical data, consider caching to reduce API calls:

```python
from functools import lru_cache
from ifpa_api import IfpaClient
from ifpa_api.models.stats import CountryPlayersResponse


@lru_cache(maxsize=10)
def get_cached_country_stats(rank_type: str = "OPEN") -> CountryPlayersResponse:
    """Get country statistics with caching."""
    client: IfpaClient = IfpaClient()
    return client.stats.country_players(rank_type=rank_type)


# First call fetches from API
stats: CountryPlayersResponse = get_cached_country_stats("OPEN")

# Subsequent calls use cache
stats: CountryPlayersResponse = get_cached_country_stats("OPEN")  # Instant
```

## Known Limitations

### API String Coercion

Many stats endpoints return numeric fields as strings. The SDK automatically handles this conversion, but you should be aware:

- **Count fields** (player_count, tournament_count): Converted to `int`
- **Point fields** (wppr_points, total_points): Converted to `Decimal`
- **Value fields** (tournament_value): Converted to `float`

### Women's System Code Bug

The `overall()` endpoint has a known API bug where `system_code="WOMEN"` returns OPEN data. The API always returns `system_code="OPEN"` regardless of the parameter value.

### Empty Period Results

When querying period-based endpoints (`points_given_period`, `events_attended_period`), empty results are valid if no tournaments occurred in the specified date range:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.stats import PointsGivenPeriodResponse

client: IfpaClient = IfpaClient()

# May return empty stats array if no tournaments in range
stats: PointsGivenPeriodResponse = client.stats.points_given_period(
    start_date="2010-01-01",
    end_date="2010-01-02"
)

if stats.return_count == 0:
    print("No results for this period")
else:
    print(f"Found {stats.return_count} results")
```

## API Coverage

The Stats resource provides access to all 10 statistical endpoints in the IFPA API v2.1:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/stats/country_players` | `country_players()` | Player counts by country |
| `/stats/state_players` | `state_players()` | Player counts by state/province (North America) |
| `/stats/state_tournaments` | `state_tournaments()` | Tournament counts and points by state |
| `/stats/events_by_year` | `events_by_year()` | Historical tournament trends by year |
| `/stats/players_by_year` | `players_by_year()` | Player retention metrics by year |
| `/stats/largest_tournaments` | `largest_tournaments()` | Top 25 tournaments by player count |
| `/stats/lucrative_tournaments` | `lucrative_tournaments()` | Top 25 tournaments by WPPR value |
| `/stats/points_given_period` | `points_given_period()` | Top point earners in date range |
| `/stats/events_attended_period` | `events_attended_period()` | Most active players in date range |
| `/stats/overall` | `overall()` | Overall IFPA system statistics |

All endpoints were verified operational as of 2025-11-19.

## Related Resources

- [Rankings](rankings.md) - View current player rankings
- [Tournaments](tournaments.md) - View tournament details and results
- [Players](players.md) - View player profiles and history
- [Error Handling](../guides/error-handling.md) - Handle API errors
- [Exceptions Reference](../api-client-reference/exceptions.md) - Exception types
