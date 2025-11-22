# Tournament

Search for tournaments and access detailed tournament information, results, formats, and submission history.

## Quick Example

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Fluent query builder - search for PAPA tournaments in Pennsylvania
results: TournamentSearchResponse = client.tournament.query("PAPA").state("PA").get()
```

## Searching Tournaments (Fluent Query Builder)

The **recommended** way to search for tournaments is using the fluent query builder:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Simple name search
results: TournamentSearchResponse = client.tournament.query("PAPA").get()

print(f"Found {len(results.tournaments)} tournaments")
for tournament in results.tournaments:
    print(f"{tournament.tournament_name} - {tournament.event_date}")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
    print(f"  Players: {tournament.player_count}")
```

### Chained Filters

The fluent API allows method chaining for complex queries:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Chain multiple filters
results: TournamentSearchResponse = (client.tournament.query("Championship")
    .country("US")
    .state("WA")
    .limit(25)
    .get())

# Location-only search (no name query)
results: TournamentSearchResponse = (client.tournament.query()
    .city("Portland")
    .state("OR")
    .get())

# Filter by tournament type (using enum - preferred)
from ifpa_api import TournamentSearchType

results: TournamentSearchResponse = (client.tournament.query()
    .country("US")
    .tournament_type(TournamentSearchType.WOMEN)
    .limit(25)
    .get())

# Using strings (backwards compatible)
results_str: TournamentSearchResponse = (client.tournament.query()
    .country("US")
    .tournament_type("women")
    .limit(25)
    .get())
```

## Date Range Filtering

Use the `.date_range()` method to filter tournaments by date. **Both dates are required** and must be in `YYYY-MM-DD` format:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Search for tournaments in 2024
results: TournamentSearchResponse = (client.tournament.query()
    .country("US")
    .date_range("2024-01-01", "2024-12-31")
    .get())

# Find upcoming tournaments
from datetime import datetime, timedelta

today = datetime.now()
next_month = today + timedelta(days=30)

upcoming: TournamentSearchResponse = (client.tournament.query()
    .date_range(
        today.strftime("%Y-%m-%d"),
        next_month.strftime("%Y-%m-%d")
    )
    .get())
```

!!! warning "Date Format Validation"
    The SDK validates date format strictly. Dates must be in `YYYY-MM-DD` format.
    Invalid formats raise `IfpaClientValidationError`:

    ```python
    from ifpa_api import IfpaClient, IfpaClientValidationError

    client: IfpaClient = IfpaClient()

    try:
        # Invalid format - raises error
        results = client.tournament.query().date_range("01-01-2024", "12-31-2024").get()
    except IfpaClientValidationError as e:
        print(f"Invalid date format: {e}")
    ```

### Query Reuse (Immutable Pattern)

The query builder is immutable - each method returns a new instance, allowing query reuse:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Create a reusable base query for US tournaments
us_query = client.tournament.query().country("US")

# Derive state-specific queries from the base
wa_tournaments: TournamentSearchResponse = us_query.state("WA").limit(25).get()
or_tournaments: TournamentSearchResponse = us_query.state("OR").limit(25).get()
id_tournaments: TournamentSearchResponse = us_query.state("ID").limit(25).get()

# The base query remains unchanged and can be reused
ca_tournaments: TournamentSearchResponse = us_query.state("CA").limit(25).get()

# Create a reusable date range query
from ifpa_api import TournamentSearchType

