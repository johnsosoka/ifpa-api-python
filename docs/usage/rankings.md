# Rankings

Access various IFPA ranking systems including WPPR, women's, youth, professional circuit, virtual tournaments, and custom rankings.

## Main WPPR Rankings

Retrieve the main World Pinball Player Rankings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get top 100 players
rankings: RankingsResponse = client.rankings.wppr(start_pos=0, count=100)

print(f"Total ranked players: {rankings.total_results}")
print(f"Ranking system: {rankings.ranking_system}")
print(f"Last updated: {rankings.last_updated}")

for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")
```

### Filter by Location

Filter rankings by country or region:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get US rankings only
us_rankings: RankingsResponse = client.rankings.wppr(
    country="US",
    count=100
)

# Get rankings for specific region
region_rankings: RankingsResponse = client.rankings.wppr(
    region="Northwest",
    count=50
)

# Paginated results
next_page: RankingsResponse = client.rankings.wppr(
    start_pos=100,
    count=100
)
```

### WPPR Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_pos` | `int \| str` | Starting position for pagination (default: 0) |
| `count` | `int \| str` | Number of results to return (max 250) |
| `country` | `str` | Filter by country code (e.g., "US", "CA") |
| `region` | `str` | Filter by region name |

## Women's Rankings

Access women's ranking system with options for open or women-only tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get women's rankings from all tournaments
rankings: RankingsResponse = client.rankings.women(
    tournament_type="OPEN",
    start_pos=0,
    count=50
)

# Get women's rankings from women-only tournaments
women_only: RankingsResponse = client.rankings.women(
    tournament_type="WOMEN",
    count=50
)

# Filter by country
us_women: RankingsResponse = client.rankings.women(
    tournament_type="OPEN",
    country="US",
    count=100
)

for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}")
    print(f"  Rating: {entry.rating}")
    print(f"  Location: {entry.city}, {entry.stateprov}")
```

### Women's Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tournament_type` | `str` | Tournament filter: "OPEN" for all tournaments, "WOMEN" for women-only (default: "OPEN") |
| `start_pos` | `int \| str` | Starting position for pagination |
| `count` | `int \| str` | Number of results to return (max 250) |
| `country` | `str` | Filter by country code |

## Youth Rankings

Access youth player rankings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get top youth players
youth: RankingsResponse = client.rankings.youth(
    start_pos=0,
    count=50
)

# Filter by country
us_youth: RankingsResponse = client.rankings.youth(
    country="US",
    count=100
)

for entry in youth.rankings:
    print(f"{entry.rank}. {entry.player_name} (Age: {entry.age})")
    print(f"  Rating: {entry.rating}")
    print(f"  Active Events: {entry.active_events}")
```

### Youth Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_pos` | `int \| str` | Starting position for pagination |
| `count` | `int \| str` | Number of results to return (max 250) |
| `country` | `str` | Filter by country code |

## Virtual Tournament Rankings

Access rankings from virtual pinball tournaments:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get virtual tournament rankings
virtual: RankingsResponse = client.rankings.virtual(
    start_pos=0,
    count=50
)

# Filter by country
us_virtual: RankingsResponse = client.rankings.virtual(
    country="US",
    count=100
)

for entry in virtual.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")
```

### Virtual Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_pos` | `int \| str` | Starting position for pagination |
| `count` | `int \| str` | Number of results to return (max 250) |
| `country` | `str` | Filter by country code |

## Professional Circuit Rankings

Access professional circuit rankings for open and women's divisions:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Get open division pro rankings
pro: RankingsResponse = client.rankings.pro(
    ranking_system="OPEN",
    start_pos=0,
    count=50
)

# Get women's division pro rankings
women_pro: RankingsResponse = client.rankings.pro(
    ranking_system="WOMEN",
    count=50
)

for entry in pro.rankings:
    print(f"{entry.rank}. {entry.player_name}")
    print(f"  Rating: {entry.rating}")
    print(f"  Best Finish: {entry.best_finish}")
    print(f"  WPPR Points: {entry.wppr_points}")
```

### Pro Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ranking_system` | `str` | Division filter: "OPEN" for open division, "WOMEN" for women's division (default: "OPEN") |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return (max 250) |

## Country Rankings

Compare countries by total players, tournaments, and aggregate statistics:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CountryRankingsResponse

client = IfpaClient()

# Get all country rankings
countries: CountryRankingsResponse = client.rankings.by_country(
    country="",
    start_pos=0,
    count=25
)

print(f"Total countries ranked: {countries.total_countries}")

for entry in countries.country_rankings:
    print(f"{entry.rank}. {entry.country_name} ({entry.country_code})")
    print(f"  Total Players: {entry.total_players}")
    print(f"  Active Players: {entry.total_active_players}")
    print(f"  Total Tournaments: {entry.total_tournaments}")
    print(f"  Average WPPR: {entry.average_wppr}")
    print(f"  Top Player: {entry.top_player_name} ({entry.top_player_wppr})")
