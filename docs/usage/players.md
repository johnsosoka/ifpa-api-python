# Players

The Players resource provides access to player profiles, rankings, tournament results, and head-to-head comparisons.

## Search for Players

Search for players by name, location, or other criteria:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Simple name search
players = client.players.search(name="John")
for player in players.players:
    print(f"{player.player_id}: {player.first_name} {player.last_name}")
    print(f"  Location: {player.city}, {player.stateprov}")
    print(f"  Current Rank: #{player.current_wppr_rank}")
```

### Search with Filters

Narrow down results with multiple filters:

```python
# Search by location
players = client.players.search(
    city="Portland",
    stateprov="OR",
    country="US"
)

# Search by first and last name
players = client.players.search(
    first_name="John",
    last_name="Smith"
)

# Paginated search
players = client.players.search(
    name="Smith",
    start_pos=0,
    count=25
)
```

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Player name (partial match) |
| `first_name` | `str` | First name filter |
| `last_name` | `str` | Last name filter |
| `city` | `str` | City filter |
| `stateprov` | `str` | State/province code |
| `country` | `str` | Country code (e.g., "US") |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return |

## Get Player Profile

Retrieve detailed information about a specific player:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get player by ID
player = client.player(12345).get()

print(f"Name: {player.first_name} {player.last_name}")
print(f"Location: {player.city}, {player.stateprov}, {player.country_name}")
print(f"Current WPPR Rank: #{player.current_wppr_rank}")
print(f"Current WPPR Value: {player.current_wppr_value}")
print(f"Active Events: {player.active_events}")
print(f"Highest Rank: #{player.highest_rank} on {player.highest_rank_date}")
```

### Profile Information

Player profiles include:

- **Identity**: Name, location, player ID
- **Rankings**: Current rank, rating, highest rank achieved
- **Activity**: Active events, inactive events, total events
- **Registration**: Age, initials, IFPA membership status
- **Statistics**: Tournament history, performance metrics

## Get Player Rankings

Access a player's rankings across all IFPA ranking systems:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get rankings for all systems
rankings = client.player(12345).rankings()

for ranking in rankings:
    print(f"{ranking['system']}: Rank {ranking['rank']}")
    if 'rating' in ranking:
        print(f"  Rating: {ranking['rating']}")
```

Rankings include:

- **Main WPPR**: Overall world ranking
- **Women's**: Women's ranking system
- **Youth**: Youth ranking system
- **Country**: Ranking within country
- **Pro**: Professional circuit ranking

## Tournament Results

Get a player's tournament history:

```python
from ifpa_sdk import IfpaClient, RankingSystem, ResultType

client = IfpaClient()

# Get all active results
results = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

print(f"Total results: {results.total_results}")
for result in results.results:
    print(f"\n{result.tournament_name}")
    print(f"  Date: {result.event_date}")
    print(f"  Placed: {result.position} of {result.total_players}")
    print(f"  Points: {result.points}")
    print(f"  Rating: {result.rating_value}")
```

### Filter Results

Filter by ranking system and result type:

```python
# Main ranking active results
active = client.player(12345).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# Women's ranking results
women = client.player(12345).results(
    ranking_system=RankingSystem.WOMEN
)

# All inactive results
inactive = client.player(12345).results(
    result_type=ResultType.INACTIVE
)
```

### Paginate Results

```python
# Get first 50 results
results = client.player(12345).results(
    start_pos=0,
    count=50
)

# Get next 50
next_results = client.player(12345).results(
    start_pos=50,
    count=50
)
```

## Head-to-Head Comparison

Compare two players' tournament history:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Compare player 12345 vs player 67890
pvp = client.player(12345).pvp(67890)

print(f"Player 1: {pvp.player1_name}")
print(f"Player 2: {pvp.player2_name}")
print(f"\nHead-to-Head Record:")
print(f"  {pvp.player1_name} wins: {pvp.player1_wins}")
print(f"  {pvp.player2_name} wins: {pvp.player2_wins}")
print(f"  Ties: {pvp.ties}")
print(f"  Total meetings: {pvp.total_meetings}")

# Show tournament-by-tournament breakdown
for match in pvp.tournaments:
    print(f"\n{match.tournament_name} ({match.event_date})")
    print(f"  {pvp.player1_name}: Position {match.player1_position}")
    print(f"  {pvp.player2_name}: Position {match.player2_position}")
```

## Ranking History

Track a player's WPPR ranking over time:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get ranking history
history = client.player(12345).history()

print(f"Player: {history.player_name}")
print(f"\nRanking History:")

