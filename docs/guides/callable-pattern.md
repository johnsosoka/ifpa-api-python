# Callable Pattern

The IFPA API Python SDK uses a **callable pattern** for resource-specific operations. This pattern provides a fluent, intuitive interface for accessing individual players, directors, tournaments, and series.

## What is the Callable Pattern?

The callable pattern allows you to "call" a resource property with an identifier to create a context for operations on that specific resource:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

# The callable pattern in action
player: Player = client.player(25584).details()
```

Breaking this down:
1. `client.player` - Access the player resource
2. `client.player(25584)` - "Call" it with a player ID to create a player context
3. `client.player(25584).details()` - Call a method on that context to get data

## Why Use the Callable Pattern?

### Type Safety

The callable pattern enables excellent IDE autocomplete and type checking:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player, PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# IDE knows this returns a Player
player: Player = client.player(25584).details()

# IDE knows this returns PlayerResultsResponse
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
```

Your IDE will:
- Suggest available methods after `client.player(id).`
- Provide parameter hints for each method
- Catch type errors before runtime

### Fluent API Design

The pattern creates a natural, readable flow:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpComparison

client: IfpaClient = IfpaClient()

# Read like English: "Get player 25584's PvP comparison with player 47585"
pvp: PvpComparison = client.player(25584).pvp(47585)
```

### Resource Scoping

Operations are scoped to specific resources, making the API self-documenting:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player
from ifpa_api.models.director import Director
from ifpa_api.models.tournaments import Tournament

client: IfpaClient = IfpaClient()

# Player operations
player: Player = client.player(25584).details()

# Director operations
director: Director = client.director(1533).details()

# Tournament operations
tournament: Tournament = client.tournament(7070).details()
```

## Player Resource Examples

The Player resource provides comprehensive player profile and tournament data.

### Get Player Profile

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

# Get Dwayne Smith's profile (Player ID: 25584)
player: Player = client.player(25584).details()

print(f"Name: {player.first_name} {player.last_name}")
print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")
print(f"IFPA Registered: {player.ifpa_registered}")

# Access rankings across systems
for ranking in player.rankings:
    print(f"{ranking.ranking_system}: Rank {ranking.rank}, Rating {ranking.rating}")
```

### Get Tournament Results

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# Get active tournament results for Dwayne Smith
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

print(f"Total active results: {results.total_results}")
for result in results.results[:5]:
    print(f"{result.tournament_name}: Position {result.position} of {result.player_count}")
```

### Head-to-Head Comparison

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpComparison
from ifpa_api.core.exceptions import PlayersNeverMetError

client: IfpaClient = IfpaClient()

try:
    # Compare Dwayne Smith (25584) vs Debbie Smith (47585)
    pvp: PvpComparison = client.player(25584).pvp(47585)

    print(f"{pvp.player1_name} vs {pvp.player2_name}")
    print(f"  {pvp.player1_name} wins: {pvp.player1_wins}")
    print(f"  {pvp.player2_name} wins: {pvp.player2_wins}")
    print(f"  Ties: {pvp.ties}")
    print(f"  Total meetings: {pvp.total_meetings}")
except PlayersNeverMetError:
    print("These players have never competed together")
```

### Get PvP Summary

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpAllCompetitors

client: IfpaClient = IfpaClient()

# Get summary of all competitors Dwayne Smith has faced
summary: PvpAllCompetitors = client.player(25584).pvp_all()

print(f"Player ID: {summary.player_id}")
print(f"Total competitors faced: {summary.total_competitors}")
```

### Get Ranking History

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import RankingHistory

client: IfpaClient = IfpaClient()

# Get Dwayne Smith's ranking history over time
history: RankingHistory = client.player(25584).history()

print(f"System: {history.system}")
print(f"Active: {history.active_flag}")

# Show recent rank changes
for entry in history.rank_history[-3:]:
    print(f"{entry.rank_date}: Rank #{entry.rank_position}, WPPR {entry.wppr_points}")
```

## Director Resource Examples

The Director resource provides tournament director profiles and their event history.

### Get Director Profile

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import Director

client: IfpaClient = IfpaClient()

# Get Josh Rainwater's director profile (Director ID: 1533)
director: Director = client.director(1533).details()

print(f"Name: {director.name}")
print(f"Location: {director.city}, {director.stateprov}, {director.country_name}")

if director.stats:
    print(f"Tournaments: {director.stats.tournament_count}")
    print(f"Unique Players: {director.stats.unique_player_count}")
    print(f"Highest Value: {director.stats.highest_value}")
```

