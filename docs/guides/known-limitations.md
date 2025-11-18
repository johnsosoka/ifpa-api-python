# Known API Limitations

This guide documents known bugs and limitations in the IFPA API that affect the SDK. These are **API-level issues**, not SDK bugs, and cannot be fixed in the client library.

!!! info "SDK vs API Issues"
    All limitations documented here are in the upstream IFPA API itself. The SDK correctly implements the API specification but cannot work around these server-side bugs.

## Critical Limitations

### State/Province Filter (Broken)

The `stateprov` filter in both player and director search endpoints returns incorrect results.

#### Player Search

**Symptom**: Filtering by state/province returns players from completely different locations.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Request players from California (CA)
ca_players: PlayerSearchResponse = (client.player.query()
    .state("CA")
    .get())

# BUG: Results may include players from:
# - Canterbury, New Zealand (state="Can")
# - Other provinces/states that contain "CA" anywhere in the name
# - Players from completely unrelated locations
```

**Impact**: Cannot reliably filter players by state/province.

**Workaround**: Filter results client-side after retrieval:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Get broader results
results: PlayerSearchResponse = client.player.query("Smith").get()

# Filter client-side for exact state match
ca_players = [p for p in results.search if p.state == "CA" and p.country_code == "US"]
```

#### Director Search

**Symptom**: Filtering by state/province returns directors from incorrect states.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Request directors from Washington (WA)
wa_directors: DirectorSearchResponse = (client.director.query()
    .state("WA")
    .get())

# BUG: Results include directors from other states
# Filter is unreliable and returns incorrect data
```

**Impact**: Cannot reliably filter directors by state/province.

**Workaround**: Use country-level filtering and filter client-side:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Get all US directors with a name filter
results: DirectorSearchResponse = (client.director.query("Josh")
    .country("US")
    .get())

# Filter client-side for exact state
wa_directors = [d for d in results.directors if d.stateprov == "WA"]
```

### Player Search Pagination (Broken)

The `.offset()` method in player search queries is completely non-functional.

**Symptom**: Using `.offset()` causes SQL errors or returns zero results.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# BAD - Will fail
try:
    page1: PlayerSearchResponse = client.player.query("Smith").offset(0).limit(25).get()
    page2: PlayerSearchResponse = client.player.query("Smith").offset(25).limit(25).get()  # FAILS
except Exception as e:
    print(f"Pagination broken: {e}")
```

**Impact**: Cannot paginate through player search results.

**Workaround**: Use `.limit()` only and request all needed results in a single query:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# GOOD - Single query with reasonable limit
all_smiths: PlayerSearchResponse = (client.player.query("Smith")
    .country("US")
    .limit(100)  # Get first 100 results only
    .get())
```

**See Also**: [Pagination Guide - Known Limitations](pagination.md#known-limitations) for detailed examples and workarounds.

### Player Results Pagination (Ignored)

The player results endpoint accepts pagination parameters but completely ignores them.

**Symptom**: Regardless of `start_pos` or `count` parameters, the API returns **all** results.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerResultsResponse
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# These pagination parameters do nothing
results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# API returns ALL results regardless of any pagination settings
print(f"Total results: {results.total_results}")
print(f"Actual count: {len(results.results)}")  # Always the same
```

**Impact**: Cannot paginate server-side; always receive full result set.

**Workaround**: Use client-side array slicing for pagination:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerResultsResponse, PlayerResult
from ifpa_api.models.common import RankingSystem, ResultType

client: IfpaClient = IfpaClient()

# Fetch all results once
all_results: PlayerResultsResponse = client.player(25584).results(
    ranking_system=RankingSystem.MAIN,
    result_type=ResultType.ACTIVE
)

# Paginate client-side
page_size: int = 50
page_1: list[PlayerResult] = all_results.results[0:50]
page_2: list[PlayerResult] = all_results.results[50:100]
```

**See Also**: [Pagination Guide - Player Results](pagination.md#player-results-pagination-ignored) for complete examples.

### Series Standings Pagination (Ignored)

Series standings endpoints also ignore pagination parameters and always return complete results.

**Symptom**: `start_pos` and `count` parameters are accepted but have no effect.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse

client: IfpaClient = IfpaClient()

# These parameters are ignored
standings: SeriesStandingsResponse = client.series("NACS").standings()

# Always returns full standings list
print(f"Results: {len(standings.overall_results)}")
```

**Impact**: Cannot paginate server-side; always receive full standings.

**Workaround**: Use client-side array slicing:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse

client: IfpaClient = IfpaClient()

all_standings: SeriesStandingsResponse = client.series("NACS").standings()

# Slice client-side
page_size: int = 20
page_1 = all_standings.overall_results[0:page_size]
page_2 = all_standings.overall_results[page_size:page_size*2]
```

**See Also**: [Pagination Guide - Series Standings](pagination.md#series-standings-pagination-ignored) for complete examples.

## Working Features

These features are **confirmed working** and fully supported:

| Feature | Status | Notes |
|---------|--------|-------|
| **Rankings Pagination** | ✅ Fully working | `start_pos` and `count` work correctly |
| **Director Search** | ✅ Mostly working | `.offset()` and `.limit()` work; only `.state()` filter is broken |
| **Tournament Search** | ✅ Fully working | All query builder filters and pagination work |
| **Country Filters** | ✅ Fully working | Country filtering works reliably across all endpoints |
| **City Filters** | ✅ Fully working | City filtering works correctly |
| **Date Range Filters** | ✅ Fully working | Tournament date filtering works correctly |

## Impact Summary

### High Impact
- **State/Province filtering**: Cannot reliably filter by state in player or director searches
- **Player search pagination**: Cannot paginate player search results

### Medium Impact
- **Player results pagination**: Must handle large result sets and paginate client-side
- **Series standings pagination**: Must handle complete standings lists

### Mitigations

All limitations have workarounds:

1. **State filtering**: Use client-side filtering after retrieval
2. **Player pagination**: Use reasonable `.limit()` values (50-100)
3. **Results pagination**: Implement client-side slicing
4. **Standings pagination**: Implement client-side slicing

The SDK provides full type safety for all workarounds, making client-side filtering and pagination straightforward and safe.

## Reporting New Issues

If you discover additional API limitations:

1. Verify it's an API issue by testing the raw API endpoint directly
2. Create a detailed test case that reproduces the issue
3. Open an issue on the SDK repository with:
   - API endpoint affected
   - Expected behavior vs actual behavior
   - Minimal reproducible example
   - Workaround if known

## Related Resources

- [Pagination Guide](pagination.md) - Detailed pagination examples and workarounds
- [Searching Guide](searching.md) - Query Builder pattern usage
- [Error Handling](error-handling.md) - Handle API errors gracefully
- [IFPA API Documentation](https://api.ifpapinball.com/docs) - Official API reference
