# Player

The Player resource provides access to player profiles, rankings, tournament results, and head-to-head comparisons.

## Quick Example

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Fluent query builder - search for players named "Smith" in Idaho
results: PlayerSearchResponse = client.player.query("Smith").state("ID").get()
```

## Search for Players

The **recommended** way to search for players is using the fluent query builder:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Simple name search
results: PlayerSearchResponse = client.player.query("Smith").state("ID").get()
for player in results.search:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")
    print(f"  Location: {player.city}, {player.state}")
    print(f"  Current Rank: #{player.wppr_rank}")

# Output:
# 25584: Dwayne Smith
#   Location: Boise, ID
#   Current Rank: #753
# 47585: Debbie Smith
#   Location: Boise, ID
#   Current Rank: #7078
```

### Chained Filters

The fluent API allows method chaining for complex queries:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Chain multiple filters
results: PlayerSearchResponse = (client.player.query("John")
    .country("US")
    .state("ID")
    .limit(5)
    .get())

# Filter by tournament participation
results: PlayerSearchResponse = (client.player.query()
    .tournament("PAPA")
    .position(1)
    .limit(10)
    .get())

# Location-only search (no name query)
results: PlayerSearchResponse = (client.player.query()
    .country("US")
    .state("ID")
    .limit(25)
    .get())
```

### Query Reuse (Immutable Pattern)

The query builder is immutable - each method returns a new instance, allowing query reuse:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Create a reusable base query for US players
us_query = client.player.query().country("US")

# Derive state-specific queries from the base
wa_players: PlayerSearchResponse = us_query.state("WA").limit(25).get()
id_players: PlayerSearchResponse = us_query.state("ID").limit(25).get()
or_players: PlayerSearchResponse = us_query.state("OR").limit(25).get()

# The base query remains unchanged and can be reused
ca_players: PlayerSearchResponse = us_query.state("CA").limit(25).get()
```

### Query Builder Methods

| Method | Parameter | Description |
|--------|-----------|-------------|
| `.query(name)` | `str` | Player name (partial match, case insensitive) |
| `.state(code)` | `str` | State/province code (2-digit, e.g., "ID", "WA") |
| `.country(code)` | `str` | Country name or 2-digit code (e.g., "US", "CA") |
| `.tournament(name)` | `str` | Tournament name (partial strings accepted) |
| `.position(pos)` | `int` | Finishing position in tournament |
| `.offset(start)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute query and return results |

!!! warning "API Pagination Limitations"
    The IFPA API's player search pagination is currently non-functional. Using `.offset()` may cause
    errors or return 0 results. For best results, use only `.limit()` and avoid `.offset()`.

!!! note "Deprecated Methods"
    The old `client.player.search(name="John")` method is deprecated and will be removed in v1.0.0.
    Use the fluent query builder instead: `client.player.query("John").get()`

## Get Player Profile

Retrieve detailed information about a specific player:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

# Get player by ID - Dwayne Smith (highly active player from Boise, ID)
player: Player = client.player(25584).details()

print(f"Name: {player.first_name} {player.last_name}")
print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")
print(f"Player ID: {player.player_id}")
print(f"IFPA Registered: {player.ifpa_registered}")
print(f"Age: {player.age}")

# Access rankings across systems
for ranking in player.rankings:
    print(f"{ranking.ranking_system}: Rank {ranking.rank}, Rating {ranking.rating}")

# Output:
# Name: Dwayne Smith
# Location: Boise, ID, United States
# Player ID: 25584
# IFPA Registered: True
# Age: 55
# Main: Rank 753, Rating 65.42
```

### Profile Information

Player profiles include:

- **Identity**: Name, location, player ID, initials
- **Rankings**: List of rankings across different systems (Main, Women, Youth, etc.)
- **Registration**: Age, IFPA membership status, FIDE player status
- **Statistics**: Additional player statistics in `player_stats` dictionary
- **Profile**: Profile photo URL, exclusion flag

### Invalid Player IDs

When requesting a non-existent player, the SDK raises an error:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError

client: IfpaClient = IfpaClient()

try:
    player = client.player(99999999).details()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Player not found")
```

## Tournament Results

Get a player's tournament history:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerResultsResponse

client: IfpaClient = IfpaClient()

# Get all active results for Dwayne Smith (both parameters required)
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

print(f"Total results: {results.total_results}")
for result in results.results[:3]:  # Show first 3 results
    print(f"\n{result.tournament_name}")
    print(f"  Date: {result.event_date}")
    print(f"  Position: {result.position} of {result.player_count}")
    print(f"  WPPR Points: {result.current_points}")
    print(f"  Rating: {result.rating_value}")

# Output:
# Total results: 218
#
# Thursday night pinball
#   Date: 2024-12-05
#   Position: 4 of 11
#   WPPR Points: 3.49
#   Rating: 8.36
```