### Get Director's Tournaments

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorTournamentsResponse
from ifpa_api.models.common import TimePeriod

client: IfpaClient = IfpaClient()

# Get past tournaments directed by Josh Rainwater
past: DirectorTournamentsResponse = client.director(1533).tournaments(TimePeriod.PAST)

print(f"Director: {past.director_name}")
print(f"Total past tournaments: {past.total_count}")

for tournament in past.tournaments[:3]:
    print(f"\n{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Players: {tournament.player_count}")
    print(f"  Value: {tournament.value}")
```

### Get Upcoming Tournaments

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorTournamentsResponse
from ifpa_api.models.common import TimePeriod

client: IfpaClient = IfpaClient()

# Get future tournaments for Erik Thoren (highly active director)
upcoming: DirectorTournamentsResponse = client.director(1151).tournaments(TimePeriod.FUTURE)

print(f"Upcoming tournaments: {upcoming.total_count}")

for tournament in upcoming.tournaments[:5]:
    print(f"\n{tournament.tournament_name}")
    print(f"  Start: {tournament.event_date}")
    print(f"  Location: {tournament.location_name}")
```

## Tournament Resource Examples

The Tournament resource provides detailed tournament information, results, and formats.

### Get Tournament Details

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament

client: IfpaClient = IfpaClient()

# Get PAPA 17 tournament details (Tournament ID: 7070)
tournament: Tournament = client.tournament(7070).details()

print(f"Name: {tournament.tournament_name}")
print(f"Event: {tournament.event_name}")
print(f"Location: {tournament.city}, {tournament.stateprov}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.player_count}")
print(f"Director: {tournament.director_name}")
print(f"WPPR Value: {tournament.wppr_value}")
```

### Get Tournament Results

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentResultsResponse

client: IfpaClient = IfpaClient()

# Get results for PAPA 17
results: TournamentResultsResponse = client.tournament(7070).results()

print(f"Tournament: {results.tournament_name}")
print(f"Date: {results.event_date}")
print(f"Players: {results.player_count}")

print("\nTop 10 Finishers:")
for result in results.results[:10]:
    wppr_str: str = f"{result.points:.2f}" if result.points else "N/A"
    print(f"{result.position}. {result.player_name} - {wppr_str} WPPR")
```

### Get Tournament Formats

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsResponse

client: IfpaClient = IfpaClient()

# Get format information for PAPA 17
formats: TournamentFormatsResponse = client.tournament(7070).formats()

print(f"Tournament ID: {formats.tournament_id}")
print(f"Formats used: {len(formats.formats)}")

for fmt in formats.formats:
    print(f"\nFormat: {fmt.format_name}")
    print(f"  Rounds: {fmt.rounds}")
    print(f"  Games per round: {fmt.games_per_round}")
    print(f"  Players: {fmt.player_count}")
```

## Series Resource Examples

The Series resource provides tournament series standings and player cards.

### Get Series Standings

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse

client: IfpaClient = IfpaClient()

# Get overall NACS standings across all regions
standings: SeriesStandingsResponse = client.series("NACS").standings()

print(f"Series: {standings.series_code}")
print(f"Year: {standings.year}")
print(f"Championship Prize Fund: ${standings.championship_prize_fund}")

# Show top regions
for region in standings.overall_results[:5]:
    print(f"\n{region.region_name}: {region.player_count} players")
    print(f"  Leader: {region.current_leader['player_name']}")
```

### Get Player's Series Card

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesPlayerCard

client: IfpaClient = IfpaClient()

# Get Dwayne Smith's (25584) NACS card for Idaho region
card: SeriesPlayerCard = client.series("NACS").player_card(25584, "ID")

print(f"Player: {card.player_name}")
print(f"Position: {card.current_position}")
print(f"Total Points: {card.total_points}")

print("\nEvent History:")
for event in card.player_card[:5]:
    print(f"  {event.tournament_name}: {event.wppr_points} pts")
```

### Get Region Representatives

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import RegionRepsResponse

client: IfpaClient = IfpaClient()

# Get PAPA region representatives
reps: RegionRepsResponse = client.series("PAPA").region_reps()

print("PAPA Region Representatives:")
for rep in reps.representative[:5]:
    print(f"\n{rep.region_name} ({rep.region_code})")
    print(f"  Rep: {rep.name}")
    print(f"  Player ID: {rep.player_id}")
```

## Comparison: Callable vs Traditional APIs

### Traditional Approach

Many APIs require you to pass IDs as parameters:

```python
# Traditional API design (NOT how this SDK works)
player = api.get_player_details(player_id=25584)
results = api.get_player_results(player_id=25584, system="MAIN", type="ACTIVE")
```

