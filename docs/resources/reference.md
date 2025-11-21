# Reference Data

The Reference resource provides access to lookup data such as countries and states/provinces that are used throughout the IFPA system. This data is useful for building UI dropdowns, validating location filters, and understanding the geographic structure of the IFPA database.

## Overview

The Reference client provides two main endpoints:

- `countries()` - Get list of all countries in the IFPA system
- `state_provs()` - Get states/provinces organized by country

## Getting Started

Access the reference client through the main `IfpaClient`:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    import asyncio

    async def main():
        async with AsyncIfpaClient(api_key="your-api-key") as client:
            # Access reference data
            countries = await client.reference.countries()
            state_provs = await client.reference.state_provs()

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    client = IfpaClient(api_key="your-api-key")

    # Access reference data
    countries = client.reference.countries()
    state_provs = client.reference.state_provs()
    ```

## Countries

### Get All Countries

The `countries()` method returns a list of all countries in the IFPA system (typically 62 countries):

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            countries = await client.reference.countries()

            # Iterate through all countries
            for country in countries.country:
                print(f"{country.country_name} ({country.country_code})")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    client = IfpaClient()

    countries = client.reference.countries()

    # Iterate through all countries
    for country in countries.country:
        print(f"{country.country_name} ({country.country_code})")
    ```

**Response fields:**

- `country_id` (int) - Unique country identifier
- `country_name` (str) - Full country name (e.g., "United States")
- `country_code` (str) - ISO country code (e.g., "US")
- `active_flag` (str) - Whether country is active ("Y" or "N")

### Find a Specific Country

```python
countries = client.reference.countries()

# Find US country data
us = next(c for c in countries.country if c.country_name == "United States")
print(us.country_code)  # "US"
print(us.country_id)    # 239
```

### Filter Active Countries

```python
countries = client.reference.countries()

# Get only active countries
active = [c for c in countries.country if c.active_flag == "Y"]
print(f"Active countries: {len(active)}")
```

## States and Provinces

### Get All States/Provinces

The `state_provs()` method returns regional subdivisions for countries that have them. The IFPA system tracks regions for three countries: Australia, Canada, and the United States (67 total regions):

