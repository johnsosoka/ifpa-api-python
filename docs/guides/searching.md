# Searching

The IFPA API Python SDK provides a powerful **Query Builder** pattern for searching players, directors, and tournaments. This pattern offers an immutable, fluent interface that's type-safe, composable, and easy to read.

## Query Builder Overview

The Query Builder pattern allows you to construct searches by chaining filter methods:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.player import PlayerSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Chain filters to build a search
            results: PlayerSearchResponse = await (client.player.search("Smith")
                .country("US")
                .state("ID")
                .limit(10)
                .get())

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.player import PlayerSearchResponse

    with IfpaClient() as client:
        # Chain filters to build a search
        results: PlayerSearchResponse = (client.player.search("Smith")
            .country("US")
            .state("ID")
            .limit(10)
            .get())
    ```

### Key Features

- **Immutable**: Each method returns a new query instance
- **Type-Safe**: Full type checking and IDE autocomplete support
- **Composable**: Build complex queries from simple building blocks
- **Reusable**: Base queries can be saved and extended

## Player Search

Search for players by name, location, tournament participation, and more.

### Basic Name Search

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.player import PlayerSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Simple name search
            results: PlayerSearchResponse = await client.player.search("Smith").get()

            print(f"Found {len(results.search)} players")
            for player in results.search:
                print(f"{player.player_id}: {player.first_name} {player.last_name}")
                print(f"  Location: {player.city}, {player.state}")
                print(f"  Rank: #{player.wppr_rank}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.player import PlayerSearchResponse

    with IfpaClient() as client:
        # Simple name search
        results: PlayerSearchResponse = client.player.search("Smith").get()

        print(f"Found {len(results.search)} players")
        for player in results.search:
            print(f"{player.player_id}: {player.first_name} {player.last_name}")
            print(f"  Location: {player.city}, {player.state}")
            print(f"  Rank: #{player.wppr_rank}")
    ```

### Location Filters

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.player import PlayerSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Search by country
            us_players: PlayerSearchResponse = await (client.player.search("John")
                .country("US")
                .get())

            # Search by state/province
            id_players: PlayerSearchResponse = await (client.player.search("John")
                .country("US")
                .state("ID")
                .get())

            # Search by city (must include country and state)
            boise_players: PlayerSearchResponse = await (client.player.search()
                .country("US")
                .state("ID")
                .city("Boise")
                .get())

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.player import PlayerSearchResponse

    with IfpaClient() as client:
        # Search by country
        us_players: PlayerSearchResponse = (client.player.search("John")
            .country("US")
            .get())

        # Search by state/province
        id_players: PlayerSearchResponse = (client.player.search("John")
            .country("US")
            .state("ID")
            .get())

        # Search by city (must include country and state)
        boise_players: PlayerSearchResponse = (client.player.search()
            .country("US")
            .state("ID")
            .city("Boise")
            .get())
    ```

### Tournament Filters

Search for players by tournament participation:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Find all PAPA winners
papa_winners: PlayerSearchResponse = (client.player.search()
    .tournament("PAPA")
    .position(1)
    .limit(20)
    .get())

print(f"Found {len(papa_winners.search)} PAPA winners")
for player in papa_winners.search:
    print(f"{player.first_name} {player.last_name} (Rank: #{player.wppr_rank})")

# Find players who competed in specific tournaments
pinburgh_players: PlayerSearchResponse = (client.player.search()
    .tournament("Pinburgh")
    .limit(50)
    .get())
```

### Combining Filters

Chain multiple filters for precise searches:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Find Johns in Idaho who competed in tournaments
results: PlayerSearchResponse = (client.player.search("John")
    .country("US")
    .state("ID")
    .tournament("Idaho")
    .limit(10)
    .get())

# Location-only search (no name required)
wa_players: PlayerSearchResponse = (client.player.search()
    .country("US")
    .state("WA")
    .limit(25)
    .get())