### Callable Pattern Approach

The IFPA SDK uses the callable pattern instead:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player, PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# Callable pattern - more intuitive and type-safe
player: Player = client.player(25584).details()
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
```

### Benefits

1. **Better IDE Support**: Type checkers know the exact return type of each method
2. **Clearer Intent**: The resource context (`player(25584)`) is explicit
3. **Method Discovery**: IDE autocomplete shows only methods valid for that resource
4. **Composition**: Easy to build helper functions around contexts

## Type Safety in Practice

The callable pattern works seamlessly with Python's type system:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player, PlayerResultsResponse, RankingHistory
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

def analyze_player_performance(player_id: int) -> dict[str, any]:
    """Analyze a player's performance with full type safety.

    Args:
        player_id: The player's unique identifier

    Returns:
        Dictionary with player analysis data
    """
    # All return types are known at compile time
    player: Player = client.player(player_id).details()
    results: PlayerResultsResponse = client.player(player_id).results(
        ranking_system=RankingSystem.MAIN,
        result_type=ResultType.ACTIVE
    )
    history: RankingHistory = client.player(player_id).history()

    return {
        "name": f"{player.first_name} {player.last_name}",
        "location": f"{player.city}, {player.stateprov}",
        "total_events": results.total_results,
        "rank_history": len(history.rank_history)
    }

# Type checkers validate this entire function
analysis: dict[str, any] = analyze_player_performance(25584)
```

## Advanced Usage

### Reusing Contexts

You can store contexts and reuse them:

```python
from ifpa_api import IfpaClient
from ifpa_api.resources.player.context import _PlayerContext

client: IfpaClient = IfpaClient()

# Create a player context
dwayne_context: _PlayerContext = client.player(25584)

# Use it multiple times (each call makes a fresh API request)
player = dwayne_context.details()
results = dwayne_context.results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)
history = dwayne_context.history()
```

### Context in Loops

The callable pattern works well in loops:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

player_ids: list[int] = [25584, 47585, 52913]  # Dwayne, Debbie, Dave

players: list[Player] = []
for player_id in player_ids:
    player: Player = client.player(player_id).details()
    players.append(player)
    print(f"Loaded: {player.first_name} {player.last_name}")
```

### Error Handling with Callable Pattern

Handle errors gracefully with full type information:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError, PlayersNeverMetError
from ifpa_api.models.player import Player, PvpComparison

client: IfpaClient = IfpaClient()

def get_player_safely(player_id: int) -> Player | None:
    """Get player with error handling.

    Args:
        player_id: Player identifier

    Returns:
        Player object or None if not found
    """
    try:
        player: Player = client.player(player_id).details()
        return player
    except IfpaApiError as e:
        if e.status_code == 404:
            print(f"Player {player_id} not found")
            return None
        raise

def compare_players_safely(player1_id: int, player2_id: int) -> PvpComparison | None:
    """Compare two players with error handling.

    Args:
        player1_id: First player ID
        player2_id: Second player ID

    Returns:
        PvP comparison or None if players never met
    """
    try:
        pvp: PvpComparison = client.player(player1_id).pvp(player2_id)
        return pvp
    except PlayersNeverMetError:
        print(f"Players {player1_id} and {player2_id} have never competed")
        return None
```

## Best Practices

### 1. Always Use Type Hints

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

# Good - type hint present
player: Player = client.player(25584).details()

# Bad - no type hint (still works but loses IDE support)
player = client.player(25584).details()
```

### 2. Import Specific Types

```python
# Good - import what you need
from ifpa_api.models.player import Player, PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

# Avoid - importing everything
from ifpa_api.models.player import *
```

### 3. Use Enums for Parameters

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType, TimePeriod

client: IfpaClient = IfpaClient()

# Good - type-safe enums
results = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# Bad - magic strings (still works but no type safety)
results = client.player(25584).results(
    ranking_system="MAIN",
    result_type="ACTIVE"
)
```

### 4. Handle Errors Explicitly

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

try:
    player: Player = client.player(99999999).details()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Player not found")
    else:
        print(f"API error: {e}")
```

## Related Resources

- [Searching Guide](searching.md) - Query Builder pattern for collections
- [Pagination Guide](pagination.md) - Handling paginated results
- [Player Resource](../resources/players.md) - Complete player API reference
- [Director Resource](../resources/directors.md) - Complete director API reference
- [Tournament Resource](../resources/tournaments.md) - Complete tournament API reference
- [Series Resource](../resources/series.md) - Complete series API reference