### Filter Results

Both `ranking_system` and `result_type` are required parameters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerResultsResponse

client: IfpaClient = IfpaClient()

# Main ranking active results for Dwayne Smith
active: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# Women's ranking active results for Debbie Smith
women: PlayerResultsResponse = client.player(47585).results(
    ranking_system=RankingSystem.WOMEN,
    result_type=ResultType.ACTIVE
)

# All inactive results for Dwayne Smith
inactive: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.INACTIVE
)
```

!!! warning "Pagination Not Supported"
    While the API accepts `start_pos` and `count` parameters for results, they are currently
    ignored by the API. Requesting a specific page size or offset will not work as expected.
    The API returns all results regardless of these parameters.

### Ranking Systems

- `RankingSystem.MAIN` - Main WPPR rankings
- `RankingSystem.WOMEN` - Women's rankings
- `RankingSystem.YOUTH` - Youth rankings
- `RankingSystem.PRO` - Pro circuit rankings

### Result Types

- `ResultType.ACTIVE` - Currently active results counting toward rankings
- `ResultType.NONACTIVE` - Non-active results
- `ResultType.INACTIVE` - Inactive results not counting toward rankings

## Head-to-Head Comparison

Compare two players' tournament history:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpComparison
from ifpa_api.core.exceptions import PlayersNeverMetError

client: IfpaClient = IfpaClient()

try:
    # Compare Dwayne Smith vs Debbie Smith (they've played 205 tournaments together)
    pvp: PvpComparison = client.player(25584).pvp(47585)

    print(f"Player 1: {pvp.player1_name}")
    print(f"Player 2: {pvp.player2_name}")
    print(f"\nHead-to-Head Record:")
    print(f"  {pvp.player1_name} wins: {pvp.player1_wins}")
    print(f"  {pvp.player2_name} wins: {pvp.player2_wins}")
    print(f"  Ties: {pvp.ties}")
    print(f"  Total meetings: {pvp.total_meetings}")

    # Show tournament-by-tournament breakdown (first 3)
    for match in pvp.tournaments[:3]:
        winner = "Player 1" if match.winner_player_id == pvp.player1_id else "Player 2"
        print(f"\n{match.tournament_name} ({match.event_date})")
        print(f"  {pvp.player1_name}: Position {match.player_1_position}")
        print(f"  {pvp.player2_name}: Position {match.player_2_position}")
        print(f"  Winner: {winner}")

except PlayersNeverMetError:
    print("These players have never competed in the same tournament")

# Output:
# Player 1: Dwayne Smith
# Player 2: Debbie Smith
#
# Head-to-Head Record:
#   Dwayne Smith wins: 139
#   Debbie Smith wins: 66
#   Ties: 0
#   Total meetings: 205
```

### Exception Handling

The `pvp()` method raises `PlayersNeverMetError` when two players have never competed together:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import PlayersNeverMetError, IfpaApiError

client: IfpaClient = IfpaClient()

try:
    # John Sosoka (50104) vs World #1 player (1) - they've never met
    comparison = client.player(50104).pvp(1)
except PlayersNeverMetError as e:
    print(f"Players {e.player_id} and {e.opponent_id} have never met")
except IfpaApiError as e:
    print(f"API error: {e}")

# Output:
# Players 50104 and 1 have never met
```

## PvP All Competitors

Get a summary of all players a player has competed against:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpAllCompetitors

client: IfpaClient = IfpaClient()

# Get summary of all competitors for Dwayne Smith
summary: PvpAllCompetitors = client.player(25584).pvp_all()

print(f"Player ID: {summary.player_id}")
print(f"Total competitors: {summary.total_competitors}")
print(f"System: {summary.system}")
print(f"Type: {summary.type}")

# Output:
# Player ID: 25584
# Total competitors: 375
# System: MAIN
# Type: all
```

## Ranking History

Track a player's WPPR ranking and rating over time:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import RankingHistory

client: IfpaClient = IfpaClient()

# Get ranking history for Dwayne Smith
history: RankingHistory = client.player(25584).history()

print(f"Player ID: {history.player_id}")
print(f"System: {history.system}")
print(f"Active: {history.active_flag}")

print("\nRank History (last 5):")
for entry in history.rank_history[-5:]:
    print(f"{entry.rank_date}: Rank #{entry.rank_position}, "
          f"WPPR {entry.wppr_points}, "
          f"Tournaments: {entry.tournaments_played_count}")

print("\nRating History (last 5):")
for entry in history.rating_history[-5:]:
    print(f"{entry.rating_date}: Rating {entry.rating}")

