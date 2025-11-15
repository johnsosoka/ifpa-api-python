# Series

Access tournament series information, standings, and player performance.

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

## Get Series Standings

Get current standings for a specific series with optional pagination.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_pos` | `int` | No | Starting position for pagination |
| `count` | `int` | No | Number of results to return |

```python
from ifpa_api.models.series import SeriesStandingsResponse

# Get standings for a specific series
standings: SeriesStandingsResponse = client.series_handle("PAPA").standings(
    start_pos=0,
    count=50
)

for entry in standings.standings:
    print(f"{entry.position}. {entry.player_name}: {entry.points} points")
    print(f"  Events Played: {entry.events_played}")
    print(f"  Best Finish: {entry.best_finish}")
```

## Get Player's Series Card

Get a player's performance card for a specific series. Requires a region code and optionally accepts a year.

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
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")

for event in card.player_card:
    print(f"{event.tournament_name}: {event.wppr_points} pts")
    print(f"  Rank: {event.region_event_rank}")

# Get card for specific year
card_2023: SeriesPlayerCard = client.series_handle("PAPA").player_card(
    player_id=12345,
    region_code="OH",
    year=2023
)
```

## Get Series Overview

Get overview information and statistics for a series.

**Parameters:** None

```python
from ifpa_api.models.series import SeriesOverview

# Get series overview and statistics
overview: SeriesOverview = client.series_handle("PAPA").overview()
print(f"Series: {overview.series_name}")
print(f"Description: {overview.description}")
print(f"Total Events: {overview.total_events}")
print(f"Total Players: {overview.total_players}")
print(f"Start Date: {overview.start_date}")
print(f"End Date: {overview.end_date}")
```

## Get Series Regions

Get list of regions participating in a series with player and event counts.

**Parameters:** None

```python
from ifpa_api.models.series import SeriesRegionsResponse

# Get regions for a series
regions: SeriesRegionsResponse = client.series_handle("PAPA").regions()
for region in regions.regions:
    print(f"{region.region_name} ({region.region_code})")
    print(f"  Players: {region.player_count}")
    print(f"  Events: {region.event_count}")
```

## Get Series Rules

Get rules and scoring system information for a series.

**Parameters:** None

```python
from ifpa_api.models.series import SeriesRules

# Get series rules and scoring system
rules: SeriesRules = client.series_handle("PAPA").rules()
print(f"Series: {rules.series_name}")
print(f"Scoring System: {rules.scoring_system}")
print(f"Events Counted: {rules.events_counted}")
print(f"Eligibility: {rules.eligibility}")
print(f"\nRules:\n{rules.rules_text}")
```

## Get Series Statistics

Get aggregate statistics for a series including totals and averages.

**Parameters:** None

```python
from ifpa_api.models.series import SeriesStats

# Get series statistics
stats: SeriesStats = client.series_handle("PAPA").stats()
print(f"Total Events: {stats.total_events}")
print(f"Total Players: {stats.total_players}")
print(f"Total Participations: {stats.total_participations}")
print(f"Average Event Size: {stats.average_event_size}")
```

## Get Series Schedule

Get the schedule of upcoming and past events for a series.

**Parameters:** None

```python
from ifpa_api.models.series import SeriesScheduleResponse

# Get series schedule
schedule: SeriesScheduleResponse = client.series_handle("PAPA").schedule()
for event in schedule.events:
    print(f"{event.event_date}: {event.event_name}")
    print(f"  Location: {event.city}, {event.stateprov}")
    print(f"  Status: {event.status}")
```

## Get Series Region Representatives

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

For complete examples, see the [README](https://github.com/jscom/ifpa-api#series).
