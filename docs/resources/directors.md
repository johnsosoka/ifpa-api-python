# Director

The Director resource provides access to tournament director information, their tournament history, and country director assignments.

## Quick Example

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Fluent query builder - search for directors named "Josh" in the US
results: DirectorSearchResponse = client.director.query("Josh").country("US").get()
```

## Searching Directors (Fluent Query Builder)

The **recommended** way to search for directors is using the fluent query builder:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Simple name search
results: DirectorSearchResponse = client.director.query("Josh").get()
for director in results.directors:
    print(f"{director.director_id}: {director.name}")
    print(f"  Location: {director.city}, {director.stateprov}, {director.country_name}")
    print(f"  Tournaments Directed: {director.tournament_count}")

# Output:
# 1533: Josh Sharpe
#   Location: Chicago, IL, United States
#   Tournaments Directed: 45
```

### Chained Filters

The fluent API allows method chaining for complex queries:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Chain multiple filters
results: DirectorSearchResponse = (client.director.query("Sharpe")
    .country("US")
    .state("IL")
    .city("Chicago")
    .limit(25)
    .get())

# Location-only search (no name query)
results: DirectorSearchResponse = (client.director.query()
    .country("US")
    .state("IL")
    .limit(50)
    .get())

# Country filter with pagination
results: DirectorSearchResponse = (client.director.query()
    .country("US")
    .offset(0)
    .limit(100)
    .get())
```

### Query Reuse (Immutable Pattern)

The query builder is immutable - each method returns a new instance, allowing query reuse:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Create a reusable base query for US directors
us_query = client.director.query().country("US")

# Derive state-specific queries from the base
il_directors: DirectorSearchResponse = us_query.state("IL").limit(25).get()
or_directors: DirectorSearchResponse = us_query.state("OR").limit(25).get()
wa_directors: DirectorSearchResponse = us_query.state("WA").limit(25).get()

# The base query remains unchanged and can be reused
ca_directors: DirectorSearchResponse = us_query.state("CA").limit(25).get()
```

### Available Filters

| Method | Parameter | Description |
|--------|-----------|-------------|
| `.query(name)` | `str` | Director name (partial match, case insensitive) |
| `.city(city)` | `str` | City filter |
| `.state(stateprov)` | `str` | State/province code (e.g., "IL", "WA") |
| `.country(code)` | `str` | Country name or code (e.g., "US", "CA") |
| `.offset(start_position)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute query and return results |

!!! note "Deprecated Methods"
    The old `client.director.search(name="Josh")` method is deprecated and will be removed in v1.0.0.
    Use the fluent query builder instead: `client.director.query("Josh").get()`

## Individual Director Operations

Access individual director information using the callable pattern. These methods are **not deprecated**.

### Get Director Details

Retrieve detailed information about a specific tournament director:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import Director

client: IfpaClient = IfpaClient()

# Get director by ID - Josh Rainwater (1533) from Columbia, SC
director: Director = client.director(1533).details()

print(f"Name: {director.name}")
print(f"Director ID: {director.director_id}")
print(f"Location: {director.city}, {director.stateprov}, {director.country_name}")

# Access director statistics
if director.stats:
    print(f"\nDirector Statistics:")
    print(f"  Total Tournaments: {director.stats.tournament_count}")
    print(f"  Unique Venues: {director.stats.unique_location_count}")
    print(f"  Total Players: {director.stats.total_player_count}")
    print(f"  Unique Players: {director.stats.unique_player_count}")
    print(f"  Largest Event: {director.stats.largest_event_count} players")
    print(f"  Average Tournament Value: {director.stats.average_value}")
    print(f"  Highest Tournament Value: {director.stats.highest_value}")

# Output:
# Name: Josh Rainwater
# Director ID: 1533
# Location: Columbia, SC, United States
#
# Director Statistics:
#   Total Tournaments: 13
#   Unique Venues: 1
#   Total Players: 347
#   Unique Players: 120
#   Largest Event: 41 players
#   Average Tournament Value: 5.89
#   Highest Tournament Value: 11.82
```

#### Director Profile Information

Director profiles include:

