# Quick Start

This guide will get you up and running with the IFPA SDK in just a few minutes.

## Prerequisites

Before you begin, ensure you have:

1. [Installed the SDK](installation.md)
2. [Obtained an API key](authentication.md)

## Your First Request

Here's a simple example to get you started:

```python
from ifpa_sdk import IfpaClient

# Initialize the client (uses IFPA_API_KEY environment variable)
client = IfpaClient()

# Get information about a player
player = client.player(12345).get()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Country: {player.country_name}")
print(f"Current Rank: {player.current_wppr_rank}")
print(f"WPPR Rating: {player.current_wppr_value}")
```

## Common Patterns

### Search for Players

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Search by name
results = client.players.search(name="John")
for player in results.players:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")

# Search with filters
results = client.players.search(
    name="Smith",
    city="Portland",
    stateprov="OR"
)
```

### Get Rankings

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get top 100 WPPR rankings
rankings = client.rankings.wppr(start_pos=0, count=100)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

# Get women's rankings
women = client.rankings.women(count=50)

# Filter by country
us_rankings = client.rankings.wppr(country="US", count=50)
```

### Find Tournaments

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Search for tournaments
tournaments = client.tournaments.search(
    name="Pinball",
    city="Seattle",
    stateprov="WA"
)

for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
    print(f"  Players: {tournament.player_count}")
```

### Get Tournament Results

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get tournament details
tournament = client.tournament(12345).get()
print(f"Tournament: {tournament.tournament_name}")

# Get results
results = client.tournament(12345).results()
for result in results.results:
    print(f"{result.position}. {result.player_name}: {result.points} points")
```

### Player Tournament History

```python
from ifpa_sdk import IfpaClient, RankingSystem, ResultType

client = IfpaClient()

# Get active tournament results
results = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

for result in results.results:
    print(f"{result.tournament_name}: Placed {result.position}")
```

### Compare Players

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Head-to-head comparison
pvp = client.player(12345).pvp(67890)
print(f"Player 1 Wins: {pvp.player1_wins}")
print(f"Player 2 Wins: {pvp.player2_wins}")
print(f"Ties: {pvp.ties}")
```

### Series Standings

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# List all series
all_series = client.series.list()
for series in all_series.series:
    print(f"{series.series_code}: {series.series_name}")

# Get series standings
standings = client.series_handle("PAPA").standings(count=50)
for entry in standings.standings:
    print(f"{entry.position}. {entry.player_name}: {entry.points} points")
```

## Using Context Manager

The client supports Python's context manager protocol for automatic cleanup:

```python
from ifpa_sdk import IfpaClient

with IfpaClient() as client:
    player = client.player(12345).get()
    rankings = client.rankings.wppr(count=100)
    # Client automatically closed when exiting
```

## Error Handling

Always handle potential errors when making API requests:

```python
from ifpa_sdk import (
    IfpaClient,
    IfpaApiError,
    MissingApiKeyError,
    IfpaClientValidationError
)

client = IfpaClient()

try:
    player = client.player(12345).get()
    print(f"Found player: {player.first_name} {player.last_name}")
except MissingApiKeyError:
    print("Error: No API key configured")
except IfpaApiError as e:
    print(f"API error [{e.status_code}]: {e.message}")
except IfpaClientValidationError as e:
    print(f"Invalid parameters: {e.message}")
```

## Pagination

Many endpoints support pagination. Here's how to handle it:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get first page
page_size = 50
start_pos = 0

rankings = client.rankings.wppr(start_pos=start_pos, count=page_size)
print(f"Total rankings: {rankings.total_count}")

# Get next page
start_pos += page_size
next_page = client.rankings.wppr(start_pos=start_pos, count=page_size)


# Iterate through all pages
def get_all_rankings(max_results=1000):
    """Get all rankings up to max_results."""
    all_rankings = []
    start_pos = 0
    page_size = 250  # Maximum per request

    while len(all_rankings) < max_results:
        rankings = client.rankings.wppr(
            start_pos=start_pos,
            count=min(page_size, max_results - len(all_rankings))
        )

        all_rankings.extend(rankings.rankings)

        if len(rankings.rankings) < page_size:
            break  # No more results

        start_pos += page_size

    return all_rankings
```

## Configuration Options

Customize the client behavior:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient(
    api_key='your-api-key',  # Explicit API key
    base_url='https://api.ifpapinball.com',  # Custom base URL
    timeout=30.0,  # Request timeout (seconds)
    validate_requests=True  # Enable request validation
)
```

## Working with Enums

The SDK provides enums for common parameters:

```python
from ifpa_sdk import (
    IfpaClient,
    TimePeriod,  # PAST, FUTURE
    RankingSystem,  # MAIN, WOMEN, YOUTH, VIRTUAL, PRO
    ResultType,  # ACTIVE, NONACTIVE, INACTIVE
    TournamentType  # OPEN, WOMEN, YOUTH, etc.
)

client = IfpaClient()

# Use enums for type safety
past_tournaments = client.director(1000).tournaments(TimePeriod.PAST)
upcoming = client.director(1000).tournaments(TimePeriod.FUTURE)

# Get active results for main ranking system
results = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
```

## Complete Example

Here's a complete example that demonstrates multiple features:

```python
from ifpa_sdk import IfpaClient, IfpaApiError


def analyze_player(player_id: int) -> None:
    """Analyze a player's profile and performance."""
    with IfpaClient() as client:
        try:
            # Get player details
            player = client.player(player_id).get()
            print(f"\n=== {player.first_name} {player.last_name} ===")
            print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")
            print(f"Current Rank: #{player.current_wppr_rank}")
            print(f"WPPR Rating: {player.current_wppr_value}")
            print(f"Active Events: {player.active_events}")

            # Get rankings across all systems
            print("\n--- Rankings ---")
            rankings = client.player(player_id).rankings()
            for ranking in rankings:
                print(f"{ranking['system']}: Rank {ranking['rank']}")

            # Get recent tournament results
            print("\n--- Recent Results ---")
            results = client.player(player_id).results(count=10)
            for result in results.results[:5]:
                print(f"{result.tournament_name}: Placed {result.position}/{result.total_players}")

        except IfpaApiError as e:
            print(f"Error fetching player data: {e}")


if __name__ == "__main__":
    analyze_player(12345)
```

## Next Steps

- Explore [resource-specific examples](../usage/directors.md)
- Learn about [error handling](../usage/error-handling.md)
- Check the [API reference](../api-reference/overview.md)
- Review [configuration options](configuration.md)
