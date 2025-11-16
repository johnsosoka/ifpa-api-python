# Series

Access tournament series information, standings, player cards, and regional data using the callable pattern: `client.series("CODE").method()`.

## List All Series

List all available tournament series, optionally filtering to active series only.

```python
# Quick example
series_list = client.series.list(active_only=True)
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `active_only` | `bool` | No | Filter to only active series |

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesListResponse

client = IfpaClient()

# List all series
all_series: SeriesListResponse = client.series.list()
for series in all_series.series:
    print(f"{series.series_code}: {series.series_name}")
    if series.active:
        print(f"  Active: {series.active}")

# Filter to active series only
active_series: SeriesListResponse = client.series.list(active_only=True)
print(f"\nFound {len(active_series.series)} active series")
```

## Get Overall Series Standings

Get overall standings overview for a series across all regions. This returns a summary of each region with current leader and prize fund information.

```python
# Quick example - NACS (North American Championship Series)
standings = client.series("NACS").standings()
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_pos` | `int` | No | Starting position for pagination (currently unused by API) |
| `count` | `int` | No | Number of results to return (currently unused by API) |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesStandingsResponse

# Get overall standings overview for all regions
standings: SeriesStandingsResponse = client.series("NACS").standings()

print(f"Series: {standings.series_code} ({standings.year})")
print(f"Total Prize Fund: ${standings.championship_prize_fund}")

# Show top 5 regions
for region in standings.overall_results[:5]:
    print(f"\n{region.region_name}: {region.player_count} players")
    print(f"  Leader: {region.current_leader['player_name']}")
    print(f"  Prize Fund: ${region.prize_fund}")
```

## Get Region-Specific Standings

Get detailed player standings for a specific region in a series.

```python
# Quick example - Ohio region in NACS
standings = client.series("NACS").region_standings("OH")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |
| `start_pos` | `int` | No | Starting position for pagination |
| `count` | `int` | No | Number of results to return |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesRegionStandingsResponse

# Get detailed standings for Ohio region
standings: SeriesRegionStandingsResponse = client.series("NACS").region_standings("OH")

print(f"Region: {standings.region_name}")
print(f"Prize Fund: ${standings.prize_fund}")
print(f"Total Players: {len(standings.standings)}")

# Show top 10 players
for player in standings.standings[:10]:
    print(f"{player.series_rank}. {player.player_name}: {player.wppr_points} pts")
    print(f"  Events: {player.event_count} | Wins: {player.win_count}")

# Paginated region standings (50 results starting from position 0)
standings_page: SeriesRegionStandingsResponse = client.series("NACS").region_standings(
    region_code="OH",
    start_pos=0,
    count=50
)
```

## Get Player's Series Card

Get a player's performance card for a specific series and region.

```python
# Quick example - Josh Sharpe (Player 14) in Ohio
card = client.series("NACS").player_card(14, "OH")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `player_id` | `int \| str` | Yes | The player's unique identifier |
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL") |
| `year` | `int` | No | Year to fetch card for (defaults to current year) |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesPlayerCard

# Get current year card for Josh Sharpe in Ohio region
card: SeriesPlayerCard = client.series("NACS").player_card(
    player_id=14,  # Josh Sharpe
    region_code="OH"
)

print(f"Player: {card.player_name}")
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")
print(f"\nEvent History:")

# Show all events on player's card
for event in card.player_card:
    print(f"  {event.tournament_name}: {event.wppr_points} pts")
    if event.region_event_rank:
        print(f"    Rank: {event.region_event_rank}")

# Get card for specific year (2023)
card_2023: SeriesPlayerCard = client.series("NACS").player_card(
    player_id=14,
    region_code="OH",
    year=2023
)
print(f"\n2023 Card: {len(card_2023.player_card)} events")
```

## Get Active Regions

Get list of active regions in a series for a specific year.

```python
# Quick example - Get 2024 NACS regions
regions = client.series("NACS").regions("OH", 2024)
```

!!! note "API Behavior"
    The `region_code` parameter is required by the API but the endpoint returns all
    active regions for the year regardless of the `region_code` value provided.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (required by API but not used for filtering) |
| `year` | `int` | Yes | Year to fetch regions for |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesRegionsResponse

# Get all active regions for 2024 (region_code is required but not used for filtering)
regions: SeriesRegionsResponse = client.series("NACS").regions("OH", 2024)

print(f"Active Regions for 2024:")
for region in regions.active_regions:
    print(f"  {region.region_name} ({region.region_code})")
    if region.player_count:
        print(f"    Players: {region.player_count}")
    if region.event_count:
        print(f"    Events: {region.event_count}")
```

## Get Series Statistics

Get aggregate statistics for a specific region in a series.

```python
# Quick example - Ohio region stats
stats = client.series("NACS").stats("OH")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesStats

# Get statistics for Ohio region in NACS
stats: SeriesStats = client.series("NACS").stats("OH")

print(f"Ohio Region Statistics:")
print(f"  Total Events: {stats.total_events}")
print(f"  Total Players: {stats.total_players}")
print(f"  Total Participations: {stats.total_participations}")
print(f"  Average Event Size: {stats.average_event_size:.1f} players")
```

