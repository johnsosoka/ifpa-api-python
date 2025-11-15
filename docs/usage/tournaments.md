# Tournaments

Search for tournaments and access detailed tournament information and results.

## Search for Tournaments

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Search by name and location
tournaments = client.tournaments.search(
    name="Pinball",
    city="Portland",
    stateprov="OR"
)

for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")
```

## Get Tournament Details

```python
# Get tournament information
tournament = client.tournament(12345).get()
print(f"Name: {tournament.tournament_name}")
print(f"Location: {tournament.city}, {tournament.stateprov}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.player_count}")
```

## Get Tournament Results

```python
# Get results
results = client.tournament(12345).results()
for result in results.results:
    print(f"{result.position}. {result.player_name}: {result.points} points")
```

## Get Tournament Formats

```python
# Get tournament format information
formats = client.tournament(12345).formats()
```

## Get League Information

```python
# Get league data (if tournament is part of a league)
league = client.tournament(12345).league()
```

For complete examples, see the [README](https://github.com/jscom/ifpa-sdk#tournaments).
