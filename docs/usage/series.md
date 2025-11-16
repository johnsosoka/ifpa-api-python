# Series

Access tournament series information, standings, player cards, and regional data.

## List All Series

List all available tournament series, optionally filtering to active series only.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_only` | `bool` | No | Filter to only active series |

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesListResponse

client = IfpaClient()

# List all series
all_series: SeriesListResponse = client.series.list()
for series in all_series.series:
    print(f"{series.series_code}: {series.series_name}")

# Filter to active series only
active_series: SeriesListResponse = client.series.list(active_only=True)
```

## Get Overall Series Standings

Get overall standings overview for a series across all regions. This returns a summary
of each region with current leader and prize fund information.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_pos` | `int` | No | Starting position for pagination (currently unused by API) |
| `count` | `int` | No | Number of results to return (currently unused by API) |

```python
from ifpa_api.models.series import SeriesStandingsResponse

# Get overall standings overview for all regions
standings: SeriesStandingsResponse = client.series_handle("NACS").standings()

print(f"Series: {standings.series_code} ({standings.year})")
print(f"Total Prize Fund: ${standings.championship_prize_fund}")

for region in standings.overall_results:
    print(f"{region.region_name}: {region.player_count} players")
    print(f"  Leader: {region.current_leader['player_name']}")
    print(f"  Prize Fund: ${region.prize_fund}")
```

## Get Region-Specific Standings

Get detailed player standings for a specific region in a series.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |
| `start_pos` | `int` | No | Starting position for pagination |
| `count` | `int` | No | Number of results to return |

```python
from ifpa_api.models.series import SeriesRegionStandingsResponse

# Get detailed standings for Ohio region
standings: SeriesRegionStandingsResponse = client.series_handle("NACS").region_standings("OH")

print(f"Region: {standings.region_name}")
print(f"Prize Fund: ${standings.prize_fund}")

for player in standings.standings[:10]:
    print(f"{player.series_rank}. {player.player_name}: {player.wppr_points} pts")
    print(f"  Events: {player.event_count} | Wins: {player.win_count}")

# Paginated region standings
standings_page: SeriesRegionStandingsResponse = client.series_handle("NACS").region_standings(
    region_code="OH",
    start_pos=0,
    count=50
)
```

## Get Player's Series Card

Get a player's performance card for a specific series and region.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `player_id` | `int \| str` | Yes | The player's unique identifier |
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL") |
| `year` | `int` | No | Year to fetch card for (defaults to current year) |

```python
from ifpa_api.models.series import SeriesPlayerCard

# Get current year card for player in Ohio region
card: SeriesPlayerCard = client.series_handle("PAPA").player_card(
    player_id=12345,
    region_code="OH"
)

print(f"Player: {card.player_name}")
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")

for event in card.player_card:
    print(f"{event.tournament_name}: {event.wppr_points} pts")
    if event.region_event_rank:
        print(f"  Rank: {event.region_event_rank}")

# Get card for specific year
card_2023: SeriesPlayerCard = client.series_handle("PAPA").player_card(
    player_id=12345,
    region_code="OH",
    year=2023
)
```

## Get Active Regions

Get list of active regions in a series for a specific year.

!!! note "API Behavior"
    The `region_code` parameter is required by the API but the endpoint returns all
    active regions for the year regardless of the `region_code` value provided.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (required by API but not used for filtering) |
| `year` | `int` | Yes | Year to fetch regions for |

```python
from ifpa_api.models.series import SeriesRegionsResponse

# Get all active regions for 2025
regions: SeriesRegionsResponse = client.series_handle("NACS").regions("OH", 2025)

for region in regions.active_regions:
    print(f"{region.region_name} ({region.region_code})")
    if region.player_count:
        print(f"  Players: {region.player_count}")
    if region.event_count:
        print(f"  Events: {region.event_count}")
```

## Get Series Statistics

Get aggregate statistics for a specific region in a series.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |

```python
from ifpa_api.models.series import SeriesStats

# Get statistics for Ohio region
stats: SeriesStats = client.series_handle("NACS").stats("OH")

print(f"Total Events: {stats.total_events}")
print(f"Total Players: {stats.total_players}")
print(f"Total Participations: {stats.total_participations}")
print(f"Average Event Size: {stats.average_event_size}")
```

## Get Series Tournaments

Get tournaments for a specific region in a series.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |

```python
from ifpa_api.models.series import SeriesTournamentsResponse

# Get tournaments for Ohio region
tournaments: SeriesTournamentsResponse = client.series_handle("NACS").tournaments("OH")

for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
```

## Get Region Representatives

Get list of region representatives for a series.

**Parameters:** None

```python
from ifpa_api.models.series import RegionRepsResponse

# Get region representatives
reps: RegionRepsResponse = client.series_handle("PAPA").region_reps()

for rep in reps.representative:
    print(f"{rep.region_name} ({rep.region_code}): {rep.name}")
    print(f"  Player ID: {rep.player_id}")
    if rep.profile_photo:
        print(f"  Photo: {rep.profile_photo}")
```

## Complete Example: Series Analysis

Here's a complete example analyzing a series across regions:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.series import (
    SeriesStandingsResponse,
    SeriesRegionStandingsResponse,
    SeriesStats,
)


def analyze_series(series_code: str, region_code: str) -> None:
    """Analyze a series and specific region."""
    with IfpaClient() as client:
        try:
            # Get overall standings
            overall: SeriesStandingsResponse = client.series_handle(series_code).standings()

            print(f"{series_code} Series - {overall.year}")
            print(f"Championship Prize Fund: ${overall.championship_prize_fund}")
            print(f"\nRegions ({len(overall.overall_results)}):")

            for region in overall.overall_results[:5]:
                print(f"  {region.region_name}: {region.player_count} players")
                print(f"    Leader: {region.current_leader['player_name']}")

            # Get detailed region standings
            region_standings: SeriesRegionStandingsResponse = (
                client.series_handle(series_code).region_standings(region_code)
            )

            print(f"\n{region_standings.region_name} Region Standings:")
            for player in region_standings.standings[:10]:
                print(f"  {player.series_rank}. {player.player_name}: {player.wppr_points} pts")

            # Get region statistics
            stats: SeriesStats = client.series_handle(series_code).stats(region_code)

            print(f"\n{region_code} Region Statistics:")
            print(f"  Total Events: {stats.total_events}")
            print(f"  Total Players: {stats.total_players}")
            print(f"  Average Event Size: {stats.average_event_size:.1f}")

        except IfpaApiError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    analyze_series("NACS", "OH")
```

## Related Resources

- [Tournaments](tournaments.md) - Search and view tournament details
- [Players](players.md) - View player profiles and results
- [Rankings](rankings.md) - View player rankings
