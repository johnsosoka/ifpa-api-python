# IFPA API Python

[![PyPI version](https://img.shields.io/pypi/v/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/ifpa-api.svg)](https://pypi.org/project/ifpa-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/johnsosoka/ifpa-api-python/branch/main/graph/badge.svg)](https://codecov.io/gh/johnsosoka/ifpa-api-python)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://johnsosoka.github.io/ifpa-api-python/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![AI Code Review](https://github.com/johnsosoka/ifpa-api-python/actions/workflows/ai-code-review.yml/badge.svg)

**Unofficial** Python client for the [IFPA (International Flipper Pinball Association) API](https://api.ifpapinball.com/).

Access player rankings, tournament data, and statistics through a clean, type-safe Python interface with Pydantic validation.

## Installation

```bash
pip install ifpa-api
```

Requires Python 3.11+.

## Quick Start

```python
from ifpa_api import IfpaClient

# Initialize (uses IFPA_API_KEY environment variable)
client = IfpaClient()

# Get player by ID
player = client.player.get(2643)
print(f"{player.first_name} {player.last_name}")

# Access stats
stats = player.player_stats["system"]["open"]
print(f"WPPR Rank: {stats['current_rank']}")

# Search with filters
results = client.player.search("John") \
    .country("US") \
    .state("CA") \
    .limit(10) \
    .get()

# Get rankings
rankings = client.rankings.wppr(count=100)
for entry in rankings.rankings[:10]:
    print(f"{entry.rank}. {entry.player_name}")

# Get tournament results
results = client.tournament(67890).results()
for result in results.results[:5]:
    print(f"{result.position}. {result.player_name}: {result.points} pts")
```

## Features

- **Type-safe**: Full type hints and Pydantic validation with IDE autocomplete
- **Fluent API**: Chainable query builder for complex searches
- **46 Endpoints**: Complete IFPA API v2.1 coverage across 7 resources
- **Automatic Pagination**: Memory-efficient iteration with `.iterate()` and `.get_all()`
- **Enhanced Errors**: Structured exceptions with request context for debugging
- **99% Test Coverage**: Comprehensive unit and integration tests

## Resources

- **Players** — Search, profiles, rankings, tournament results, head-to-head
- **Tournaments** — Search, details, results, formats
- **Rankings** — WPPR, women, youth, country, age-based
- **Series** — Circuit standings, player cards, region data
- **Stats** — Overall metrics, largest tournaments, player activity
- **Directors** — Search, tournament listings

## Documentation

**Full documentation:** https://johnsosoka.github.io/ifpa-api-python/

- [Quick Start Guide](https://johnsosoka.github.io/ifpa-api-python/getting-started/quickstart/)
- [API Reference](https://johnsosoka.github.io/ifpa-api-python/api-client-reference/client/)
- [Practical Examples](https://johnsosoka.github.io/ifpa-api-python/guides/practical-examples/)
- [Migration Guide](https://johnsosoka.github.io/ifpa-api-python/api-client-reference/changelog/) (0.2.x → 0.4.x)

## AI Code Review

All pull requests are automatically reviewed by GPT-4o via [ai-code-review](https://github.com/AleksandrFurmenkovOfficial/ai-code-review). The AI checks for code quality, security issues, performance concerns, and maintainability.

Reviews run on every PR open and update. Results are posted as inline comments on the pull request.

## License

MIT License — see [LICENSE](LICENSE) file.

---

*Not affiliated with or endorsed by IFPA.*
