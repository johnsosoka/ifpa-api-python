# Quick Start

This guide will get you up and running with the IFPA API package in just a few minutes.

## Prerequisites

Before you begin, ensure you have:

1. [Installed the package](installation.md)
2. [Obtained an API key](authentication.md)

## Your First Request

Here's a simple example to get you started:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

# Initialize the client (uses IFPA_API_KEY environment variable)
client: IfpaClient = IfpaClient()

# Get information about a player - Dwayne Smith, highly active player from Boise, ID
player: Player = client.player(25584).details()
print(f"Name: {player.first_name} {player.last_name}")
print(f"Country: {player.country_name}")

# Access rankings from the rankings list
for ranking in player.rankings:
    if ranking.ranking_system == "Main":
        print(f"Current Rank: {ranking.rank}")
        print(f"WPPR Rating: {ranking.rating}")

# Output:
# Name: Dwayne Smith
# Country: United States
# Current Rank: 753
# WPPR Rating: 65.42
```

## Common Patterns

### Search for Players

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Query by name - Find players named "Smith" in Idaho
results: PlayerSearchResponse = client.player.query("Smith").state("ID").get()
for player in results.search:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")

# Output:
# 25584: Dwayne Smith
# 47585: Debbie Smith

# Query with filters - Find players named "John" in Idaho
results: PlayerSearchResponse = client.player.query("John").state("ID").country("US").limit(5).get()
```

### Get Rankings

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Get top 100 WPPR rankings
rankings: RankingsResponse = client.rankings.wppr(count=100)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.wppr_points}")

# Get women's rankings
women: RankingsResponse = client.rankings.women(count=50)

# Filter by country
us_rankings: RankingsResponse = client.rankings.wppr(country="US", count=50)
```

### Find Tournaments

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Query for tournaments with filters
tournaments: TournamentSearchResponse = client.tournament.query("Pinball").state("WA").get()

for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
```

### Get Tournament Results

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament, TournamentResultsResponse

client: IfpaClient = IfpaClient()

# Get tournament details
tournament: Tournament = client.tournament(12345).details()
print(f"Tournament: {tournament.tournament_name}")

# Get results
results: TournamentResultsResponse = client.tournament(12345).results()
for result in results.results:
    print(f"{result.position}. {result.player_name}")
```

### Player Tournament History

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerResultsResponse

client: IfpaClient = IfpaClient()

# Get active tournament results
results: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

for result in results.results:
    print(f"{result.tournament_name}: Placed {result.position}")
```

### Compare Players

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpComparison

client: IfpaClient = IfpaClient()

# Head-to-head comparison
pvp: PvpComparison = client.player(12345).pvp(67890)
print(f"Player 1 Wins: {pvp.player1_wins}")
print(f"Player 2 Wins: {pvp.player2_wins}")
print(f"Ties: {pvp.ties}")
```

### Series Standings

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesListResponse, SeriesStandingsResponse

client: IfpaClient = IfpaClient()

# List all series
all_series: SeriesListResponse = client.series.list()
for series_item in all_series.series:
    print(f"{series_item.series_code}: {series_item.series_name}")

# Get series standings
standings: SeriesStandingsResponse = client.series("PAPA").standings()
for entry in standings.standings:
    print(f"{entry.position}. {entry.player_name}")
```

### Reference Data

```python
from ifpa_api import IfpaClient
from ifpa_api.models.reference import CountryResponse, StateProvResponse

client: IfpaClient = IfpaClient()

# Get all countries
countries: CountryResponse = client.reference.countries()
for country in countries.country[:5]:
    print(f"{country.country_name} ({country.country_code})")

# Get states/provinces for a country
state_provs: StateProvResponse = client.reference.state_provs()
us_regions = next(c for c in state_provs.stateprov if c.country_code == "US")
print(f"US has {len(us_regions.regions)} states")
```

## Using Context Manager

The client supports Python's context manager protocol for automatic cleanup:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player
from ifpa_api.models.rankings import RankingsResponse

with IfpaClient() as client:
    player: Player = client.player(12345).details()
    rankings: RankingsResponse = client.rankings.wppr(count=100)
    # Client automatically closed when exiting