year_2024 = client.tournament.query().date_range("2024-01-01", "2024-12-31")
us_2024 = year_2024.country("US").get()
women_2024 = year_2024.tournament_type(TournamentSearchType.WOMEN).get()
```

## Available Filters

The fluent query builder provides these methods:

| Method | Parameter | Description |
|--------|-----------|-------------|
| `.query(name)` | `str` | Tournament name (partial match, case insensitive) |
| `.city(city)` | `str` | Filter by city name |
| `.state(stateprov)` | `str` | Filter by state/province code |
| `.country(country)` | `str` | Filter by country code (e.g., "US", "CA") |
| `.date_range(start, end)` | `str, str` | Date range filter (both required, YYYY-MM-DD format) |
| `.tournament_type(type)` | `TournamentSearchType \| str` | Tournament type (`TournamentSearchType.OPEN`, `WOMEN`, `YOUTH`, `LEAGUE` or strings) |
| `.offset(start_position)` | `int` | Pagination offset (0-based) |
| `.limit(count)` | `int` | Maximum number of results |
| `.get()` | - | Execute query and return results |

!!! info "Migration from 0.2.x"
    The `client.tournament.search(name="PAPA")` method was removed in v0.3.0.
    Use the fluent query builder instead: `client.tournament.query("PAPA").get()`

!!! success "State Filter Works Correctly"
    Tournament search uses **exact matching** for state/province filtering, unlike player and director search which have a substring matching bug. You can reliably filter tournaments by state code without false positives.

    See [Known Limitations](../guides/known-limitations.md#stateprovince-filter-broken) for details on the player/director state filter bug.

## Complex Query Examples

Combine multiple filters for precise searches:

```python
from ifpa_api import IfpaClient, TournamentSearchType
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Find all women's tournaments in the Pacific Northwest during 2024
results: TournamentSearchResponse = (client.tournament.query()
    .country("US")
    .date_range("2024-01-01", "2024-12-31")
    .tournament_type(TournamentSearchType.WOMEN)
    .limit(100)
    .get())

# Search for championship events in a specific city
results: TournamentSearchResponse = (client.tournament.query("Championship")
    .city("Portland")
    .state("OR")
    .get())

# Find recent tournaments with pagination
results: TournamentSearchResponse = (client.tournament.query()
    .date_range("2024-11-01", "2024-11-30")
    .country("US")
    .offset(0)
    .limit(50)
    .get())
```

## Get Tournament Details

Retrieve detailed information about a specific tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament

client: IfpaClient = IfpaClient()

# Get PAPA 17 tournament details (tournament ID 7070)
tournament: Tournament = client.tournament(7070).details()

print(f"Name: {tournament.tournament_name}")
print(f"Event: {tournament.event_name}")
print(f"Location: {tournament.city}, {tournament.stateprov}, {tournament.country_name}")
print(f"Venue: {tournament.location_name}")
print(f"Date: {tournament.event_date}")
print(f"Players: {tournament.player_count}")
print(f"Machines: {tournament.machine_count}")
print(f"Director: {tournament.director_name}")
print(f"WPPR Value: {tournament.wppr_value}")
print(f"Rating: {tournament.rating_value}")
```

### Tournament Information

Tournament details include:

- **Basic Info**: Name, event name, tournament type
- **Location**: Venue name, address, city, state, country, coordinates
- **Schedule**: Event date, start date, end date
- **Details**: Player count, machine count, director information
- **Scoring**: WPPR value, rating value
- **Registration**: Entry fee, prize pool, private flag
- **Links**: Tournament website, additional details

## Get Tournament Results

Access complete tournament standings and player results:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentResultsResponse

client: IfpaClient = IfpaClient()

# Get PAPA 17 results
results: TournamentResultsResponse = client.tournament(7070).results()

print(f"Tournament: {results.tournament_name}")
print(f"Date: {results.event_date}")
print(f"Players: {results.player_count}")
print("\nTop 10 Finishers:")

for result in results.results[:10]:
    print(f"{result.position}. {result.player_name} ({result.city}, {result.stateprov})")
    if result.points:
        print(f"   WPPR: {result.points:.2f}", end="")
    if result.ratings_value:
        print(f" | Rating: {result.ratings_value:.2f}", end="")
    print()
```

### Result Details

Each result includes:

- **Placement**: Position, percentile
- **Player Info**: Player ID, name, location
- **Points**: WPPR points earned, rating value earned
- **Performance**: Best game finish, total player tournaments

## Get Tournament Formats

Retrieve format information for a specific tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsResponse

client: IfpaClient = IfpaClient()

# Get PAPA 17 format information
formats: TournamentFormatsResponse = client.tournament(7070).formats()

print(f"Tournament ID: {formats.tournament_id}")
print(f"Formats used: {len(formats.formats)}")

for fmt in formats.formats:
    print(f"\nFormat: {fmt.format_name}")
    print(f"  Rounds: {fmt.rounds}")
    print(f"  Games per round: {fmt.games_per_round}")
    print(f"  Players: {fmt.player_count}")
    if fmt.machine_list:
        print(f"  Machines: {', '.join(fmt.machine_list[:5])}")
    if fmt.details:
        print(f"  Details: {fmt.details}")
```

