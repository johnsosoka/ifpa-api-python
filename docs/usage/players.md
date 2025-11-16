# Players

The Players resource provides access to player profiles, rankings, tournament results, and head-to-head comparisons.

## Search for Players

Search for players by name, location, or tournament participation:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse, PlayerSearchResult

client: IfpaClient = IfpaClient()

# Simple name search
response: PlayerSearchResponse = client.players.search(name="John")
for player in response.search:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")
    print(f"  Location: {player.city}, {player.state}")
    print(f"  Current Rank: #{player.wppr_rank}")
```

### Search with Filters

Narrow down results with multiple filters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Search by location
response: PlayerSearchResponse = client.players.search(
    stateprov="OR",
    country="US"
)

# Search by tournament participation
response: PlayerSearchResponse = client.players.search(
    tournament="PAPA",
    tourpos=1
)

# Search with count limit
response: PlayerSearchResponse = client.players.search(
    name="Smith",
    count=25
)
```

!!! warning "Pagination Limitations"
    The IFPA API's player search pagination is currently non-functional. Using `start_pos` parameter
    may cause errors or return 0 results. For best results, use only the `count` parameter to limit
    results and avoid `start_pos` entirely.

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Player name (partial match, case insensitive) |
| `stateprov` | `str` | State/province code (2-digit) |
| `country` | `str` | Country name or 2-digit code |
| `tournament` | `str` | Tournament name (partial strings accepted) |
| `tourpos` | `int` | Finishing position in tournament |
| `count` | `int \| str` | Number of results to return (recommended: use without start_pos) |

!!! note "Deprecated Parameter"
    The `start_pos` parameter is documented but non-functional in the API. Avoid using it.

## Get Player Profile

Retrieve detailed information about a specific player:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

# Get player by ID
player: Player = client.player(12345).get()

print(f"Name: {player.first_name} {player.last_name}")
print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")
print(f"Player ID: {player.player_id}")
print(f"IFPA Registered: {player.ifpa_registered}")
print(f"Age: {player.age}")

# Access rankings across systems
for ranking in player.rankings:
    print(f"{ranking.ranking_system}: Rank {ranking.rank}, Rating {ranking.rating}")
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
from ifpa_api.exceptions import IfpaApiError

client: IfpaClient = IfpaClient()

try:
    player = client.player(99999999).get()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Player not found")
```

## Get Multiple Players

Fetch multiple players in a single request for efficient batch operations:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import MultiPlayerResponse, Player

client: IfpaClient = IfpaClient()

# Fetch up to 50 players at once
response: MultiPlayerResponse = client.players.get_multiple([123, 456, 789])

# Handle single or multiple players
if isinstance(response.player, list):
    for player in response.player:
        print(f"{player.first_name} {player.last_name}")
else:
    player: Player = response.player
    print(f"{player.first_name} {player.last_name}")
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `player_ids` | `list[int \| str]` | List of player IDs (maximum 50) |

### Notes

- Maximum 50 player IDs per request
- Raises `IfpaClientValidationError` if more than 50 IDs provided
- Response may contain a single `Player` or list of `Player` objects depending on API response
- Invalid player IDs will cause the entire request to fail with a 404 error

## Tournament Results

Get a player's tournament history:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerResultsResponse, TournamentResult

client: IfpaClient = IfpaClient()

# Get all active results (both parameters required)
results: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

print(f"Total results: {results.total_results}")
for result in results.results:
    print(f"\n{result.tournament_name}")
    print(f"  Date: {result.event_date}")
    print(f"  Position: {result.position} of {result.player_count}")
    print(f"  WPPR Points: {result.wppr_points}")
    print(f"  Rating: {result.rating_value}")
```

### Filter Results

Both `ranking_system` and `result_type` are required parameters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerResultsResponse

client: IfpaClient = IfpaClient()

# Main ranking active results
active: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# Women's ranking active results
women: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.WOMEN,
    result_type=ResultType.ACTIVE
)

# All inactive results
inactive: PlayerResultsResponse = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.INACTIVE
)
```

!!! warning "Pagination Not Supported"
    While the API accepts `start_pos` and `count` parameters for results, they are currently
    ignored by the API. Requesting a specific page size or offset will not work as expected.
    The API returns all results regardless of these parameters.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ranking_system` | `RankingSystem` | Ranking system filter (REQUIRED) |
| `result_type` | `ResultType` | Result activity type (REQUIRED) |

!!! note "Deprecated Parameters"
    `start_pos` and `count` parameters are non-functional in the current API.

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
from ifpa_api.exceptions import PlayersNeverMetError

client: IfpaClient = IfpaClient()

try:
    # Compare player 12345 vs player 67890
    pvp: PvpComparison = client.player(12345).pvp(67890)

    print(f"Player 1: {pvp.player1_name}")
    print(f"Player 2: {pvp.player2_name}")
    print(f"\nHead-to-Head Record:")
    print(f"  {pvp.player1_name} wins: {pvp.player1_wins}")
    print(f"  {pvp.player2_name} wins: {pvp.player2_wins}")
    print(f"  Ties: {pvp.ties}")
    print(f"  Total meetings: {pvp.total_meetings}")

    # Show tournament-by-tournament breakdown
    for match in pvp.tournaments:
        winner = "Player 1" if match.winner_player_id == pvp.player1_id else "Player 2"
        print(f"\n{match.tournament_name} ({match.event_date})")
        print(f"  {pvp.player1_name}: Position {match.player_1_position}")
        print(f"  {pvp.player2_name}: Position {match.player_2_position}")
        print(f"  Winner: {winner}")

except PlayersNeverMetError:
    print("These players have never competed in the same tournament")