## Get Series Tournaments

Get tournaments for a specific region in a series.

```python
# Quick example - Ohio tournaments in NACS
tournaments = client.series("NACS").tournaments("OH")
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `region_code` | `str` | Yes | Region code (e.g., "OH", "IL", "CA") |

**Complete Example:**

```python
from ifpa_api.models.series import SeriesTournamentsResponse

# Get tournaments for Ohio region in NACS
tournaments: SeriesTournamentsResponse = client.series("NACS").tournaments("OH")

print(f"Ohio NACS Tournaments ({len(tournaments.tournaments)} total):")
for tournament in tournaments.tournaments[:10]:  # Show first 10
    print(f"\n{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
    if tournament.event_value:
        print(f"  Value: {tournament.event_value} WPPR points")
```

## Get Region Representatives

Get list of region representatives for a series.

```python
# Quick example - Get PAPA region reps
reps = client.series("PAPA").region_reps()
```

**Parameters:** None

**Complete Example:**

```python
from ifpa_api.models.series import RegionRepsResponse

# Get region representatives for PAPA series
reps: RegionRepsResponse = client.series("PAPA").region_reps()

print("PAPA Series Region Representatives:")
for rep in reps.representative:
    print(f"\n{rep.region_name} ({rep.region_code})")
    print(f"  Rep: {rep.name}")
    print(f"  Player ID: {rep.player_id}")
    if rep.profile_photo:
        print(f"  Photo: {rep.profile_photo}")
```

## Complete Example: Series Analysis

Here's a complete example analyzing a series across regions using real test data:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.series import (
    SeriesStandingsResponse,
    SeriesRegionStandingsResponse,
    SeriesStats,
)


def analyze_series(series_code: str, region_code: str) -> None:
    """Analyze a series and specific region.

    Args:
        series_code: Series code (e.g., "NACS", "PAPA")
        region_code: Region code (e.g., "OH", "IL")

    Example:
        analyze_series("NACS", "OH")
    """
    with IfpaClient() as client:
        try:
            # Get overall standings across all regions
            overall: SeriesStandingsResponse = client.series(series_code).standings()

            print(f"\n{'=' * 60}")
            print(f"{series_code} Series - {overall.year}")
            print(f"Championship Prize Fund: ${overall.championship_prize_fund:,}")
            print(f"{'=' * 60}")

            # Show top 5 regions
            print(f"\nTop 5 Regions ({len(overall.overall_results)} total):")
            for i, region in enumerate(overall.overall_results[:5], 1):
                print(f"\n{i}. {region.region_name}")
                print(f"   Players: {region.player_count}")
                print(f"   Leader: {region.current_leader['player_name']}")
                print(f"   Prize Fund: ${region.prize_fund:,}")

            # Get detailed region standings
            print(f"\n{'=' * 60}")
            print(f"{region_code} Region Detailed Standings")
            print(f"{'=' * 60}")

            region_standings: SeriesRegionStandingsResponse = (
                client.series(series_code).region_standings(region_code)
            )

            print(f"\nRegion: {region_standings.region_name}")
            print(f"Prize Fund: ${region_standings.prize_fund:,}")
            print(f"\nTop 10 Players:")

            for player in region_standings.standings[:10]:
                print(f"  {player.series_rank:3d}. {player.player_name:30s} "
                      f"{player.wppr_points:6.2f} pts "
                      f"({player.event_count} events, {player.win_count} wins)")

            # Get region statistics
            stats: SeriesStats = client.series(series_code).stats(region_code)

            print(f"\n{'=' * 60}")
            print(f"{region_code} Region Statistics")
            print(f"{'=' * 60}")
            print(f"  Total Events: {stats.total_events}")
            print(f"  Total Players: {stats.total_players}")
            print(f"  Total Participations: {stats.total_participations}")
            print(f"  Average Event Size: {stats.average_event_size:.1f} players")

        except IfpaApiError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Analyze NACS Ohio region (real test data)
    analyze_series("NACS", "OH")

    # You can also try:
    # analyze_series("PAPA", "OH")  # PAPA series in Ohio
    # analyze_series("NACS", "IL")  # NACS Illinois region
```

## Real Test Data Reference

All examples above use real, testable data from integration tests:

**Series Codes:**
- `NACS` - North American Championship Series
- `PAPA` - Professional and Amateur Pinball Association

**Player IDs:**
- `14` - Josh Sharpe (World #1, highly active)
- `25584` - Dwayne Smith (Rank #753, Idaho player)
- `47585` - Debbie Smith (Rank #7078, Idaho player)

**Region Codes:**
- `OH` - Ohio
- `IL` - Illinois
- `CA` - California

**Years:**
- `2024` - Current year data
- `2023` - Historical year data

All examples can be copied and run directly with a valid IFPA API key.

## Related Resources

- [Player](player.md) - View player profiles and results
- [Tournaments](tournaments.md) - Search and view tournament details
- [Rankings](rankings.md) - View player rankings