# Output:
# Player ID: 25584
# System: MAIN
# Active: Y
#
# Rank History (last 5):
# 2024-11-01: Rank #765, WPPR 65.25, Tournaments: 432
# 2024-12-01: Rank #753, WPPR 65.42, Tournaments: 433
```

!!! note "String Values"
    The API returns numeric fields as strings in history data. Convert them using `int()` or
    `float()` when performing calculations.

## Complete Example: Player Analysis

Here's a complete example that analyzes a player's profile:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import Player, PlayerResultsResponse, RankingHistory


def analyze_player(player_id: int = 25584) -> None:
    """Comprehensive player analysis.

    Default player: Dwayne Smith (25584) - highly active player from Boise, ID
    """
    client: IfpaClient = IfpaClient()

    try:
        # Get player profile
        player: Player = client.player(player_id).details()

        print("=" * 60)
        print(f"{player.first_name} {player.last_name}")
        print("=" * 60)

        # Basic info
        print(f"\nLocation: {player.city}, {player.stateprov}, {player.country_name}")
        print(f"Player ID: {player.player_id}")
        print(f"Age: {player.age}")
        print(f"IFPA Registered: {player.ifpa_registered}")

        # Rankings across systems
        print(f"\nRankings by System:")
        for ranking in player.rankings:
            print(f"  {ranking.ranking_system}: Rank {ranking.rank}, Rating {ranking.rating}")
            if ranking.country_rank:
                print(f"    Country Rank: {ranking.country_rank}")

        # Recent results
        print(f"\nRecent Tournament Results:")
        results: PlayerResultsResponse = client.player(player_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE
        )

        for result in results.results[:5]:
            finish = f"{result.position}/{result.player_count}" if result.player_count else str(result.position)
            points = f"{result.current_points:.2f}" if result.current_points else "N/A"
            print(f"  {result.tournament_name}: {finish} ({points} pts)")

        # Ranking trend
        history: RankingHistory = client.player(player_id).history()
        if len(history.rank_history) >= 2:
            recent = history.rank_history[-1]
            previous = history.rank_history[-2]
            rank_change = int(previous.rank_position) - int(recent.rank_position)
            rating_change = float(recent.wppr_points) - float(previous.wppr_points)

            print(f"\nRecent Trend:")
            print(f"  Rank change: {rank_change:+d}")
            print(f"  WPPR change: {rating_change:+.2f}")

    except IfpaApiError as e:
        print(f"API Error: {e}")
        if e.status_code:
            print(f"Status Code: {e.status_code}")


if __name__ == "__main__":
    # Analyze Dwayne Smith - highly active player
    analyze_player(25584)
```

## Best Practices

### Error Handling

Always handle potential errors:

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

### Caching Results

For frequently accessed data, consider caching:

```python
from functools import lru_cache
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player


@lru_cache(maxsize=100)
def get_cached_player(player_id: int) -> Player:
    """Get player with caching."""
    client: IfpaClient = IfpaClient()
    return client.player(player_id).details()


# First call fetches from API
player: Player = get_cached_player(25584)  # Dwayne Smith

# Subsequent calls use cache
player: Player = get_cached_player(25584)  # Instant - from cache
```

### Reusable Queries

Take advantage of the immutable query builder pattern:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Create a base query for tournament winners
winners_query = client.player.query().position(1)

# Derive specific tournament queries
papa_winners: PlayerSearchResponse = winners_query.tournament("PAPA").limit(10).get()
pinburgh_winners: PlayerSearchResponse = winners_query.tournament("Pinburgh").limit(10).get()
tilt_winners: PlayerSearchResponse = winners_query.tournament("TILT").limit(10).get()
```

## Known Limitations

### API Pagination Issues

The IFPA API has several known pagination issues:

1. **Player Search Pagination**: Using `.offset()` may cause SQL errors or return 0 results
2. **Results Pagination**: The `count` and `start_pos` parameters are ignored by the API
3. **State/Province Filter**: May return players from incorrect states/countries

These are API-level issues, not SDK bugs. For the most reliable experience:

- Avoid using `.offset()` in player searches
- Don't rely on pagination for player results
- Be cautious with state/province filters - verify results manually

## Deprecated Methods

!!! warning "Deprecated in v0.2.0"
    The following methods are deprecated and will be removed in v1.0.0:

    - `client.player.search(name="John")` → Use `client.player.query("John").get()`
    - `client.player.get_multiple([123, 456])` → Use `client.player(123).details()` for individual players

    Both methods still work but emit deprecation warnings. Migrate to the new fluent API.

## Related Resources

- [Rankings](rankings.md) - View rankings across all players
- [Tournaments](tournaments.md) - View tournament results
- [Error Handling](../guides/error-handling.md) - Handle API errors
- [Exceptions Reference](../api-client-reference/exceptions.md) - Exception types