for entry in history.history[-10:]:  # Last 10 entries
    print(f"{entry.date}: Rank #{entry.rank}, WPPR {entry.rating}")
```

### Visualize Ranking Trends

```python
import matplotlib.pyplot as plt
from datetime import datetime

history = client.player(12345).history()

# Extract dates and rankings
dates = [datetime.strptime(e.date, "%Y-%m-%d") for e in history.history]
ranks = [e.rank for e in history.history]
ratings = [e.rating for e in history.history]

# Plot ranking over time
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(dates, ranks)
ax1.set_ylabel('World Rank')
ax1.set_title(f'{history.player_name} - WPPR Ranking History')
ax1.invert_yaxis()  # Lower rank number is better

ax2.plot(dates, ratings)
ax2.set_ylabel('WPPR Rating')
ax2.set_xlabel('Date')

plt.tight_layout()
plt.show()
```

## Player Cards

Get a player's achievement cards and badges:

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get player cards
cards = client.player(12345).cards()

print(f"Total Cards: {len(cards.cards)}")

for card in cards.cards:
    print(f"\n{card.card_name}")
    print(f"  Earned: {card.date_earned}")
    print(f"  Description: {card.description}")
```

## Complete Example: Player Analysis

Here's a complete example that analyzes a player's profile:

```python
from ifpa_sdk import IfpaClient, RankingSystem, ResultType, IfpaApiError


def analyze_player(player_id: int) -> None:
    """Comprehensive player analysis."""
    with IfpaClient() as client:
        try:
            # Get player profile
            player = client.player(player_id).get()

            print("=" * 60)
            print(f"{player.first_name} {player.last_name}")
            print("=" * 60)

            # Basic info
            print(f"\nLocation: {player.city}, {player.stateprov}, {player.country_name}")
            print(f"Player ID: {player.player_id}")

            # Rankings
            print(f"\nCurrent Performance:")
            print(f"  World Rank: #{player.current_wppr_rank}")
            print(f"  WPPR Rating: {player.current_wppr_value}")
            print(f"  Active Events: {player.active_events}")

            print(f"\nCareer Best:")
            print(f"  Highest Rank: #{player.highest_rank}")
            print(f"  Achieved: {player.highest_rank_date}")

            # Get rankings across systems
            print(f"\nRankings by System:")
            rankings = client.player(player_id).rankings()
            for ranking in rankings:
                print(f"  {ranking['system']}: #{ranking['rank']}")

            # Recent results
            print(f"\nRecent Tournament Results:")
            results = client.player(player_id).results(
                ranking_system=RankingSystem.MAIN,
                result_type=ResultType.ACTIVE,
                count=10
            )

            for result in results.results[:5]:
                finish = f"{result.position}/{result.total_players}"
                print(f"  {result.tournament_name}: {finish} ({result.points:.2f} pts)")

            # Ranking trend
            history = client.player(player_id).history()
            if len(history.history) >= 2:
                recent = history.history[-1]
                previous = history.history[-2]
                rank_change = previous.rank - recent.rank
                rating_change = recent.rating - previous.rating

                print(f"\nRecent Trend:")
                print(f"  Rank change: {rank_change:+d}")
                print(f"  Rating change: {rating_change:+.2f}")

        except IfpaApiError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    analyze_player(12345)
```

## Best Practices

### Error Handling

Always handle potential errors:

```python
from ifpa_sdk import IfpaClient, IfpaApiError

client = IfpaClient()

try:
    player = client.player(999999).get()
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
from ifpa_sdk import IfpaClient


@lru_cache(maxsize=100)
def get_cached_player(player_id: int):
    """Get player with caching."""
    client = IfpaClient()
    return client.player(player_id).get()


# First call fetches from API
player = get_cached_player(12345)

# Subsequent calls use cache
player = get_cached_player(12345)  # Instant
```

### Batch Operations

When working with multiple players:

```python
from ifpa_sdk import IfpaClient


def get_multiple_players(player_ids: list[int]):
    """Get multiple player profiles efficiently."""
    client = IfpaClient()
    players = []

    for player_id in player_ids:
        try:
            player = client.player(player_id).get()
            players.append(player)
        except Exception as e:
            print(f"Failed to fetch player {player_id}: {e}")

    return players


# Get multiple players
players = get_multiple_players([12345, 67890, 11111])
```

## Related Resources

- [Rankings](rankings.md) - View rankings across all players
- [Tournaments](tournaments.md) - View tournament results
- [Error Handling](error-handling.md) - Handle API errors
