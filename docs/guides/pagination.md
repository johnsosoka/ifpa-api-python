# Pagination

Many IFPA API endpoints support pagination to handle large result sets. This guide covers pagination patterns, best practices, and known API limitations.

## Pagination Overview

Pagination allows you to retrieve large datasets in smaller, manageable chunks:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Get first 100 rankings
page1: RankingsResponse = client.rankings.wppr(start_pos=0, count=100)

# Get next 100 rankings
page2: RankingsResponse = client.rankings.wppr(start_pos=100, count=100)
```

### Common Pagination Parameters

- **`start_pos`** (or `offset`): Starting position (0-based index)
- **`count`** (or `limit`): Number of results to return

## Rankings Pagination

Rankings endpoints have the most reliable pagination support.

### Basic Rankings Pagination

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Get top 100 players
rankings: RankingsResponse = client.rankings.wppr(start_pos=0, count=100)

print(f"Total rankings: {rankings.total_count}")
print(f"Retrieved: {len(rankings.rankings)} rankings")

for entry in rankings.rankings[:10]:
    print(f"{entry.rank}. {entry.player_name}: {entry.wppr_points} WPPR")
```

### Iterating Through Pages

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse, RankingEntry

client: IfpaClient = IfpaClient()

def get_top_n_rankings(max_results: int = 500) -> list[RankingEntry]:
    """Get top N rankings using pagination.

    Args:
        max_results: Maximum number of rankings to retrieve

    Returns:
        List of ranking entries with full type safety
    """
    all_rankings: list[RankingEntry] = []
    start_pos: int = 0
    page_size: int = 100  # Fetch 100 at a time

    while len(all_rankings) < max_results:
        # Calculate how many to fetch this iteration
        remaining: int = max_results - len(all_rankings)
        fetch_count: int = min(page_size, remaining)

        # Fetch page
        page: RankingsResponse = client.rankings.wppr(
            start_pos=start_pos,
            count=fetch_count
        )

        # Add to results
        all_rankings.extend(page.rankings)

        # Check if we got fewer results than requested (end of data)
        if len(page.rankings) < fetch_count:
            break

        # Move to next page
        start_pos += fetch_count

    return all_rankings

# Get top 500 players
top_500: list[RankingEntry] = get_top_n_rankings(500)
print(f"Retrieved {len(top_500)} rankings")
```

### Country-Specific Rankings

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Get top 100 US players
us_rankings: RankingsResponse = client.rankings.wppr(
    country="US",
    start_pos=0,
    count=100
)

# Get next page of US players
us_rankings_page2: RankingsResponse = client.rankings.wppr(
    country="US",
    start_pos=100,
    count=100
)

print(f"US Rankings - Page 1: {len(us_rankings.rankings)} players")
print(f"US Rankings - Page 2: {len(us_rankings_page2.rankings)} players")
```

### Women's and Youth Rankings

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Women's rankings with pagination
women_page1: RankingsResponse = client.rankings.women(
    start_pos=0,
    count=50
)

women_page2: RankingsResponse = client.rankings.women(
    start_pos=50,
    count=50
)

# Youth rankings with pagination
youth_page1: RankingsResponse = client.rankings.youth(
    start_pos=0,
    count=50
)

youth_page2: RankingsResponse = client.rankings.youth(
    start_pos=50,
    count=50
)
```

## Query Builder Pagination

The Query Builder pattern supports pagination through `.offset()` and `.limit()` methods.

### Player Query Pagination

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# First page - players named "Smith" in the US
page1: PlayerSearchResponse = (client.player.query("Smith")
    .country("US")
    .offset(0)
    .limit(25)
    .get())
```

### Director Query Pagination

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# First page of US directors
page1: DirectorSearchResponse = (client.director.query()
    .country("US")
    .offset(0)
    .limit(50)
    .get())

# Second page
page2: DirectorSearchResponse = (client.director.query()
    .country("US")
    .offset(50)
    .limit(50)
    .get())

print(f"Page 1: {len(page1.directors)} directors")
print(f"Page 2: {len(page2.directors)} directors")
```

### Tournament Query Pagination

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# First page of 2024 tournaments
page1: TournamentSearchResponse = (client.tournament.query()
    .date_range("2024-01-01", "2024-12-31")
    .country("US")
    .offset(0)
    .limit(100)
    .get())

# Second page
page2: TournamentSearchResponse = (client.tournament.query()
    .date_range("2024-01-01", "2024-12-31")
    .country("US")
    .offset(100)
    .limit(100)
    .get())

print(f"Page 1: {len(page1.tournaments)} tournaments")
print(f"Page 2: {len(page2.tournaments)} tournaments")
```

## Paginating with Query Reuse

Take advantage of immutable queries for cleaner pagination:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Create base query
us_directors_query = client.director.query().country("US").limit(50)

# Fetch multiple pages from same base query
page1: DirectorSearchResponse = us_directors_query.offset(0).get()
page2: DirectorSearchResponse = us_directors_query.offset(50).get()
page3: DirectorSearchResponse = us_directors_query.offset(100).get()