- **Identity**: Name, director ID, profile photo
- **Location**: City, state/province, country
- **Social**: Twitch username (if available)
- **Statistics**: Tournament count, player statistics, format usage
  - Tournament counts (total, women's, league)
  - Player metrics (total, unique, first-time, repeat)
  - Venue count
  - Format breakdown (single, multiple, unknown)
  - Tournament values (highest, average)

#### Invalid Director IDs

When requesting a non-existent director, the SDK raises an error:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError

client: IfpaClient = IfpaClient()

try:
    director = client.director(99999999).details()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Director not found")
```

### Get Director's Tournaments

Access a director's tournament history:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import DirectorTournamentsResponse

client: IfpaClient = IfpaClient()

# Get past tournaments for Josh Rainwater (1533)
past: DirectorTournamentsResponse = client.director(1533).tournaments(TimePeriod.PAST)

print(f"Director: {past.director_name}")
print(f"Total past tournaments: {past.total_count}")

for tournament in past.tournaments[:3]:  # Show first 3
    print(f"\n{tournament.tournament_name}")
    print(f"  Date: {tournament.event_date}")
    print(f"  Location: {tournament.location_name}")
    print(f"  City: {tournament.city}, {tournament.stateprov}")
    print(f"  Players: {tournament.player_count}")
    print(f"  Value: {tournament.value}")

# Output:
# Director: Josh Rainwater
# Total past tournaments: 13
#
# South Carolina Pinball Championship
#   Date: 2024-03-16
#   Location: Cinnebarre
#   City: Columbia, SC
#   Players: 41
#   Value: 11.82
```

#### Get Upcoming Tournaments

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import DirectorTournamentsResponse

client: IfpaClient = IfpaClient()

# Get future tournaments for Josh Rainwater (1533)
upcoming: DirectorTournamentsResponse = client.director(1533).tournaments(TimePeriod.FUTURE)

print(f"Upcoming tournaments: {upcoming.total_count}")

for tournament in upcoming.tournaments:
    print(f"\n{tournament.tournament_name}")
    print(f"  Start: {tournament.event_date}")
    print(f"  End: {tournament.event_end_date}")
    print(f"  Location: {tournament.location_name}")
    print(f"  Ranking System: {tournament.ranking_system}")
```

#### Working with Highly Active Directors

For directors with extensive history, use the same pattern:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import Director, DirectorTournamentsResponse

client: IfpaClient = IfpaClient()

# Get highly active director - Erik Thoren (1151)
# 545 tournaments, 1,658 unique players, De Pere, WI
director: Director = client.director(1151).details()

print(f"{director.name}")
print(f"  Tournaments: {director.stats.tournament_count}")
print(f"  Unique Players: {director.stats.unique_player_count}")
print(f"  Highest Value: {director.stats.highest_value}")
print(f"  Location: {director.city}, {director.stateprov}")

# Get future events
future: DirectorTournamentsResponse = client.director(1151).tournaments(TimePeriod.FUTURE)
print(f"  Upcoming Events: {future.total_count}")
```

#### Handling Empty Results

Some directors may have no future tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import DirectorTournamentsResponse

client: IfpaClient = IfpaClient()

# Check for empty tournament lists
future: DirectorTournamentsResponse = client.director(1752).tournaments(TimePeriod.FUTURE)

if future.total_count == 0 or not future.tournaments:
    print("No upcoming tournaments")
else:
    print(f"Found {future.total_count} upcoming tournaments")
```

#### Tournament Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time_period` | `TimePeriod` | Yes | `TimePeriod.PAST` or `TimePeriod.FUTURE` |

#### Tournament Information

Each tournament includes:

- **Identity**: Tournament ID, name, event name
- **Dates**: Event start date, end date
- **Location**: Venue name, city, state/province, country
- **Format**: Qualifying format, finals format
- **Details**: Ranking system, player count, tournament value
- **Special**: Women-only flag

## Country Directors

Get the list of IFPA country directors:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import CountryDirectorsResponse

client: IfpaClient = IfpaClient()

# Get all country directors
country_dirs: CountryDirectorsResponse = client.director.country_directors()

print(f"Total country directors: {country_dirs.count}")

for director in country_dirs.country_directors[:5]:  # Show first 5
    profile = director.player_profile
    print(f"\n{profile.country_name} ({profile.country_code})")
    print(f"  Director: {profile.name}")
    print(f"  Player ID: {profile.player_id}")
```

### Country Director Information

Each country director includes a nested `player_profile` with:

- **Identity**: Player ID, name
- **Country**: Country code, country name
- **Profile**: Profile photo URL

Note: Access director information through the `player_profile` field:

```python
profile = director.player_profile
print(f"{profile.name} - {profile.country_name}")
```

## Complete Example: Director Analysis

Here's a complete example that analyzes a director's activity:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.common import TimePeriod
from ifpa_api.models.director import Director, DirectorTournamentsResponse


def analyze_director(director_id: int = 1533) -> None:
    """Comprehensive director analysis.

    Default director: Josh Rainwater (1533) - active director from Columbia, SC
    """
    client: IfpaClient = IfpaClient()

    try:
        # Get director profile
        director: Director = client.director(director_id).details()

        print("=" * 60)
        print(f"{director.name}")
        print("=" * 60)

        # Basic info
        print(f"\nLocation: {director.city}, {director.stateprov}, {director.country_name}")
        print(f"Director ID: {director.director_id}")

        # Statistics
        if director.stats:
            stats = director.stats
            print(f"\nTournament Activity:")
            print(f"  Total Tournaments: {stats.tournament_count}")
            print(f"  Women's Tournaments: {stats.women_tournament_count}")
            print(f"  League Events: {stats.league_count}")
            print(f"  Unique Venues: {stats.unique_location_count}")

            print(f"\nPlayer Engagement:")
            print(f"  Total Participations: {stats.total_player_count}")
            print(f"  Unique Players: {stats.unique_player_count}")
            print(f"  First-Time Players: {stats.first_time_player_count}")
            print(f"  Repeat Players: {stats.repeat_player_count}")
            print(f"  Largest Event: {stats.largest_event_count} players")

            print(f"\nTournament Quality:")
            print(f"  Average Value: {stats.average_value:.2f}")
            print(f"  Highest Value: {stats.highest_value:.2f}")

            # Format breakdown
            if stats.formats:
                print(f"\nFormat Usage:")
                for fmt in stats.formats[:5]:
                    print(f"  {fmt.name}: {fmt.count} tournaments")

        # Get recent past tournaments
        past: DirectorTournamentsResponse = client.director(director_id).tournaments(TimePeriod.PAST)

        print(f"\nRecent Past Tournaments ({past.total_count} total):")
        for tournament in past.tournaments[:5]:
            print(f"\n  {tournament.tournament_name}")
            print(f"    Date: {tournament.event_date}")
            print(f"    Players: {tournament.player_count}")
            if tournament.value:
                print(f"    Value: {tournament.value:.2f}")

        # Get upcoming tournaments
        future: DirectorTournamentsResponse = client.director(director_id).tournaments(TimePeriod.FUTURE)

        if future.total_count and future.total_count > 0:
            print(f"\nUpcoming Tournaments ({future.total_count}):")
            for tournament in future.tournaments[:3]:
                print(f"\n  {tournament.tournament_name}")
                print(f"    Start: {tournament.event_date}")
                print(f"    Location: {tournament.location_name}")
        else:
            print(f"\nNo upcoming tournaments scheduled")

    except IfpaApiError as e:
        if e.status_code == 404:
            print(f"Director {director_id} not found")
        else:
            print(f"API error: {e}")


if __name__ == "__main__":
    # Analyze Josh Rainwater - active director
    analyze_director(1533)
```

## Best Practices

### Error Handling

Always handle potential errors:

```python
from ifpa_api import IfpaClient
from ifpa_api.core.exceptions import IfpaApiError
from ifpa_api.models.director import Director

client: IfpaClient = IfpaClient()

try:
    director: Director = client.director(999999).details()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Director not found")
    else:
        print(f"API error: {e}")
```

### Reusable Queries

Take advantage of the immutable query builder pattern:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Create a base query for US directors
us_query = client.director.query().country("US")

# Derive specific state queries
il_directors: DirectorSearchResponse = us_query.state("IL").limit(50).get()
wa_directors: DirectorSearchResponse = us_query.state("WA").limit(50).get()
or_directors: DirectorSearchResponse = us_query.state("OR").limit(50).get()
```

### Working with Country Directors

Find a specific country's director:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import CountryDirectorsResponse

client: IfpaClient = IfpaClient()

country_dirs: CountryDirectorsResponse = client.director.country_directors()

# Find director for a specific country
target_country = "US"
country_director = next(
    (d for d in country_dirs.country_directors if d.player_profile.country_code == target_country),
    None
)

if country_director:
    print(f"Country Director for {target_country}: {country_director.player_profile.name}")
else:
    print(f"No director found for {target_country}")
```

### Working with International Directors

Access directors from any country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import Director

client: IfpaClient = IfpaClient()

# Get international director - Michael Trepp (1071) from Switzerland
director: Director = client.director(1071).details()

print(f"{director.name}")
print(f"  Country: {director.country_name} ({director.country_code})")
print(f"  Tournaments: {director.stats.tournament_count}")
print(f"  Unique Players: {director.stats.unique_player_count}")
```

## Deprecated Methods

!!! warning "Deprecated in v0.2.0"
    The `search()` method is deprecated and will be removed in v1.0.0. Use the fluent query builder instead.

### Old Search Method

The old `search()` method still works but emits deprecation warnings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# DEPRECATED - Emits DeprecationWarning
results: DirectorSearchResponse = client.director.search(name="Josh")

# DEPRECATED - Multiple filters
results: DirectorSearchResponse = client.director.search(
    name="Josh",
    city="Chicago",
    stateprov="IL",
    country="US"
)
```

### Migration Guide

Migrate to the new fluent API:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.director import DirectorSearchResponse

client: IfpaClient = IfpaClient()

# Old (deprecated):
results: DirectorSearchResponse = client.director.search(name="Josh", country="US")

# New (recommended):
results: DirectorSearchResponse = client.director.query("Josh").country("US").get()

# Old (deprecated):
results: DirectorSearchResponse = client.director.search(
    name="Sharpe",
    city="Chicago",
    stateprov="IL",
    country="US"
)

# New (recommended):
results: DirectorSearchResponse = (client.director.query("Sharpe")
    .city("Chicago")
    .state("IL")
    .country("US")
    .get())
```

### Benefits of the New API

- **Type-safe**: Better IDE autocomplete and type checking
- **Composable**: Chain methods in any order
- **Reusable**: Immutable pattern allows query reuse
- **Readable**: Fluent interface is more intuitive
- **Flexible**: Can start with filters only (no name required)

## Related Resources

- [Tournaments](tournaments.md) - View tournament details and results
- [Player](players.md) - View player profiles and statistics
- [Error Handling](../guides/error-handling.md) - Handle API errors