```

### Query Reuse (Immutability)

The Query Builder is **immutable** - each method returns a new instance. This enables powerful query composition:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.player import PlayerSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Create a reusable base search for US players
            us_search = client.player.search().country("US")

            # Derive state-specific searches from the base (filters are sync, execution is async)
            wa_players: PlayerSearchResponse = await us_search.state("WA").limit(25).get()
            id_players: PlayerSearchResponse = await us_search.state("ID").limit(25).get()
            or_players: PlayerSearchResponse = await us_search.state("OR").limit(25).get()

            # The base search remains unchanged!
            ca_players: PlayerSearchResponse = await us_search.state("CA").limit(25).get()

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.player import PlayerSearchResponse

    with IfpaClient() as client:
        # Create a reusable base search for US players
        us_search = client.player.search().country("US")

        # Derive state-specific searches from the base
        wa_players: PlayerSearchResponse = us_search.state("WA").limit(25).get()
        id_players: PlayerSearchResponse = us_search.state("ID").limit(25).get()
        or_players: PlayerSearchResponse = us_search.state("OR").limit(25).get()

        # The base search remains unchanged!
        ca_players: PlayerSearchResponse = us_search.state("CA").limit(25).get()
    ```

This pattern is especially useful when building dashboards or reports:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Base search for championship winners
champions_search = client.player.search().position(1)

# Get winners from different tournaments
papa_champs: PlayerSearchResponse = champions_search.tournament("PAPA").limit(10).get()
pinburgh_champs: PlayerSearchResponse = champions_search.tournament("Pinburgh").limit(10).get()
tilt_champs: PlayerSearchResponse = champions_search.tournament("TILT").limit(10).get()
```

### Player Query Methods

| Method | Parameter Type | Description |
|--------|----------------|-------------|
| `.search(name)` | `str` | Player name (partial match, case insensitive) |
| `.country(code)` | `str` | Country name or 2-digit code (e.g., "US", "CA") |
| `.state(code)` | `str` | State/province code (2-digit, e.g., "ID", "WA") |
| `.city(name)` | `str` | City name |
| `.tournament(name)` | `str` | Tournament name (partial strings accepted) |
| `.position(pos)` | `int` | Finishing position in tournament |
| `.offset(start)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute search and return results |
| `.first()` | - | Get first result (raises IndexError if none) |
| `.first_or_none()` | - | Get first result or None if empty |

## Director Search

Search for tournament directors by name and location.