```

### Exception Handling

The `pvp()` method raises `PlayersNeverMetError` when two players have never competed together:

```python
from ifpa_api import IfpaClient
from ifpa_api.exceptions import PlayersNeverMetError, IfpaApiError

client: IfpaClient = IfpaClient()

try:
    comparison = client.player(12345).pvp(67890)
except PlayersNeverMetError as e:
    print(f"Players {e.player1_id} and {e.player2_id} have never met")
except IfpaApiError as e:
    print(f"API error: {e}")
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `opponent_id` | `int \| str` | ID of player to compare against |

## PvP All Competitors

Get a summary of all players a player has competed against:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PvpAllCompetitors

client: IfpaClient = IfpaClient()

# Get summary of all competitors
summary: PvpAllCompetitors = client.player(2643).pvp_all()

print(f"Player ID: {summary.player_id}")
print(f"Total competitors: {summary.total_competitors}")
print(f"System: {summary.system}")
print(f"Type: {summary.type}")
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | `int` | The player's ID |
| `total_competitors` | `int` | Total number of players competed against |
| `system` | `str` | Ranking system (e.g., "MAIN") |
| `type` | `str` | Type of PvP data (e.g., "all") |
| `title` | `str` | Title or description |

## Ranking History

Track a player's WPPR ranking and rating over time:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import RankingHistory

client: IfpaClient = IfpaClient()

# Get ranking history
history: RankingHistory = client.player(12345).history()

print(f"Player ID: {history.player_id}")
print(f"System: {history.system}")
print(f"Active: {history.active_flag}")

print("\nRank History (last 10):")
for entry in history.rank_history[-10:]:
    print(f"{entry.rank_date}: Rank #{entry.rank_position}, "
          f"WPPR {entry.wppr_points}, "
          f"Tournaments: {entry.tournaments_played_count}")

print("\nRating History (last 10):")
for entry in history.rating_history[-10:]:
    print(f"{entry.rating_date}: Rating {entry.rating}")
```

### Response Fields

The history response contains two separate arrays:

- **rank_history**: Historical rank positions with WPPR points and tournament counts
- **rating_history**: Historical rating values

!!! note "String Values"
    The API returns numeric fields as strings in history data. Convert them using `int()` or
    `float()` when performing calculations.

### Visualize Ranking Trends

```python
import matplotlib.pyplot as plt
from datetime import datetime
from ifpa_api import IfpaClient
from ifpa_api.models.player import RankingHistory

client: IfpaClient = IfpaClient()
history: RankingHistory = client.player(12345).history()

# Extract dates and rankings (convert string values to numbers)
rank_dates = [datetime.strptime(e.rank_date, "%Y-%m-%d") for e in history.rank_history]
ranks = [int(e.rank_position) for e in history.rank_history]
wppr_points = [float(e.wppr_points) for e in history.rank_history]

# Plot ranking over time
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(rank_dates, ranks)
ax1.set_ylabel('World Rank')
ax1.set_title(f'Player {history.player_id} - WPPR Ranking History')
ax1.invert_yaxis()  # Lower rank number is better

ax2.plot(rank_dates, wppr_points)
ax2.set_ylabel('WPPR Points')
ax2.set_xlabel('Date')

plt.tight_layout()
plt.show()
```

## Complete Example: Player Analysis

Here's a complete example that analyzes a player's profile:

```python
from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import Player, PlayerResultsResponse, RankingHistory


def analyze_player(player_id: int) -> None:
    """Comprehensive player analysis."""
    client: IfpaClient = IfpaClient()

    try:
        # Get player profile
        player: Player = client.player(player_id).get()

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
            points = f"{result.wppr_points:.2f}" if result.wppr_points else "N/A"
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
    analyze_player(12345)
```

## Best Practices

### Error Handling

Always handle potential errors:

```python
from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError
from ifpa_api.models.player import Player

client: IfpaClient = IfpaClient()

try:
    player: Player = client.player(999999).get()
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
    return client.player(player_id).get()


# First call fetches from API
player: Player = get_cached_player(12345)

# Subsequent calls use cache
player: Player = get_cached_player(12345)  # Instant
```

### Batch Operations

When working with multiple players, use the `get_multiple()` method for efficiency:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import MultiPlayerResponse, Player

client: IfpaClient = IfpaClient()

# Efficient batch fetch (up to 50 at once)
response: MultiPlayerResponse = client.players.get_multiple([12345, 67890, 11111])

if isinstance(response.player, list):
    for player in response.player:
        print(f"{player.first_name} {player.last_name}")
```

For larger batches, chunk the requests:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player

def get_many_players(player_ids: list[int]) -> list[Player]:
    """Get multiple player profiles with chunking."""
    client: IfpaClient = IfpaClient()
    all_players: list[Player] = []

    # Process in chunks of 50
    for i in range(0, len(player_ids), 50):
        chunk = player_ids[i:i+50]
        response = client.players.get_multiple(chunk)

        if isinstance(response.player, list):
            all_players.extend(response.player)
        else:
            all_players.append(response.player)

    return all_players
```

## Known Limitations

### API Pagination Issues

The IFPA API has several known pagination issues:

1. **Player Search Pagination**: Using `start_pos` may cause SQL errors or return 0 results
2. **Results Pagination**: The `count` and `start_pos` parameters are ignored by the API
3. **State/Province Filter**: May return players from incorrect states/countries

These are API-level issues, not SDK bugs. For the most reliable experience:

- Avoid using `start_pos` in player searches
- Don't rely on pagination for player results
- Be cautious with state/province filters - verify results manually

## Related Resources

- [Rankings](rankings.md) - View rankings across all players
- [Tournaments](tournaments.md) - View tournament results
- [Error Handling](error-handling.md) - Handle API errors
- [Exceptions Reference](../api-reference/exceptions.md) - Exception types