!!! warning "Reference Data Incompleteness"
    The `/stateprovs` endpoint only returns official codes for US, Canada, and Australia. However, the IFPA database contains many additional undocumented state/province codes from other countries (e.g., "CAB" for Buenos Aires, "Can" for Canterbury NZ, "PAC" for Provence-Alpes-Côte d'Azur).

    **Impact**: You cannot use this endpoint to validate all possible state codes that appear in player, director, or tournament records.

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            state_provs = await client.reference.state_provs()

            # Iterate through countries and their regions
            for country_region in state_provs.stateprov:
                print(f"{country_region.country_name}:")
                for region in country_region.regions:
                    print(f"  - {region.region_name} ({region.region_code})")

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    client = IfpaClient()

    state_provs = client.reference.state_provs()

    # Iterate through countries and their regions
    for country_region in state_provs.stateprov:
        print(f"{country_region.country_name}:")
        for region in country_region.regions:
            print(f"  - {region.region_name} ({region.region_code})")
    ```

**Response fields:**

Country-level:
- `country_id` (int) - Unique country identifier
- `country_name` (str) - Full country name
- `country_code` (str) - ISO country code
- `regions` (list[Region]) - List of regions in this country

Region-level:
- `region_name` (str) - Full region name (e.g., "California", "Ontario")
- `region_code` (str) - Region code abbreviation (e.g., "CA", "ON")

### Get States for a Specific Country

```python
state_provs = client.reference.state_provs()

# Find US states
us_regions = next(c for c in state_provs.stateprov if c.country_code == "US")
print(f"US has {len(us_regions.regions)} states")

# Get all state codes
us_codes = [r.region_code for r in us_regions.regions]
print(us_codes)  # ["AL", "AK", "AZ", ...]
```

### Get Canadian Provinces

```python
state_provs = client.reference.state_provs()

# Find Canadian provinces
ca_regions = next(c for c in state_provs.stateprov if c.country_code == "CA")

for region in ca_regions.regions:
    print(f"{region.region_name}: {region.region_code}")
# Ontario: ON
# Quebec: QC
# British Columbia: BC
# ...
```

!!! note "API Limitation"
    The Canadian provinces data is incomplete in the API - it returns 8 provinces but Canada has 13 total provinces/territories. Missing: Newfoundland and Labrador (NL), Prince Edward Island (PE), Northwest Territories (NT), Nunavut (NU), and Yukon (YT).

## Common Use Cases

### Building Location Dropdowns

Reference data is perfect for building cascading location dropdowns in UIs:

```python
# Get countries for first dropdown
countries = client.reference.countries()
active_countries = [
    {"id": c.country_id, "name": c.country_name, "code": c.country_code}
    for c in countries.country
    if c.active_flag == "Y"
]

# Get states/provinces for second dropdown (when US/CA/AU selected)
state_provs = client.reference.state_provs()
regions_by_country = {
    c.country_code: [
        {"name": r.region_name, "code": r.region_code}
        for r in c.regions
    ]
    for c in state_provs.stateprov
}
```

### Validating Location Filters

Use reference data to validate user input before making other API calls:

```python
def is_valid_country(country_code: str) -> bool:
    """Check if a country code is valid."""
    countries = client.reference.countries()
    valid_codes = [c.country_code for c in countries.country]
    return country_code in valid_codes

def is_valid_state(country_code: str, state_code: str) -> bool:
    """Check if a state code is valid for a given country."""
    state_provs = client.reference.state_provs()
    country_data = next(
        (c for c in state_provs.stateprov if c.country_code == country_code),
        None
    )
    if not country_data:
        return False

    valid_codes = [r.region_code for r in country_data.regions]
    return state_code in valid_codes

# Validate before making API call
if is_valid_country("US") and is_valid_state("US", "CA"):
    players = client.player.query().country("US").state("CA").get()
```

### Converting Country Names to Codes

```python
def get_country_code(country_name: str) -> str | None:
    """Get country code from country name."""
    countries = client.reference.countries()
    country = next(
        (c for c in countries.country if c.country_name == country_name),
        None
    )
    return country.country_code if country else None

code = get_country_code("United States")  # Returns "US"
```

### Counting Total Geographic Coverage

```python
# Count total countries
countries = client.reference.countries()
total_countries = len(countries.country)
active_countries = sum(1 for c in countries.country if c.active_flag == "Y")

print(f"Total countries: {total_countries}")
print(f"Active countries: {active_countries}")

# Count total regions
state_provs = client.reference.state_provs()
total_regions = sum(len(c.regions) for c in state_provs.stateprov)

print(f"Total regions: {total_regions}")
```

## Caching Recommendations

Reference data changes infrequently. Consider caching this data in your application:

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_countries():
    """Get countries with caching."""
    client = IfpaClient()
    return client.reference.countries()

@lru_cache(maxsize=1)
def get_state_provs():
    """Get state/provs with caching."""
    client = IfpaClient()
    return client.reference.state_provs()

# First call hits API
countries = get_countries()

# Subsequent calls use cache
countries = get_countries()  # Cached
```

For longer-lived applications, implement time-based cache expiration:

```python
from datetime import datetime, timedelta
from typing import Any

class ReferenceCache:
    """Simple time-based cache for reference data."""

    def __init__(self, ttl_hours: int = 24):
        self.ttl = timedelta(hours=ttl_hours)
        self._countries_cache: tuple[Any, datetime] | None = None
        self._state_provs_cache: tuple[Any, datetime] | None = None
        self._client = IfpaClient()

    def get_countries(self):
        """Get countries with time-based caching."""
        if self._countries_cache:
            data, cached_at = self._countries_cache
            if datetime.now() - cached_at < self.ttl:
                return data

        # Cache expired or doesn't exist, fetch fresh data
        data = self._client.reference.countries()
        self._countries_cache = (data, datetime.now())
        return data

    def get_state_provs(self):
        """Get state/provs with time-based caching."""
        if self._state_provs_cache:
            data, cached_at = self._state_provs_cache
            if datetime.now() - cached_at < self.ttl:
                return data

        data = self._client.reference.state_provs()
        self._state_provs_cache = (data, datetime.now())
        return data

# Usage
cache = ReferenceCache(ttl_hours=24)
countries = cache.get_countries()  # Cached for 24 hours
```

## Error Handling

Reference endpoints use standard SDK error handling:

```python
from ifpa_api import IfpaClient, IfpaApiError, MissingApiKeyError

try:
    client = IfpaClient(api_key="your-api-key")
    countries = client.reference.countries()
except MissingApiKeyError:
    print("API key not provided")
except IfpaApiError as e:
    print(f"API error: {e.status_code} - {e.response_body}")
```

For more details on error handling, see the [Error Handling guide](../guides/error-handling.md).

## API Endpoints

The Reference client uses these IFPA API endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `countries()` | `GET /countries` | Get all countries |
| `state_provs()` | `GET /stateprovs` | Get states/provinces by country |

## Related Resources

- [Rankings](rankings.md) - Use country filters with rankings
- [Player](players.md) - Search players by location
- [Tournaments](tournaments.md) - Search tournaments by location
- [API Reference: Models](../api-client-reference/models.md) - Complete model definitions
