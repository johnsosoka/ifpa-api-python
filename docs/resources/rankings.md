# Rankings

Access various IFPA ranking systems including WPPR, women's, youth, professional circuit, virtual tournaments, and custom rankings.

## Main WPPR Rankings

Retrieve the main World Pinball Player Rankings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

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

client: IfpaClient = IfpaClient()

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

client: IfpaClient = IfpaClient()

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

client: IfpaClient = IfpaClient()

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

client: IfpaClient = IfpaClient()

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

client: IfpaClient = IfpaClient()

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

Get player rankings filtered by a specific country:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CountryRankingsResponse

client: IfpaClient = IfpaClient()

# Get US player rankings
us_rankings: CountryRankingsResponse = client.rankings.by_country(
    country="US",
    start_pos=0,
    count=25
)

print(f"Country: {us_rankings.rank_country_name}")
print(f"Total players: {us_rankings.total_count}")
print(f"Showing: {us_rankings.return_count} results starting at position {us_rankings.start_position}")

for entry in us_rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}")
    print(f"  Rating: {entry.rating}")
    print(f"  Location: {entry.city}, {entry.stateprov}")
    print(f"  Active Events: {entry.active_events}")
```

### Filter by Country Code or Name

You can use either the country code or full country name:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CountryRankingsResponse

client: IfpaClient = IfpaClient()

# Using country code
us_rankings: CountryRankingsResponse = client.rankings.by_country(
    country="US",
    count=50
)

# Using country name
canada_rankings: CountryRankingsResponse = client.rankings.by_country(
    country="Canada",
    count=50
)

print(f"Top US player: {us_rankings.rankings[0].player_name} (Rating: {us_rankings.rankings[0].rating})")
print(f"Top Canadian player: {canada_rankings.rankings[0].player_name} (Rating: {canada_rankings.rankings[0].rating})")
```

### Country Rankings Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `country` | `str` | Country code (e.g., "US") or country name (e.g., "United States") - **required** |
| `start_pos` | `int` | Starting position for pagination |
| `count` | `int` | Number of results to return |

## List All Countries

Get a list of all countries with ranked players:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsCountryListResponse

client: IfpaClient = IfpaClient()

# Get all countries with player counts
countries: RankingsCountryListResponse = client.rankings.country_list()

print(f"Total countries: {countries.count}")

# Display top 10 countries by player count
top_countries = sorted(
    countries.country,
    key=lambda c: c.player_count,
    reverse=True
)[:10]

for country in top_countries:
    print(f"{country.country_name} ({country.country_code}): {country.player_count} players")

# Find a specific country
us = next((c for c in countries.country if c.country_code == "US"), None)
if us:
    print(f"\nUS has {us.player_count} ranked players")
```

This endpoint is useful for discovering valid country codes before calling `by_country()`

## Custom Rankings

Access custom ranking systems created for specific purposes or regions.

### List Available Custom Rankings

First, discover available custom ranking systems:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CustomRankingListResponse

client: IfpaClient = IfpaClient()

# Get all custom ranking systems
custom_list: CustomRankingListResponse = client.rankings.custom_list()

print(f"Total custom rankings: {custom_list.total_count}")

for ranking_info in custom_list.custom_view:
    print(f"\nID: {ranking_info.view_id}")
    print(f"Title: {ranking_info.title}")
    if ranking_info.description:
        print(f"Description: {ranking_info.description}")
```

### Get Custom Ranking Results

Once you have a ranking ID, retrieve its rankings:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CustomRankingsResponse

client: IfpaClient = IfpaClient()

# Get custom ranking by ID
custom: CustomRankingsResponse = client.rankings.custom(
    ranking_id=123,
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

### Find and Query a Specific Custom Ranking

Combine both methods to find and query a specific ranking:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import CustomRankingListResponse, CustomRankingsResponse

client: IfpaClient = IfpaClient()

# Find a specific ranking by title keyword
custom_list: CustomRankingListResponse = client.rankings.custom_list()
retro_ranking = next(
    (r for r in custom_list.custom_view if "retro" in r.title.lower()),
    None
)

if retro_ranking:
    print(f"Found: {retro_ranking.title} (ID: {retro_ranking.view_id})")

    # Get rankings for that system
    rankings: CustomRankingsResponse = client.rankings.custom(retro_ranking.view_id, count=25)

    print(f"\nTop 25 in {rankings.ranking_name}:")
    for entry in rankings.rankings:
        print(f"{entry.rank}. {entry.player_name}: {entry.value}")
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
    client: IfpaClient = IfpaClient()

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
from ifpa_api.models.rankings import RankingsResponse, RankingEntry

client: IfpaClient = IfpaClient()

# Fetch rankings in batches
all_rankings: list[RankingEntry] = []
batch_size: int = 250  # Maximum allowed
start: int = 0

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
from ifpa_api.models.rankings import RankingsResponse

client: IfpaClient = IfpaClient()

try:
    rankings: RankingsResponse = client.rankings.wppr(count=100)
except IfpaApiError as e:
    if e.status_code == 429:
        print("Rate limit exceeded. Please wait and retry.")
    elif e.status_code >= 500:
        print("IFPA API is experiencing issues. Please try again later.")
    else:
        print(f"API error: {e}")
```

### Finding Country Codes

Use the `country_list()` method to discover valid country codes and player counts:

```python
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsCountryListResponse

client: IfpaClient = IfpaClient()

# Get all countries
countries: RankingsCountryListResponse = client.rankings.country_list()

# Find countries with most players
top_countries = sorted(countries.country, key=lambda c: c.player_count, reverse=True)[:10]
for country in top_countries:
    print(f"{country.country_code}: {country.country_name} ({country.player_count} players)")
```

## Related Resources

- [Player](players.md) - View individual player profiles and rankings
- [Tournaments](tournaments.md) - View tournament results
- [Error Handling](../guides/error-handling.md) - Handle API errors
