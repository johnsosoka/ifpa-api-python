# IFPA API Client

> **Note**: This is an unofficial client library, not affiliated with or endorsed by IFPA.

Welcome to the IFPA API documentation! This library provides a typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/).

## Overview

The IFPA API client enables Python developers to access pinball rankings, tournament data, and player statistics through a clean, modern interface. Whether you're building a tournament management system, statistics dashboard, or analyzing player performance, this client provides the tools you need.

## Key Features

- **Fluent API Patterns** (v0.4.0+): Direct `.get()`, safe `.get_or_none()`, and `.exists()` methods
- **Modern Search API**: Chainable `.search()` builder with `.first()` and `.first_or_none()` helpers
- **Immutable Query Builder**: Type-safe, composable queries that can be safely reused
- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Resource-Oriented**: Intuitive access patterns matching the IFPA API structure
- **Comprehensive Coverage**: 46 IFPA API v2.1 endpoints across 7 resources
- **Pagination Support**: Built-in support for paginated endpoints with helper methods
- **Clear Error Handling**: Exception hierarchy for different failure scenarios
- **Well Tested**: 94% test coverage with 319 unit tests

## Quick Example

The v0.4.0 fluent API makes common operations simple and intuitive:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player, PlayerSearchResponse

# Initialize client with API key
client = IfpaClient(api_key="your-api-key")

# === New Fluent API (v0.4.0+) ===

# Direct resource access - simple and clear
player: Player = client.player.get(25584)  # Dwayne Smith, Rank #753
print(f"Player: {player.first_name} {player.last_name}")

# Safe access - returns None instead of raising exception
maybe_player: Player | None = client.player.get_or_none(999999)
if maybe_player:
    print(f"Found: {maybe_player.first_name}")

# Quick existence check
if client.player.exists(25584):
    print("Player exists!")

# Search with new .search() method
results: PlayerSearchResponse = client.player.search("Smith").state("ID").get()
print(f"Found {len(results.search)} Smiths in Idaho")

# Get first search result directly
first_smith = client.player.search("Smith").state("ID").first()
print(f"First result: {first_smith.first_name} {first_smith.last_name}")

# Safe first result - returns None if no matches
maybe = client.player.search("NONEXISTENT").first_or_none()

# === Immutable Query Builder ===

# Build base query and reuse it safely
us_query = client.player.search().country("US")
idaho_players = us_query.state("ID").get()     # Doesn't modify us_query
washington_players = us_query.state("WA").get()  # us_query unchanged!

# === Advanced Filtering ===

# Complex searches with chaining
papa_winners = (
    client.player.search()
    .tournament("PAPA")
    .position(1)
    .limit(25)
    .get()
)

# === Rankings Access ===

rankings = client.rankings.wppr(count=10)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

client.close()
```

**What's New in v0.4.0:**

- ✅ **`.get(id)`** - Direct resource access (replaces `.details()`)
- ✅ **`.get_or_none(id)`** - Safe access without exceptions
- ✅ **`.exists(id)`** - Quick existence check
- ✅ **`.search(query)`** - Fluent search builder (replaces `.query()`)
- ✅ **`.first()`** - Get first search result
- ✅ **`.first_or_none()`** - Safe first result access

**Deprecated patterns** (still work with warnings):
- ⚠️ `.query()` → Use `.search()` instead
- ⚠️ `.details()` → Use `.get()` instead

## Installation

Install the client using pip:

```bash
pip install ifpa-api
```

Requires Python 3.11 or higher.

## API Resources

The client provides access to 46 IFPA API v2.1 endpoints across 7 resources:

| Resource | Description | Endpoints | Fluent API |
|----------|-------------|-----------|------------|
| **Players** | Player profiles, rankings, tournament history | 6 | ✅ `.get()`, `.search()` |
| **Directors** | Search tournament directors, view their events | 4 | ✅ `.get()`, `.search()` |
| **Tournaments** | Search tournaments, view results and details | 5 | ✅ `.get()`, `.search()` |
| **Rankings** | WPPR, women, youth, pro, and custom rankings | 9 | 📋 Collection only |
| **Series** | Tournament series standings and statistics | 8 | 📋 Collection only |
| **Stats** | Player/tournament statistics by region and period | 10 | 📋 Collection only |
| **Reference** | Countries and states lookup | 2 | 📋 Collection only |

## Complete Example

Here's a real-world workflow combining multiple fluent API patterns:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player, PlayerSearchResponse

client = IfpaClient(api_key="your-api-key")

# Step 1: Search for players in Idaho
idaho_players: PlayerSearchResponse = (
    client.player.search()
    .country("US")
    .state("ID")
    .limit(10)
    .get()
)
print(f"Found {len(idaho_players.search)} players")

# Step 2: Get details for the top player
if idaho_players.search:
    top_player_id = idaho_players.search[0].player_id
    top_player: Player = client.player.get(top_player_id)
    print(f"Top player: {top_player.first_name} {top_player.last_name}")

    if top_player.player_stats:
        stats = top_player.player_stats['system']['open']
        print(f"Rank: {stats['current_rank']}")

# Step 3: Check if a specific player exists
if client.player.exists(50104):  # John Sosoka
    player: Player = client.player.get(50104)
    print(f"Found: {player.first_name} {player.last_name}")

# Step 4: Find tournaments with safe access
papa_tournament = client.tournament.search("PAPA").country("US").first_or_none()
if papa_tournament:
    print(f"Tournament: {papa_tournament.tournament_name}")

# Step 5: Batch operations with existence checks
player_ids = [25584, 47585, 52913]  # Active Idaho players
valid_players: list[Player] = []

for pid in player_ids:
    if client.player.exists(pid):
        player = client.player.get(pid)
        valid_players.append(player)
        print(f"✓ {player.first_name} {player.last_name}")

print(f"Successfully loaded {len(valid_players)} players")

client.close()
```

## Getting Help

- **Documentation**: Browse the [Getting Started](getting-started/installation.md) guide
- **Guides**: Learn [key patterns](guides/callable-pattern.md) and [search techniques](guides/searching.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/johnsosoka/ifpa-api-python/issues)
- **API Reference**: See the [IFPA API docs](https://api.ifpapinball.com/docs)

## Next Steps

### Get Started
- [Install the client](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [Authentication Setup](getting-started/authentication.md)

### Learn Key Patterns
- [Fluent API Guide](guides/callable-pattern.md) - Direct `.get()` and safe access patterns
- [Search Guide](guides/searching.md) - Modern `.search()` with `.first()` helpers
- [Pagination](guides/pagination.md) - Handle large result sets

### Explore Resources
- [Players](resources/players.md) - Player profiles and results
- [Directors](resources/directors.md) - Tournament directors
- [Tournaments](resources/tournaments.md) - Tournament data
- [Rankings](resources/rankings.md) - WPPR rankings
- [Series](resources/series.md) - Series standings

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/johnsosoka/ifpa-api-python/blob/main/LICENSE) file for details.

## Acknowledgments

Built by [John Sosoka](https://johnsosoka.com) for the pinball community. Thanks to IFPA for providing the public API.

**Maintainer**: [open.source@sosoka.com](mailto:open.source@sosoka.com)