### Format Information

Format data includes:

- **Format Type**: Swiss, Match Play, Strike Knockout, etc.
- **Structure**: Number of rounds, games per round
- **Participation**: Player count for this format
- **Machines**: List of machines used
- **Additional Details**: Format-specific rules and notes

## List All Format Types

Get a comprehensive list of all available tournament format types:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsListResponse

client: IfpaClient = IfpaClient()

# Get all tournament formats
formats: TournamentFormatsListResponse = client.tournament.list_formats()

print(f"Qualifying formats ({len(formats.qualifying_formats)}):")
for fmt in formats.qualifying_formats:
    print(f"  {fmt.format_id}: {fmt.name}")
    if fmt.description:
        print(f"    {fmt.description}")

print(f"\nFinals formats ({len(formats.finals_formats)}):")
for fmt in formats.finals_formats:
    print(f"  {fmt.format_id}: {fmt.name}")
    if fmt.description:
        print(f"    {fmt.description}")
```

## Get Related Tournaments

Find tournaments related to a specific tournament (same venue or series):

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import RelatedTournamentsResponse

client: IfpaClient = IfpaClient()

# Get related tournaments for PAPA 17
related: RelatedTournamentsResponse = client.tournament(7070).related()

print(f"Found {len(related.tournament)} related tournaments")
for t in related.tournament:
    print(f"\n{t.event_start_date}: {t.tournament_name}")
    print(f"  Type: {t.tournament_type}")
    print(f"  Event: {t.event_name}")
    if t.winner:
        print(f"  Winner: {t.winner.name} ({t.winner.country_name})")
```

## Get League Information

For tournaments that are part of a league, retrieve league session data:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentLeagueResponse

client: IfpaClient = IfpaClient()

# Get league data (if tournament is part of a league)
league: TournamentLeagueResponse = client.tournament(12345).league()

print(f"Tournament ID: {league.tournament_id}")
print(f"League Format: {league.league_format}")
print(f"Total Sessions: {league.total_sessions}")
print("\nSession Details:")

for session in league.sessions:
    print(f"\n{session.session_date}")
    print(f"  Players: {session.player_count}")
    if session.session_value:
        print(f"  WPPR Value: {session.session_value}")
```

### League Session Data

League information includes:

- **Format**: League format description
- **Sessions**: Individual session data
- **Session Details**: Date, player count, WPPR value
- **Total Count**: Total number of sessions

## Get Tournament Submissions

Access submission history and status for a tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSubmissionsResponse

client: IfpaClient = IfpaClient()

# Get submission information
submissions: TournamentSubmissionsResponse = client.tournament(7070).submissions()

print(f"Tournament ID: {submissions.tournament_id}")
print(f"Total Submissions: {len(submissions.submissions)}")

for submission in submissions.submissions:
    print(f"\nSubmission ID: {submission.submission_id}")
    if submission.submission_date:
        print(f"  Date: {submission.submission_date}")
    if submission.submitter_name:
        print(f"  Submitter: {submission.submitter_name}")
    if submission.status:
        print(f"  Status: {submission.status}")
    if submission.details:
        print(f"  Details: {submission.details}")
```

### Submission Information

Submission data includes:

- **Submission ID**: Unique identifier
- **Submission Date**: When results were submitted
- **Submitter**: Name of person who submitted
- **Status**: Current submission status
- **Details**: Additional submission information

## Complete Example: Tournament Analysis

Here's a complete example that analyzes a tournament comprehensively:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.tournaments import (
    Tournament,
    TournamentResultsResponse,
    TournamentFormatsResponse,
)