total_results: int = len(page1.directors) + len(page2.directors) + len(page3.directors)
print(f"Total results: {total_results}")
```

## Helper Functions for Pagination

### Generic Pagination Iterator

```python
from typing import TypeVar, Generic, Callable
from ifpa_api import IfpaClient

T = TypeVar('T')

def paginate_all(
    fetch_page: Callable[[int, int], list[T]],
    page_size: int = 100,
    max_results: int | None = None
) -> list[T]:
    """Generic pagination helper with type safety.

    Args:
        fetch_page: Function that takes (start_pos, count) and returns list of items
        page_size: Number of items per page
        max_results: Maximum total items to fetch (None for all)

    Returns:
        All items across all pages
    """
    all_items: list[T] = []
    start_pos: int = 0

    while True:
        # Calculate how many to fetch
        if max_results is not None:
            remaining: int = max_results - len(all_items)
            if remaining <= 0:
                break
            fetch_count: int = min(page_size, remaining)
        else:
            fetch_count: int = page_size

        # Fetch page
        items: list[T] = fetch_page(start_pos, fetch_count)

        # No more results
        if not items:
            break

        all_items.extend(items)

        # Got fewer than requested - end of data
        if len(items) < fetch_count:
            break

        start_pos += fetch_count

    return all_items

# Usage example
client: IfpaClient = IfpaClient()

def fetch_wppr_page(start_pos: int, count: int) -> list:
    """Fetch a page of WPPR rankings."""
    response = client.rankings.wppr(start_pos=start_pos, count=count)
    return response.rankings

# Get all top 1000 players
top_1000 = paginate_all(fetch_wppr_page, page_size=100, max_results=1000)
print(f"Fetched {len(top_1000)} rankings")
```

### Rankings Pagination Helper

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse, RankingEntry

client: IfpaClient = IfpaClient()

def get_all_wppr_rankings(
    max_rank: int = 1000,
    page_size: int = 250,
    country: str | None = None
) -> list[RankingEntry]:
    """Fetch WPPR rankings up to a maximum rank.

    Args:
        max_rank: Maximum rank position to fetch
        page_size: Number of rankings per page (max 250)
        country: Optional country filter

    Returns:
        List of ranking entries with type safety
    """
    all_rankings: list[RankingEntry] = []
    start_pos: int = 0

    while start_pos < max_rank:
        # Calculate how many to fetch
        remaining: int = max_rank - start_pos
        fetch_count: int = min(page_size, remaining)

        # Fetch page with optional country filter
        if country:
            page: RankingsResponse = client.rankings.wppr(
                country=country,
                start_pos=start_pos,
                count=fetch_count
            )
        else:
            page: RankingsResponse = client.rankings.wppr(
                start_pos=start_pos,
                count=fetch_count
            )

        # Add to results
        all_rankings.extend(page.rankings)

        # Check if we're done
        if len(page.rankings) < fetch_count:
            break

        start_pos += fetch_count

    return all_rankings

# Get top 500 worldwide
top_500_world: list[RankingEntry] = get_all_wppr_rankings(max_rank=500)

# Get top 200 US players
top_200_us: list[RankingEntry] = get_all_wppr_rankings(max_rank=200, country="US")

print(f"Worldwide: {len(top_500_world)} players")
print(f"US: {len(top_200_us)} players")
```

## Known Limitations

### Player Results Pagination (Ignored)

The player results endpoint accepts `start_pos` and `count` parameters but **completely ignores them**:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# These pagination parameters are IGNORED by the API
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE,
    # These do nothing:
    # start_pos=0,
    # count=50
)

# API always returns ALL results regardless of pagination parameters
print(f"Total results: {results.total_results}")
print(f"Actual results returned: {len(results.results)}")
# These will be the same number
```

**Workaround**: Handle pagination client-side:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerResultsResponse, PlayerResult
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

def get_player_results_page(
    player_id: int,
    ranking_system: RankingSystem,
    result_type: ResultType,
    page: int = 0,
    page_size: int = 50
) -> list[PlayerResult]:
    """Get paginated player results (client-side pagination).

    Args:
        player_id: Player identifier
        ranking_system: Ranking system filter
        result_type: Result type filter
        page: Page number (0-based)
        page_size: Results per page

    Returns:
        List of results for the requested page
    """
    # Fetch all results
    all_results: PlayerResultsResponse = client.player(player_id).results(
        ranking_system=ranking_system,
        result_type=result_type
    )

    # Calculate slice indices
    start_idx: int = page * page_size
    end_idx: int = start_idx + page_size

    # Return page slice
    page_results: list[PlayerResult] = all_results.results[start_idx:end_idx]
    return page_results

# Get first page (results 0-49)
page1: list[PlayerResult] = get_player_results_page(
    player_id=25584,
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE,
    page=0,
    page_size=50
)

# Get second page (results 50-99)
page2: list[PlayerResult] = get_player_results_page(
    player_id=25584,
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE,
    page=1,
    page_size=50
)
```

### Series Standings Pagination (Ignored)

