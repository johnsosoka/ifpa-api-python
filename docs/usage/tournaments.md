# Tournament

Search for tournaments and access detailed tournament information, results, formats, and submission history.

## Callable Pattern

The Tournament resource uses a callable pattern for accessing both collection-level and resource-level operations:

```python
from ifpa_api import IfpaClient

client = IfpaClient()

# Collection operations on client.tournament
search_results = client.tournament.search(name="PAPA")
formats = client.tournament.list_formats()

# Individual tournament operations via callable pattern
tournament = client.tournament(7070).details()
results = client.tournament(7070).results()
```

## Search for Tournaments

Search for tournaments by name, location, date range, or tournament type.

!!! warning "Date Range Requirement"
    When using date filters, you **must** provide both `start_date` and `end_date` together.
    The API requires both dates or neither. Providing only one will result in a `ValueError`.

### Basic Search

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

tournaments: TournamentSearchResponse = client.tournament.search(name="PAPA")
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Search for PAPA tournaments
tournaments: TournamentSearchResponse = client.tournament.search(name="PAPA", count=10)

print(f"Found {len(tournaments.tournaments)} PAPA tournaments")
for t in tournaments.tournaments:
    print(f"{t.tournament_name} - {t.event_date}")
    print(f"  Location: {t.city}, {t.stateprov}")
    print(f"  Players: {t.player_count}, Rating: {t.rating_value}")
```

### Search with Filters

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Search by location and date range (BOTH dates required)
results: TournamentSearchResponse = client.tournament.search(
    city="Portland",
    stateprov="OR",
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Search by location and date range (BOTH dates required)
results: TournamentSearchResponse = client.tournament.search(
    city="Portland",
    stateprov="OR",
    start_date="2024-01-01",
    end_date="2024-12-31",
    count=50
)

print(f"Found {len(results.tournaments)} tournaments in Portland, OR")
for t in results.tournaments:
    print(f"\n{t.tournament_name}")
    print(f"  Date: {t.event_date}")
    print(f"  Players: {t.player_count}")
    print(f"  Rating: {t.rating_value}")

# Search women's tournaments only
women_tournaments: TournamentSearchResponse = client.tournament.search(
    tournament_type="women",
    country="US",
    count=25
)

print(f"\n\nFound {len(women_tournaments.tournaments)} women's tournaments")
```

### Search Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | No | Tournament name (partial match) |
| `city` | `str` | No | Filter by city |
| `stateprov` | `str` | No | Filter by state/province code |
| `country` | `str` | No | Filter by country code (e.g., "US") |
| `start_date` | `str` | No* | Filter by start date (YYYY-MM-DD format) |
| `end_date` | `str` | No* | Filter by end date (YYYY-MM-DD format) |
| `tournament_type` | `str` | No | Filter by type ("open", "women", etc.) |
| `start_pos` | `int` | No | Starting position for pagination |
| `count` | `int` | No | Number of results to return |

*Must be provided together - both required or both omitted

## Get Tournament Details

Retrieve detailed information about a specific tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament

client = IfpaClient()

tournament: Tournament = client.tournament(7070).details()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament

client = IfpaClient()

# Get PAPA 17 tournament details
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

client = IfpaClient()

results: TournamentResultsResponse = client.tournament(7070).results()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentResultsResponse

client = IfpaClient()

# Get PAPA 17 results
results: TournamentResultsResponse = client.tournament(7070).results()

print(f"Tournament: {results.tournament_name}")
print(f"Date: {results.event_date}")
print(f"Players: {results.player_count}")
print("\nTop 10 Finishers:")

for result in results.results[:10]:
    print(f"{result.position}. {result.player_name} ({result.city}, {result.stateprov})")
    if result.wppr_points:
        print(f"   WPPR: {result.wppr_points:.2f}", end="")
    if result.rating_points:
        print(f" | Rating: {result.rating_points:.2f}", end="")
    print()
```

### Result Details

Each result includes:

- **Placement**: Position, percentile
- **Player Info**: Player ID, name, location
- **Points**: WPPR points earned, rating points earned
- **Performance**: Best game finish, total events

## Get Tournament Formats

Retrieve format information for a specific tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsResponse

client = IfpaClient()

formats: TournamentFormatsResponse = client.tournament(7070).formats()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsResponse

client = IfpaClient()

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

client = IfpaClient()

formats: TournamentFormatsListResponse = client.tournament.list_formats()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsListResponse

client = IfpaClient()

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

# Find a specific format
swiss = next(
    (f for f in formats.qualifying_formats if "swiss" in f.name.lower()),
    None
)
if swiss:
    print(f"\nSwiss format ID: {swiss.format_id}")
```

## Get Related Tournaments

Find tournaments related to a specific tournament (same venue or series):

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import RelatedTournamentsResponse

client = IfpaClient()

related: RelatedTournamentsResponse = client.tournament(7070).related()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import RelatedTournamentsResponse

client = IfpaClient()

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

client = IfpaClient()

league: TournamentLeagueResponse = client.tournament(12345).league()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentLeagueResponse

client = IfpaClient()

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

client = IfpaClient()

submissions: TournamentSubmissionsResponse = client.tournament(7070).submissions()
```

**Complete Example:**

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSubmissionsResponse

client = IfpaClient()

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


def analyze_tournament(tournament_id: int) -> None:
    """Comprehensive tournament analysis."""
    client = IfpaClient()

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
            wppr = result.wppr_points if result.wppr_points else 0
            print(f"  {result.position}. {result.player_name} - {wppr:.2f} WPPR")

        # Calculate statistics
        if results.results:
            avg_wppr = sum(r.wppr_points or 0 for r in results.results) / len(results.results)
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

### Date Range Searches

When searching by date, always provide both dates in ISO format (YYYY-MM-DD):

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# CORRECT: Both dates provided
results: TournamentSearchResponse = client.tournament.search(
    start_date="2024-01-01",
    end_date="2024-12-31",
    country="US"
)

# INCORRECT: Only one date - raises ValueError
try:
    results = client.tournament.search(start_date="2024-01-01")
except ValueError as e:
    print(f"Error: {e}")

# Get upcoming tournaments
from datetime import datetime, timedelta

today = datetime.now()
next_month = today + timedelta(days=30)

upcoming: TournamentSearchResponse = client.tournament.search(
    start_date=today.strftime("%Y-%m-%d"),
    end_date=next_month.strftime("%Y-%m-%d")
)
```

### Error Handling

Always handle potential errors when accessing tournament data:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.tournaments import Tournament

client = IfpaClient()

try:
    tournament: Tournament = client.tournament(999999).details()
    print(f"Found: {tournament.tournament_name}")
except IfpaApiError as e:
    if e.status_code == 404:
        print("Tournament not found")
    else:
        print(f"API error: {e}")
```

### Pagination for Large Result Sets

Use pagination when searching for tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()


def get_all_tournaments(name: str, page_size: int = 100):
    """Get all tournaments matching a name with pagination."""
    all_tournaments = []
    start_pos = 0

    while True:
        results: TournamentSearchResponse = client.tournament.search(
            name=name,
            start_pos=start_pos,
            count=page_size
        )

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

## Related Resources

- [Director](director.md) - View tournament directors
- [Player](player.md) - View player profiles and results
- [Series](series.md) - Tournament series information
- [Error Handling](error-handling.md) - Handle API errors
