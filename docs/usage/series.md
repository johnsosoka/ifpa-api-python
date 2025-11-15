# Series

Access tournament series information, standings, and player performance.

## List All Series

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# List all series
all_series = client.series.list()
for series in all_series.series:
    print(f"{series.series_code}: {series.series_name}")

# Filter to active series only
active_series = client.series.list(active_only=True)
```

## Get Series Standings

```python
# Get standings for a specific series
standings = client.series_handle("PAPA").standings(start_pos=0, count=50)
for entry in standings.standings:
    print(f"{entry.position}. {entry.player_name}: {entry.points} points")
```

## Get Player's Series Card

```python
# Get player's performance in a series
card = client.series_handle("PAPA").player_card(12345)
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")

for event in card.events:
    print(f"{event.tournament_name}: {event.points_earned} points")
```

## Get Series Overview

```python
# Get series overview and statistics
overview = client.series_handle("PAPA").overview()
print(f"Series: {overview.series_name}")
print(f"Total Events: {overview.total_events}")
print(f"Total Players: {overview.total_players}")
```

## Get Series Rules

```python
# Get series rules and scoring system
rules = client.series_handle("PAPA").rules()
print(f"Scoring System: {rules.scoring_system}")
```

For complete examples, see the [README](https://github.com/jscom/ifpa-sdk#series).