Series standings endpoints also ignore pagination parameters:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse

client: IfpaClient = IfpaClient()

# These parameters do nothing
standings: SeriesStandingsResponse = client.series("NACS").standings(
    start_pos=0,
    count=50
)

# API returns all standings regardless
print(f"Results: {len(standings.overall_results)}")
```

**Workaround**: Use client-side slicing if needed:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse

client: IfpaClient = IfpaClient()

# Fetch all results
all_standings: SeriesStandingsResponse = client.series("NACS").standings()

# Slice client-side
page_size: int = 10
page_1 = all_standings.overall_results[0:page_size]
page_2 = all_standings.overall_results[page_size:page_size*2]
```

## Best Practices

### 1. Always Use Type Hints

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Good - type hints on all variables
page_size: int = 100
start_pos: int = 0
rankings: RankingsResponse = client.rankings.wppr(
    start_pos=start_pos,
    count=page_size
)

# Bad - no type hints
page_size = 100
start_pos = 0
rankings = client.rankings.wppr(start_pos=start_pos, count=page_size)
```

### 2. Set Reasonable Page Sizes

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

# Good - reasonable page size (100-250)
rankings: RankingsResponse = client.rankings.wppr(start_pos=0, count=100)

# Bad - too small (many API calls)
rankings: RankingsResponse = client.rankings.wppr(start_pos=0, count=10)

# Bad - too large (may timeout or fail)
rankings: RankingsResponse = client.rankings.wppr(start_pos=0, count=10000)
```

### 3. Check for End of Data

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

page_size: int = 100
start_pos: int = 0

while True:
    page: RankingsResponse = client.rankings.wppr(
        start_pos=start_pos,
        count=page_size
    )

    # Process results
    print(f"Fetched {len(page.rankings)} rankings starting at {start_pos}")

    # Check if we're done
    if len(page.rankings) < page_size:
        print("Reached end of data")
        break

    start_pos += page_size
```

### 4. Handle Rate Limits

```python
import time
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

def fetch_with_rate_limiting(
    start_pos: int,
    count: int,
    delay_seconds: float = 0.5
) -> RankingsResponse:
    """Fetch rankings with rate limiting.

    Args:
        start_pos: Starting position
        count: Number of results
        delay_seconds: Delay between requests

    Returns:
        Rankings response
    """
    try:
        rankings: RankingsResponse = client.rankings.wppr(
            start_pos=start_pos,
            count=count
        )
        time.sleep(delay_seconds)  # Be kind to the API
        return rankings
    except IfpaApiError as e:
        if e.status_code == 429:  # Rate limit exceeded
            print(f"Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return fetch_with_rate_limiting(start_pos, count, delay_seconds)
        raise
```

### 5. Implement Progress Tracking

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse, RankingEntry

client: IfpaClient = IfpaClient()

def fetch_rankings_with_progress(
    max_results: int = 1000,
    page_size: int = 100
) -> list[RankingEntry]:
    """Fetch rankings with progress tracking.

    Args:
        max_results: Maximum results to fetch
        page_size: Results per page

    Returns:
        List of ranking entries
    """
    all_rankings: list[RankingEntry] = []
    start_pos: int = 0

    while start_pos < max_results:
        # Calculate fetch count
        remaining: int = max_results - start_pos
        fetch_count: int = min(page_size, remaining)

        # Fetch page
        page: RankingsResponse = client.rankings.wppr(
            start_pos=start_pos,
            count=fetch_count
        )

        all_rankings.extend(page.rankings)

        # Progress update
        progress: float = (len(all_rankings) / max_results) * 100
        print(f"Progress: {len(all_rankings)}/{max_results} ({progress:.1f}%)")

        # Check if done
        if len(page.rankings) < fetch_count:
            break

        start_pos += fetch_count

    return all_rankings

rankings: list[RankingEntry] = fetch_rankings_with_progress(max_results=500)
```

## Summary of Pagination Support

| Endpoint | Pagination Support | Notes |
|----------|-------------------|-------|
| **Rankings (WPPR, Women, Youth, etc.)** | ✅ Full support | `start_pos` and `count` work correctly |
| **Director Search (Query Builder)** | ✅ Full support | `.offset()` and `.limit()` work correctly |
| **Tournament Search (Query Builder)** | ✅ Full support | `.offset()` and `.limit()` work correctly |
| **Player Search (Query Builder)** | ✅ Full support | `.offset()` and `.limit()` work correctly |
| **Player Results** | ❌ **Ignored** | API ignores pagination params - returns all results |
| **Series Standings** | ❌ **Ignored** | API ignores pagination params - returns all results |
| **Series Region Standings** | ✅ Partial support | `start_pos` and `count` accepted but may not be reliable |

## Related Resources

- [Searching Guide](searching.md) - Query Builder pattern
- [Callable Pattern Guide](callable-pattern.md) - Individual resource operations
- [Rankings Resource](../resources/rankings.md) - Complete rankings API reference
- [Player Resource](../resources/players.md) - Complete player API reference
- [Error Handling](../guides/error-handling.md) - Handle API errors