### Basic Director Search

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.director import DirectorSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Simple name search
            results: DirectorSearchResponse = await client.director.search("Josh").get()

            print(f"Found {len(results.directors)} directors")
            for director in results.directors:
                print(f"{director.director_id}: {director.name}")
                print(f"  Location: {director.city}, {director.stateprov}, {director.country_name}")
                print(f"  Tournaments: {director.tournament_count}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.director import DirectorSearchResponse

    with IfpaClient() as client:
        # Simple name search
        results: DirectorSearchResponse = client.director.search("Josh").get()

        print(f"Found {len(results.directors)} directors")
        for director in results.directors:
            print(f"{director.director_id}: {director.name}")
            print(f"  Location: {director.city}, {director.stateprov}, {director.country_name}")
            print(f"  Tournaments: {director.tournament_count}")
    ```

### Location Filters

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Search by country
us_directors: DirectorSearchResponse = (client.director.search("Josh")
    .country("US")
    .get())

# Search by state and city
il_directors: DirectorSearchResponse = (client.director.search()
    .country("US")
    .state("IL")
    .city("Chicago")
    .get())

# Location-only search (no name required)
wa_directors: DirectorSearchResponse = (client.director.search()
    .country("US")
    .state("WA")
    .limit(50)
    .get())
```

### Query Reuse

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Create a reusable base query for US directors
us_directors_query = client.director.search().country("US")

# Derive state-specific queries
il_directors: DirectorSearchResponse = us_directors_query.state("IL").limit(25).get()
wa_directors: DirectorSearchResponse = us_directors_query.state("WA").limit(25).get()
or_directors: DirectorSearchResponse = us_directors_query.state("OR").limit(25).get()

# Base query is unchanged and can be reused
ca_directors: DirectorSearchResponse = us_directors_query.state("CA").limit(25).get()
```

### Director Query Methods

| Method | Parameter Type | Description |
|--------|----------------|-------------|
| `.search(name)` | `str` | Director name (partial match, case insensitive) |
| `.country(code)` | `str` | Country name or code (e.g., "US", "CA") |
| `.state(stateprov)` | `str` | State/province code (e.g., "IL", "WA") |
| `.city(city)` | `str` | City name |
| `.offset(start_position)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute search and return results |
| `.first()` | - | Get first result (raises IndexError if none) |
| `.first_or_none()` | - | Get first result or None if empty |

## Tournament Search

Search for tournaments by name, location, date range, and type.

### Basic Tournament Search

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.tournaments import TournamentSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Simple name search
            results: TournamentSearchResponse = await client.tournament.search("PAPA").get()

            print(f"Found {len(results.tournaments)} tournaments")
            for tournament in results.tournaments:
                print(f"{tournament.tournament_name} - {tournament.event_date}")
                print(f"  Location: {tournament.city}, {tournament.stateprov}")
                print(f"  Players: {tournament.player_count}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.tournaments import TournamentSearchResponse

    with IfpaClient() as client:
        # Simple name search
        results: TournamentSearchResponse = client.tournament.search("PAPA").get()

        print(f"Found {len(results.tournaments)} tournaments")
        for tournament in results.tournaments:
            print(f"{tournament.tournament_name} - {tournament.event_date}")
            print(f"  Location: {tournament.city}, {tournament.stateprov}")
            print(f"  Players: {tournament.player_count}")
    ```

### Location Filters

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Search by country and state
wa_tournaments: TournamentSearchResponse = (client.tournament.search("Championship")
    .country("US")
    .state("WA")
    .limit(25)
    .get())

# Search by city
portland_tournaments: TournamentSearchResponse = (client.tournament.search()
    .city("Portland")
    .state("OR")
    .country("US")
    .get())
```

### Date Range Filtering

Use the `.date_range()` method to filter tournaments by date. **Both dates are required** and must be in `YYYY-MM-DD` format:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.models.tournaments import TournamentSearchResponse
    from datetime import datetime, timedelta
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            # Search for tournaments in 2024
            results_2024: TournamentSearchResponse = await (client.tournament.search()
                .country("US")
                .date_range("2024-01-01", "2024-12-31")
                .get())

            # Find tournaments in a specific month
            jan_2024: TournamentSearchResponse = await (client.tournament.search()
                .date_range("2024-01-01", "2024-01-31")
                .country("US")
                .get())

            # Use Python datetime for dynamic ranges
            today: datetime = datetime.now()
            next_month: datetime = today + timedelta(days=30)

            upcoming: TournamentSearchResponse = await (client.tournament.search()
                .date_range(
                    today.strftime("%Y-%m-%d"),
                    next_month.strftime("%Y-%m-%d")
                )
                .country("US")
                .get())

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.models.tournaments import TournamentSearchResponse
    from datetime import datetime, timedelta

    with IfpaClient() as client:
        # Search for tournaments in 2024
        results_2024: TournamentSearchResponse = (client.tournament.search()
            .country("US")
            .date_range("2024-01-01", "2024-12-31")
            .get())

        # Find tournaments in a specific month
        jan_2024: TournamentSearchResponse = (client.tournament.search()
            .date_range("2024-01-01", "2024-01-31")
            .country("US")
            .get())

        # Use Python datetime for dynamic ranges
        today: datetime = datetime.now()
        next_month: datetime = today + timedelta(days=30)

        upcoming: TournamentSearchResponse = (client.tournament.search()
            .date_range(
                today.strftime("%Y-%m-%d"),
                next_month.strftime("%Y-%m-%d")
            )
            .country("US")
            .get())
    ```

### Tournament Type Filtering

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Find women's tournaments
women_tournaments: TournamentSearchResponse = (client.tournament.search()
    .country("US")
    .tournament_type("women")
    .limit(25)
    .get())

# Find youth tournaments
youth_tournaments: TournamentSearchResponse = (client.tournament.search()
    .tournament_type("youth")
    .limit(25)
    .get())
```

### Query Reuse with Date Ranges

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Create a reusable base query for 2024 tournaments
year_2024 = client.tournament.search().date_range("2024-01-01", "2024-12-31")

# Derive specific queries
us_2024: TournamentSearchResponse = year_2024.country("US").limit(100).get()
women_2024: TournamentSearchResponse = year_2024.tournament_type("women").get()
wa_2024: TournamentSearchResponse = year_2024.country("US").state("WA").get()

# Base query unchanged - can still be used
ca_2024: TournamentSearchResponse = year_2024.country("US").state("CA").get()
```

### Complex Tournament Queries

Combine multiple filters for precise searches:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Find all women's tournaments in the Pacific Northwest during 2024
pnw_women_2024: TournamentSearchResponse = (client.tournament.search()
    .country("US")
    .date_range("2024-01-01", "2024-12-31")
    .tournament_type("women")
    .limit(100)
    .get())

# Search for championship events in a specific city with date range
pdx_championships: TournamentSearchResponse = (client.tournament.search("Championship")
    .city("Portland")
    .state("OR")
    .country("US")
    .date_range("2024-01-01", "2024-12-31")
    .get())
```

### Tournament Query Methods

| Method | Parameter Type | Description |
|--------|----------------|-------------|
| `.search(name)` | `str` | Tournament name (partial match, case insensitive) |
| `.city(city)` | `str` | Filter by city name |
| `.state(stateprov)` | `str` | Filter by state/province code |
| `.country(country)` | `str` | Filter by country code (e.g., "US", "CA") |
| `.date_range(start, end)` | `str, str` | Date range filter (both required, YYYY-MM-DD format) |
| `.tournament_type(type)` | `str` | Tournament type (e.g., "open", "women", "youth") |
| `.offset(start_position)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute search and return results |
| `.first()` | - | Get first result (raises IndexError if none) |
| `.first_or_none()` | - | Get first result or None if empty |

## Error Handling

Handle errors gracefully when executing queries:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    from ifpa_api.core.exceptions import IfpaApiError, IfpaClientValidationError
    from ifpa_api.models.player import PlayerSearchResponse
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            try:
                # Valid query
                results: PlayerSearchResponse = await (client.player.search("Smith")
                    .country("US")
                    .state("ID")
                    .get())

                print(f"Found {len(results.search)} players")

            except IfpaClientValidationError as e:
                # Validation error (e.g., invalid date format)
                print(f"Invalid query parameters: {e}")

            except IfpaApiError as e:
                # API error
                print(f"API error [{e.status_code}]: {e.message}")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient
    from ifpa_api.core.exceptions import IfpaApiError, IfpaClientValidationError
    from ifpa_api.models.player import PlayerSearchResponse

    with IfpaClient() as client:
        try:
            # Valid query
            results: PlayerSearchResponse = (client.player.search("Smith")
                .country("US")
                .state("ID")
                .get())

            print(f"Found {len(results.search)} players")

        except IfpaClientValidationError as e:
            # Validation error (e.g., invalid date format)
            print(f"Invalid query parameters: {e}")

        except IfpaApiError as e:
            # API error
            print(f"API error [{e.status_code}]: {e.message}")
    ```

### Date Format Validation

The SDK validates date formats strictly:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaClientValidationError

client: IfpaClient = IfpaClient()

try:
    # Invalid date format - raises error
    results = (client.tournament.search()
        .date_range("01-01-2024", "12-31-2024")  # Wrong format!
        .get())
except IfpaClientValidationError as e:
    print(f"Date format must be YYYY-MM-DD: {e}")

# Correct date format
results = (client.tournament.search()
    .date_range("2024-01-01", "2024-12-31")  # Correct format
    .get())
```

## Advanced Query Patterns

### Building Dynamic Queries

Create queries programmatically based on user input:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

def search_players(
    name: str | None = None,
    country: str | None = None,
    state: str | None = None,
    limit: int = 25
) -> PlayerSearchResponse:
    """Search players with optional filters.

    Args:
        name: Player name to search for
        country: Country code filter
        state: State code filter
        limit: Maximum results

    Returns:
        Search results with type safety
    """
    # Start with base query
    query = client.player.search()

    # Add filters conditionally
    if name:
        query = query.search(name)
    if country:
        query = query.country(country)
    if state:
        query = query.state(state)

    # Execute with limit
    results: PlayerSearchResponse = query.limit(limit).get()
    return results

# Use the dynamic search function
results: PlayerSearchResponse = search_players(name="Smith", state="ID", limit=10)
```

### Query Templates

Create reusable query templates:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Template: US directors by state
def us_directors_by_state(state_code: str, limit: int = 25) -> DirectorSearchResponse:
    """Get directors from a specific US state.

    Args:
        state_code: Two-letter state code
        limit: Maximum results

    Returns:
        Directors from the specified state
    """
    results: DirectorSearchResponse = (client.director.search()
        .country("US")
        .state(state_code)
        .limit(limit)
        .get())
    return results

# Use the template
wa_directors: DirectorSearchResponse = us_directors_by_state("WA", limit=50)
or_directors: DirectorSearchResponse = us_directors_by_state("OR", limit=50)
```

### Aggregating Search Results

Collect results from multiple queries:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse, PlayerSearchResult

client: IfpaClient = IfpaClient()

# Search multiple states
states: list[str] = ["WA", "OR", "ID"]
all_players: list[PlayerSearchResult] = []

for state_code in states:
    results: PlayerSearchResponse = (client.player.search("Smith")
        .country("US")
        .state(state_code)
        .limit(10)
        .get())

    all_players.extend(results.search)
    print(f"Found {len(results.search)} Smiths in {state_code}")

print(f"\nTotal: {len(all_players)} players across {len(states)} states")
```

## Best Practices

### 1. Always Use Type Hints

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Good - type hint present
results: PlayerSearchResponse = client.player.search("Smith").get()

# Bad - no type hint (still works but loses IDE support)
results = client.player.search("Smith").get()
```

### 2. Store and Reuse Base Queries

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Good - reusable base query
us_query = client.player.search().country("US")
wa_players: PlayerSearchResponse = us_query.state("WA").get()
or_players: PlayerSearchResponse = us_query.state("OR").get()

# Bad - rebuilding query each time
wa_players = client.player.search().country("US").state("WA").get()
or_players = client.player.search().country("US").state("OR").get()
```

### 3. Use Descriptive Variable Names

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Good - clear intent
papa_winners: PlayerSearchResponse = (client.player.search()
    .tournament("PAPA")
    .position(1)
    .get())

# Bad - unclear purpose
results: PlayerSearchResponse = (client.player.search()
    .tournament("PAPA")
    .position(1)
    .get())
```

### 4. Validate User Input

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaClientValidationError
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

def search_tournaments_by_date(start_date: str, end_date: str) -> TournamentSearchResponse | None:
    """Search tournaments with date validation.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Search results or None if validation fails
    """
    try:
        results: TournamentSearchResponse = (client.tournament.search()
            .date_range(start_date, end_date)
            .get())
        return results
    except IfpaClientValidationError as e:
        print(f"Invalid date format: {e}")
        return None
```

### 5. Limit Result Set Sizes

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# Good - reasonable limit
results: PlayerSearchResponse = (client.player.search("Smith")
    .country("US")
    .limit(100)
    .get())

# Bad - no limit (may return thousands of results)
results: PlayerSearchResponse = (client.player.search("Smith")
    .country("US")
    .get())
```

## Known Limitations

### State/Province Filters

The API's state/province filter may occasionally return players from incorrect states. Always verify critical results manually.

### Tournament Search Performance

Large date ranges without other filters may timeout or return incomplete results. Always include at least one additional filter (country, tournament type, etc.) when using date ranges.

## Migration from Deprecated Methods

If you're migrating from the old `search()` methods:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.player import PlayerSearchResponse

client: IfpaClient = IfpaClient()

# OLD (deprecated):
results: PlayerSearchResponse = client.player.search(name="Smith", stateprov="ID")

# NEW (recommended):
results: PlayerSearchResponse = client.player.search("Smith").state("ID").get()

# OLD (deprecated):
results = client.director.search(name="Josh", country="US", stateprov="IL")

# NEW (recommended):
results = client.director.search("Josh").country("US").state("IL").get()
```

## Related Resources

- [Callable Pattern Guide](callable-pattern.md) - Individual resource operations
- [Pagination Guide](pagination.md) - Handling paginated results
- [Player Resource](../resources/players.md) - Complete player API reference
- [Director Resource](../resources/directors.md) - Complete director API reference
- [Tournament Resource](../resources/tournaments.md) - Complete tournament API reference