def analyze_tournament(tournament_id: int = 7070) -> None:
    """Comprehensive tournament analysis.

    Default tournament: PAPA 17 (7070)
    """
    client: IfpaClient = IfpaClient()

    try:
        # Get tournament details
        tournament: Tournament = client.tournament(tournament_id).details()

        print("=" * 60)
        print(f"{tournament.tournament_name}")
        print("=" * 60)

        # Basic info
        print(f"\nEvent: {tournament.event_name}")
        print(f"Location: {tournament.location_name}")
        print(f"  {tournament.city}, {tournament.stateprov}, {tournament.country_name}")
        print(f"Date: {tournament.event_date}")

        # Tournament details
        print(f"\nTournament Details:")
        print(f"  Type: {tournament.tournament_type}")
        print(f"  Players: {tournament.player_count}")
        print(f"  Machines: {tournament.machine_count}")
        print(f"  Director: {tournament.director_name}")
        print(f"  WPPR Value: {tournament.wppr_value}")
        print(f"  Rating Value: {tournament.rating_value}")

        # Get formats
        formats: TournamentFormatsResponse = client.tournament(tournament_id).formats()
        print(f"\nFormats Used:")
        for fmt in formats.formats:
            print(f"  - {fmt.format_name}: {fmt.rounds} rounds, {fmt.games_per_round} games/round")

        # Get results
        results: TournamentResultsResponse = client.tournament(tournament_id).results()
        print(f"\nTop 5 Finishers:")
        for result in results.results[:5]:
            wppr = result.points if result.points else 0
            print(f"  {result.position}. {result.player_name} - {wppr:.2f} WPPR")

        # Calculate statistics
        if results.results:
            avg_wppr = sum(r.points or 0 for r in results.results) / len(results.results)
            print(f"\nStatistics:")
            print(f"  Average WPPR: {avg_wppr:.2f}")
            print(f"  Total Finishers: {len(results.results)}")

    except IfpaApiError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Analyze PAPA 17 (tournament ID 7070)
    analyze_tournament(7070)
```

## Best Practices

### Error Handling

Always handle potential errors when accessing tournament data:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.tournaments import Tournament

client: IfpaClient = IfpaClient()

try:
    tournament: Tournament = client.tournament(999999).details()
    print(f"Found: {tournament.tournament_name}")
except IfpaApiError as e:
    if e.status_code == 404:
        print("Tournament not found")
    else:
        print(f"API error: {e}")
```

### Reusable Queries

Take advantage of the immutable query builder pattern:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()

# Create a base query for 2024 tournaments
year_2024 = client.tournament.query().date_range("2024-01-01", "2024-12-31")

# Derive specific queries
us_tournaments: TournamentSearchResponse = year_2024.country("US").limit(100).get()
women_tournaments: TournamentSearchResponse = year_2024.tournament_type("women").get()
ca_tournaments: TournamentSearchResponse = year_2024.country("CA").limit(100).get()
```

### Pagination for Large Result Sets

Use pagination when searching for tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client: IfpaClient = IfpaClient()


def get_all_tournaments(name: str, page_size: int = 100):
    """Get all tournaments matching a name with pagination."""
    all_tournaments = []
    start_pos = 0

    while True:
        results: TournamentSearchResponse = (client.tournament.query(name)
            .offset(start_pos)
            .limit(page_size)
            .get())

        if not results.tournaments:
            break

        all_tournaments.extend(results.tournaments)
        start_pos += page_size

        # Stop if we've retrieved all results
        if results.total_results and len(all_tournaments) >= results.total_results:
            break

    return all_tournaments


# Get all "Championship" tournaments
championships = get_all_tournaments("Championship")
print(f"Found {len(championships)} championship tournaments")
```

## Migration from 0.2.x

!!! info "Migration from 0.2.x"
    The `search()` method was removed in v0.3.0. Use the fluent query builder instead:

    ```python
    # Old (0.2.x):
    results: TournamentSearchResponse = client.tournament.search(name="PAPA")

    # New (0.3.0+):
    results: TournamentSearchResponse = client.tournament.query("PAPA").get()
    ```

    Complex queries with filters:

    ```python
    # Old (0.2.x):
    results = client.tournament.search(
        name="Championship",
        city="Portland",
        stateprov="OR",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )

    # New (0.3.0+):
    results = client.tournament.query("Championship") \
        .city("Portland") \
        .state("OR") \
        .date_range("2024-01-01", "2024-12-31") \
        .get()
    ```

    The query builder is immutable and chainable, enabling query reuse and better type safety.

## Related Resources

- [Director](directors.md) - View tournament directors
- [Player](players.md) - View player profiles and results
- [Series](series.md) - Tournament series information
- [Error Handling](../guides/error-handling.md) - Handle API errors