```

## Error Handling

Always handle potential errors when making API requests:

```python
from ifpa_api import (
    IfpaClient,
    IfpaApiError,
    MissingApiKeyError,
    IfpaClientValidationError
)
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

try:
    player: Player = client.player(12345).details()
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
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse, RankingEntry

client: IfpaClient = IfpaClient()

# Get first page
page_size: int = 50
start_pos: int = 0

rankings: RankingsResponse = client.rankings.wppr(start_pos=start_pos, count=page_size)
print(f"Total rankings: {rankings.total_count}")

# Get next page
start_pos += page_size
next_page: RankingsResponse = client.rankings.wppr(start_pos=start_pos, count=page_size)


# Iterate through all pages
def get_all_rankings(max_results: int = 1000) -> list[RankingEntry]:
    """Get all rankings up to max_results."""
    all_rankings: list[RankingEntry] = []
    start_pos: int = 0
    page_size: int = 250  # Maximum per request

    while len(all_rankings) < max_results:
        rankings: RankingsResponse = client.rankings.wppr(
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
from ifpa_api import IfpaClient

client: IfpaClient = IfpaClient(
    api_key='your-api-key',  # Explicit API key
    base_url='https://api.ifpapinball.com',  # Custom base URL
    timeout=30.0,  # Request timeout (seconds)
    validate_requests=True  # Enable request validation
)
```

## Working with Enums

The package provides enums for common parameters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import (
    TimePeriod,  # PAST, FUTURE
    RankingSystem,  # MAIN, WOMEN, YOUTH, VIRTUAL, PRO
    ResultType,  # ACTIVE, NONACTIVE, INACTIVE
    TournamentType  # OPEN, WOMEN, YOUTH, etc.
)
from ifpa_api.models.director import DirectorTournamentsResponse
from ifpa_api.models.player import PlayerResultsResponse

client: IfpaClient = IfpaClient()

# Use enums for type safety - Get Josh Rainwater's tournaments
past_tournaments: DirectorTournamentsResponse = client.director(1533).tournaments(TimePeriod.PAST)
upcoming: DirectorTournamentsResponse = client.director(1533).tournaments(TimePeriod.FUTURE)

# Get active results for main ranking system
results: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
```

## Complete Example

Here's a complete example that demonstrates multiple features:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import Player, PlayerResultsResponse


def analyze_player(player_id: int) -> None:
    """Analyze a player's profile and performance."""
    with IfpaClient() as client:
        try:
            # Get player details
            player: Player = client.player(player_id).details()
            print(f"\n=== {player.first_name} {player.last_name} ===")
            print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")

            # Get rankings across all systems
            print("\n--- Rankings ---")
            for ranking in player.rankings:
                print(f"{ranking.ranking_system}: Rank {ranking.rank}, Rating {ranking.rating}")

            # Get recent tournament results
            print("\n--- Recent Results ---")
            results: PlayerResultsResponse = client.player(player_id).results(
                ranking_system=RankingSystem.MAIN,
                result_type=ResultType.ACTIVE
            )
            for result in results.results[:5]:
                print(f"{result.tournament_name}: Placed {result.position}")

        except IfpaApiError as e:
            print(f"Error fetching player data: {e}")


if __name__ == "__main__":
    analyze_player(12345)
```

## Next Steps

### Learn Key Patterns
- [Callable Pattern](../guides/callable-pattern.md) - Understand `client.player(id).details()` pattern
- [Searching](../guides/searching.md) - Master the Query Builder for powerful searches
- [Pagination](../guides/pagination.md) - Handle large result sets effectively
- [Error Handling](../guides/error-handling.md) - Robust error handling strategies

### Explore API Resources
- [Players](../resources/players.md) - Player profiles, results, and comparisons
- [Directors](../resources/directors.md) - Tournament directors and their events
- [Tournaments](../resources/tournaments.md) - Tournament details, results, and formats
- [Rankings](../resources/rankings.md) - WPPR rankings across all systems
- [Series](../resources/series.md) - Series standings and player cards
- [Reference](../resources/reference.md) - Countries and state/province data

### API Client Reference
- [Client](../api-client-reference/client.md) - Complete IfpaClient documentation
- [Models](../api-client-reference/models.md) - Pydantic models reference
- [Exceptions](../api-client-reference/exceptions.md) - Exception handling reference