```

### Filter by Specific Country

Search for a specific country by code or name:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CountryRankingsResponse

client = IfpaClient()

# Using country code
us_info: CountryRankingsResponse = client.rankings.by_country(
    country="US",
    count=10
)

# Using country name
canada_info: CountryRankingsResponse = client.rankings.by_country(
    country="Canada",
    count=10
)

for entry in us_info.country_rankings:
    print(f"Rank: {entry.rank}")
    print(f"Total Players: {entry.total_players}")
```

### Country Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `country` | `str` | Country code (e.g., "US") or country name (e.g., "United States"). Use empty string for all countries |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return |

## Custom Rankings

Access custom ranking systems created for specific purposes or regions:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CustomRankingsResponse

client = IfpaClient()

# Get custom ranking by ID
custom: CustomRankingsResponse = client.rankings.custom(
    ranking_id="regional-2024",
    start_pos=0,
    count=50
)

print(f"Ranking: {custom.ranking_name}")
print(f"Description: {custom.description}")

for entry in custom.rankings:
    print(f"{entry.rank}. {entry.player_name}")
    print(f"  Value: {entry.value}")
    if entry.details:
        print(f"  Details: {entry.details}")
```

### Custom Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ranking_id` | `str \| int` | Custom ranking system identifier |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return |

## Complete Example: Rankings Comparison

Compare multiple ranking systems for analysis:

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.rankings import RankingsResponse


def compare_rankings() -> None:
    """Compare different ranking systems."""
    client = IfpaClient()

    try:
        # Get top players from different systems
        print("=" * 60)
        print("RANKING SYSTEM COMPARISON")
        print("=" * 60)

        # Main WPPR
        wppr: RankingsResponse = client.rankings.wppr(count=10)
        print("\nMain WPPR Top 10:")
        for entry in wppr.rankings[:10]:
            print(f"  {entry.rank}. {entry.player_name}: {entry.rating}")

        # Women's rankings
        women: RankingsResponse = client.rankings.women(count=10)
        print("\nWomen's Rankings Top 10:")
        for entry in women.rankings[:10]:
            print(f"  {entry.rank}. {entry.player_name}: {entry.rating}")

        # Youth rankings
        youth: RankingsResponse = client.rankings.youth(count=10)
        print("\nYouth Rankings Top 10:")
        for entry in youth.rankings[:10]:
            print(f"  {entry.rank}. {entry.player_name}: {entry.rating}")

        # Pro circuit
        pro: RankingsResponse = client.rankings.pro(count=10)
        print("\nPro Circuit Top 10:")
        for entry in pro.rankings[:10]:
            print(f"  {entry.rank}. {entry.player_name}: {entry.rating}")

        # Virtual tournaments
        virtual: RankingsResponse = client.rankings.virtual(count=10)
        print("\nVirtual Tournament Top 10:")
        for entry in virtual.rankings[:10]:
            print(f"  {entry.rank}. {entry.player_name}: {entry.rating}")

    except IfpaApiError as e:
        print(f"Error fetching rankings: {e}")


if __name__ == "__main__":
    compare_rankings()
```

## Best Practices

### Pagination

When working with large result sets, use pagination:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client = IfpaClient()

# Fetch rankings in batches
all_rankings = []
batch_size = 250  # Maximum allowed
start = 0

while True:
    batch: RankingsResponse = client.rankings.wppr(
        start_pos=start,
        count=batch_size
    )

    all_rankings.extend(batch.rankings)

    # Stop if we got fewer results than requested
    if len(batch.rankings) < batch_size:
        break

    start += batch_size

print(f"Total players fetched: {len(all_rankings)}")
```

### Error Handling

Handle API errors gracefully:

```python
from ifpa_api import IfpaClient, IfpaApiError

client = IfpaClient()

try:
    rankings = client.rankings.wppr(count=100)
except IfpaApiError as e:
    if e.status_code == 429:
        print("Rate limit exceeded. Please wait and retry.")
    elif e.status_code >= 500:
        print("IFPA API is experiencing issues. Please try again later.")
    else:
        print(f"API error: {e}")
```

### Country Code Reference

Common country codes for filtering:

- `US` - United States
- `CA` - Canada
- `GB` - United Kingdom
- `DE` - Germany
- `SE` - Sweden
- `AU` - Australia
- `JP` - Japan
- `FR` - France
- `IT` - Italy
- `ES` - Spain

For a complete list of country codes, use the reference endpoint (see [API Reference](../api-reference/overview.md)).

## Related Resources

- [Players](players.md) - View individual player profiles and rankings
- [Tournaments](tournaments.md) - View tournament results
- [Error Handling](error-handling.md) - Handle API errors
