# Tournaments

Search for tournaments and access detailed tournament information, results, formats, and submission history.

## Search for Tournaments

Search for tournaments by name, location, date range, or tournament type:

```python
from ifpa_api import IfpaClient

client = IfpaClient()

# Simple name search
tournaments = client.tournaments.search(name="Pinball")
for tournament in tournaments.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")
    print(f"  Location: {tournament.city}, {tournament.stateprov}")
    print(f"  Players: {tournament.player_count}")
```

### Search with Filters

Narrow down results with location, date range, and tournament type filters:

```python
from ifpa_api import IfpaClient, TournamentType
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Search by location and date range
results: TournamentSearchResponse = client.tournaments.search(
    city="Portland",
    stateprov="OR",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Search women's tournaments only
women_tournaments: TournamentSearchResponse = client.tournaments.search(
    tournament_type=TournamentType.WOMEN.value,
    country="US"
)

# Paginated search
results: TournamentSearchResponse = client.tournaments.search(
    name="Championship",
    start_pos=0,
    count=50
)
```

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Tournament name (partial match) |
| `city` | `str` | Filter by city |
| `stateprov` | `str` | Filter by state/province code |
| `country` | `str` | Filter by country code (e.g., "US") |
| `start_date` | `str` | Filter by start date (YYYY-MM-DD format) |
| `end_date` | `str` | Filter by end date (YYYY-MM-DD format) |
| `tournament_type` | `str` | Filter by type ("open", "women") |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return |

## Get Tournament Details

Retrieve detailed information about a specific tournament:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import Tournament

client = IfpaClient()

# Get tournament by ID
tournament: Tournament = client.tournament(12345).get()

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

# Get results
results: TournamentResultsResponse = client.tournament(12345).results()

print(f"Tournament: {results.tournament_name}")
print(f"Date: {results.event_date}")
print(f"Players: {results.player_count}")
print("\nFinal Standings:")

for result in results.results[:10]:  # Top 10
    print(f"{result.position}. {result.player_name} ({result.city}, {result.stateprov})")
    print(f"   WPPR: {result.wppr_points:.2f} | Rating: {result.rating_points:.2f}")
```

### Result Details

Each result includes:

- **Placement**: Position, percentile
- **Player Info**: Player ID, name, location
- **Points**: WPPR points earned, rating points earned
- **Performance**: Best game finish, total events

## Get Tournament Formats

Retrieve format information for tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentFormatsResponse

client = IfpaClient()

# Get tournament format information
formats: TournamentFormatsResponse = client.tournament(12345).formats()

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

## Get League Information

For tournaments that are part of a league, retrieve league session data:

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

# Get submission information
submissions: TournamentSubmissionsResponse = client.tournament(12345).submissions()

print(f"Tournament ID: {submissions.tournament_id}")
print(f"Total Submissions: {len(submissions.submissions)}")

for submission in submissions.submissions:
    print(f"\nSubmission ID: {submission.submission_id}")
    print(f"  Date: {submission.submission_date}")
    print(f"  Submitter: {submission.submitter_name}")
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
    with IfpaClient() as client:
        try:
            # Get tournament details
            tournament: Tournament = client.tournament(tournament_id).get()

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
                print(f"  {result.position}. {result.player_name} - {result.wppr_points:.2f} WPPR")

            # Calculate statistics
            if results.results:
                avg_wppr = sum(r.wppr_points or 0 for r in results.results) / len(results.results)
                print(f"\nStatistics:")
                print(f"  Average WPPR: {avg_wppr:.2f}")
                print(f"  Total Finishers: {len(results.results)}")

        except IfpaApiError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    analyze_tournament(12345)
```

## Best Practices

### Date Range Searches

When searching by date, use ISO format (YYYY-MM-DD):

```python
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Get tournaments for a specific year
results: TournamentSearchResponse = client.tournaments.search(
    start_date="2024-01-01",
    end_date="2024-12-31",
    country="US"
)

# Get upcoming tournaments
from datetime import datetime, timedelta

today = datetime.now()
next_month = today + timedelta(days=30)

upcoming: TournamentSearchResponse = client.tournaments.search(
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
    tournament: Tournament = client.tournament(999999).get()
except IfpaApiError as e:
    if e.status_code == 404:
        print("Tournament not found")
    else:
        print(f"API error: {e}")
```

### Tournament Type Filtering

Use the TournamentType enum for type safety:

```python
from ifpa_api import IfpaClient, TournamentType
from ifpa_api.models.tournaments import TournamentSearchResponse

client = IfpaClient()

# Filter by tournament type
open_tournaments: TournamentSearchResponse = client.tournaments.search(
    tournament_type=TournamentType.OPEN.value
)

women_tournaments: TournamentSearchResponse = client.tournaments.search(
    tournament_type=TournamentType.WOMEN.value
)
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
        results: TournamentSearchResponse = client.tournaments.search(
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

- [Directors](directors.md) - View tournament directors
- [Players](players.md) - View player profiles and results
- [Series](series.md) - Tournament series information
- [Error Handling](error-handling.md) - Handle API errors
