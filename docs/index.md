# IFPA API Client

> **Note**: This is an unofficial client library, not affiliated with or endorsed by IFPA.

Welcome to the IFPA API documentation! This library provides a typed Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/).

## Overview

The IFPA API client enables Python developers to access pinball rankings, tournament data, and player statistics through a clean, modern interface. Whether you're building a tournament management system, statistics dashboard, or analyzing player performance, this client provides the tools you need.

## Key Features

- **Fluent Query Builder API**: Immutable, type-safe, chainable query building for complex searches
- **Callable Pattern**: Direct resource access via `client.player(50104).details()` syntax
- **Fully Typed**: Complete type hints for IDE autocompletion and type checking
- **Pydantic Models**: Automatic request/response validation with detailed error messages
- **Resource-Oriented**: Intuitive access patterns matching the IFPA API structure
- **Comprehensive Coverage**: 36 IFPA API v2.1 endpoints across 6 resources
- **Pagination Support**: Built-in support for paginated endpoints with query builder methods
- **Clear Error Handling**: Exception hierarchy for different failure scenarios
- **Well Tested**: 99% test coverage with unit and integration tests

> **Alpha Release**: This library is under active development. The API is stable but may evolve based on community feedback. Production use is supported, but you may encounter occasional updates to the interface.

## Quick Example

This example demonstrates the fluent query builder API and callable pattern using real IFPA data:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse, Player

# Initialize client with API key
client: IfpaClient = IfpaClient(api_key="your-api-key-here")

# === Fluent Query Builder Pattern ===

# Simple query - search by name
results: PlayerSearchResponse = client.player.query("Smith").get()
print(f"Found {len(results.search)} players named Smith")

# Build a base query for US players - demonstrates immutable query builder
us_query = client.player.query().country("US")

# Reuse the base query for different states (immutable pattern!)
idaho_players: PlayerSearchResponse = us_query.state("ID").limit(10).get()
washington_players: PlayerSearchResponse = us_query.state("WA").limit(10).get()

print(f"Found {len(idaho_players.search)} players in Idaho")

# === Callable Pattern for Direct Resource Access ===

# Get specific player by ID (Dwayne Smith, rank #753)
player: Player = client.player(25584).details()

print(f"\nPlayer: {player.first_name} {player.last_name}")
# Active players always have stats; type-safe access with dict navigation
if player.player_stats:
    print(f"Current WPPR Rank: {player.player_stats['system']['open']['current_rank']}")
    print(f"Total Events: {player.player_stats['player_events']['total_events']}")

# === Advanced Query Builder - Complex Filtering ===

# Find all PAPA tournament winners using filter-only query
papa_winners: PlayerSearchResponse = (
    client.player.query()
    .tournament("PAPA")
    .position(1)
    .limit(25)
    .get()
)

print(f"\nFound {len(papa_winners.search)} PAPA winners")
for winner in papa_winners.search[:5]:
    print(f"  {winner.first_name} {winner.last_name} (ID: {winner.player_id})")

# === Rankings Access ===

# Get top 10 WPPR rankings
rankings = client.rankings.wppr(count=10)
for entry in rankings.rankings[:5]:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")

# Close the client when done
client.close()
```

**Key Patterns Demonstrated:**

- **Fluent Query Builder**: Immutable, composable queries with `.query()`, `.country()`, `.state()`, `.limit()`
- **Query Reusability**: Base queries can be safely reused without side effects (immutable pattern)
- **Callable Pattern**: Direct resource access via `client.player(25584).details()`
- **Advanced Filtering**: Chain multiple filters like `.tournament()` and `.position()` for complex queries
- **Type Safety**: Full type hints enable IDE autocompletion and type checking
- **Pydantic Models**: Response models provide validated, typed data access

## Installation

Install the client using pip:

```bash
pip install ifpa-api
```

Requires Python 3.11 or higher.

## API Resources

The client provides access to 36 of 46 IFPA API endpoints:

| Resource | Description | Endpoints |
|----------|-------------|-----------|
| **Directors** | Search tournament directors, view their events | 4 |
| **Players** | Player profiles, rankings, tournament history | 7 |
| **Rankings** | WPPR, women, youth, pro, and custom rankings | 9 |
| **Tournaments** | Search tournaments, view results and details | 6 |
| **Series** | Tournament series standings and statistics | 8 |
| **Reference** | Countries and states lookup | 2 |

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
- [Callable Pattern](guides/callable-pattern.md) - Direct resource access with `client.player(id)`
- [Query Builder](guides/searching.md) - Fluent, composable search queries
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
