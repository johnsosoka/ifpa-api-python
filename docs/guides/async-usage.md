# Async Usage Guide

Starting with version 1.0.0, the IFPA API client provides full async/await support through the `AsyncIfpaClient`. This guide covers everything you need to know about using the async client effectively.

## Overview

The async client provides the exact same API as the sync client but with async/await support. Choose the async client when:

- Building async applications (FastAPI, aiohttp, etc.)
- Need to make concurrent API requests
- Want better performance in high-throughput scenarios
- Working in an async codebase

## Quick Start

```python
from ifpa_api import AsyncIfpaClient
import asyncio

async def main():
    async with AsyncIfpaClient() as client:
        # All operations use await
        player = await client.player.get(25584)  # Dwayne Smith
        print(f"{player.first_name} {player.last_name}")

asyncio.run(main())
```

## Sync vs Async

Both clients share the same API surface:

=== "Async"
    ```python
    from ifpa_api import AsyncIfpaClient
    import asyncio

    async def main():
        async with AsyncIfpaClient() as client:
            player = await client.player.get(25584)  # Dwayne Smith
            rankings = await client.rankings.wppr(count=100)

    asyncio.run(main())
    ```

=== "Sync"
    ```python
    from ifpa_api import IfpaClient

    with IfpaClient() as client:
        player = client.player.get(25584)  # Dwayne Smith
        rankings = client.rankings.wppr(count=100)
    ```

**Key Differences:**
- Import `AsyncIfpaClient` instead of `IfpaClient`
- Use `async with` for context manager
- Add `await` before method calls that make API requests
- Use `async for` for pagination
- Filter methods stay sync (`.country()`, `.state()`, `.limit()`)

## Initialization

### With API Key

```python
from ifpa_api import AsyncIfpaClient

# Explicit API key
client = AsyncIfpaClient(api_key="your-api-key")

# From environment variable IFPA_API_KEY
client = AsyncIfpaClient()

# Custom configuration
client = AsyncIfpaClient(
    api_key="your-api-key",
    timeout=30.0,  # Request timeout in seconds
    validate_requests=True  # Pydantic validation
)
```

### Context Manager (Recommended)

**Always use async context managers** to ensure proper cleanup:

```python
async with AsyncIfpaClient() as client:
    player = await client.player.get(25584)  # Dwayne Smith
# Automatically closed, connections released
```

**Manual cleanup** (not recommended):

```python
client = AsyncIfpaClient()
try:
    player = await client.player.get(25584)  # Dwayne Smith
finally:
    await client.close()  # Must close manually!
```

!!! warning "Resource Leaks"
    Failing to close the async client will leak HTTP connections and may cause `ResourceWarning`s. Always use `async with` or call `await client.close()`.

## Basic Operations

### Player Operations

#### Get Player Details

```python
async with AsyncIfpaClient() as client:
    # Get player by ID
    player = await client.player.get(25584)  # Dwayne Smith
    print(f"{player.first_name} {player.last_name}")
    print(f"Rank: {player.player_stats.current_wppr_rank}")
```

#### Check Player Existence

```python
async with AsyncIfpaClient() as client:
    # Check if player exists
    exists = await client.player.exists(25584)  # Dwayne Smith
    print(f"Player exists: {exists}")

    # Get or None (no exception on 404)
    maybe_player = await client.player.get_or_none(50106)  # Anna Rigas (inactive)
    if maybe_player:
        print(f"Found: {maybe_player.first_name}")
    else:
        print("Player not found or inactive")
```

#### PvP Comparison

```python
async with AsyncIfpaClient() as client:
    # Compare two players who have competed together
    pvp = await client.player(25584).pvp(47585)  # Dwayne vs Debbie Smith
    print(f"Total meetings: {pvp.total_meetings}")
    print(f"Wins: {pvp.player1_wins}/{pvp.player2_wins}")
```

#### Player Results and Rankings

```python
from ifpa_api.models.common import RankingSystem, ResultType

async with AsyncIfpaClient() as client:
    # Get player rankings
    rankings = await client.player(25584).rankings()  # Dwayne Smith
    print(f"WPPR Rank: {rankings.rankings[0].rank}")

    # Get player results
    results = await client.player(25584).results(
        RankingSystem.MAIN,
        ResultType.ACTIVE
    )
    print(f"Active events: {len(results.results)}")
```

### Search with Query Builders

**Query builders work the same - filters are sync, execution is async:**

```python
async with AsyncIfpaClient() as client:
    # Build query (sync operations)
    query = client.player.search("Smith") \
        .country("US") \
        .state("WA") \
        .limit(25)

    # Execute query (async operation)
    results = await query.get()

    # Query reuse (immutable pattern)
    us_players = client.player.search().country("US")
    wa_results = await us_players.state("WA").get()
    or_results = await us_players.state("OR").get()
```

### Tournament Operations

```python
async with AsyncIfpaClient() as client:
    # Get tournament
    tournament = await client.tournament.get(7070)  # PAPA 17
    print(f"Tournament: {tournament.tournament_name}")

    # Search tournaments
    results = await client.tournament.search("Championship") \
        .country("US") \
        .date_range("2024-01-01", "2024-12-31") \
        .get()
    print(f"Found {len(results.tournaments)} championships")

    # Get tournament results
    results = await client.tournament(7070).results()  # PAPA 17
    print(f"Standings: {len(results.results)} players")
```

### Director Operations

```python
async with AsyncIfpaClient() as client:
    # Get director details
    director = await client.director.get(1533)  # Josh Rainwater
    print(f"{director.first_name} {director.last_name}")
    print(f"Tournaments: {director.stats.tournament_count}")

    # Get director's tournaments
    from ifpa_api.models.common import TimePeriod

    tournaments = await client.director(1533).tournaments(TimePeriod.PAST)
    print(f"Past events: {len(tournaments.tournaments)}")
```

## Concurrent Requests

One of the main benefits of async is making concurrent requests:

### Basic Concurrency

```python
import asyncio

async with AsyncIfpaClient() as client:
    # Fetch multiple players concurrently (Idaho pinball community)
    players = await asyncio.gather(
        client.player.get(25584),  # Dwayne Smith
        client.player.get(47585),  # Debbie Smith
        client.player.get(52913)   # Dave Fellows
    )

    for player in players:
        print(f"{player.first_name} {player.last_name} - Rank {player.player_stats.current_wppr_rank}")

    # Mix different resources
    player, director, tournament = await asyncio.gather(
        client.player.get(25584),     # Dwayne Smith
        client.director.get(1533),    # Josh Rainwater
        client.tournament.get(7070)   # PAPA 17
    )
```

### Error Handling with Gather

```python
from ifpa_api import IfpaApiError

async with AsyncIfpaClient() as client:
    # return_exceptions=True to handle errors individually
    results = await asyncio.gather(
        client.player.get(25584),  # Dwayne Smith - exists
        client.player.get(50106),  # Anna Rigas - inactive player
        client.player.get(52913),  # Dave Fellows - exists
        return_exceptions=True
    )

    for result in results:
        if isinstance(result, IfpaApiError):
            print(f"Error: {result.message}")
        elif isinstance(result, Exception):
            print(f"Unexpected error: {result}")
        else:
            print(f"Player: {result.first_name} {result.last_name}")
```

### TaskGroup (Python 3.11+)

```python
async with AsyncIfpaClient() as client:
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(client.player.get(25584))   # Dwayne Smith
        task2 = tg.create_task(client.player.get(47585))   # Debbie Smith
        task3 = tg.create_task(client.tournament.get(7070))  # PAPA 17

    # All tasks complete here
    player1 = task1.result()
    player2 = task2.result()
    tournament = task3.result()

    print(f"Player 1: {player1.first_name}")
    print(f"Player 2: {player2.first_name}")
    print(f"Tournament: {tournament.tournament_name}")
```

## Pagination

### Async Iteration

```python
async with AsyncIfpaClient() as client:
    # Memory-efficient pagination
    async for player in client.player.search().country("US").iterate(limit=100):
        print(f"{player.first_name} {player.last_name}")
        # Process each player without loading all into memory
```

### Get All Results

```python
async with AsyncIfpaClient() as client:
    # Fetch all results (loads into memory)
    all_players = await client.player.search().state("WA").get_all()
    print(f"Total players: {len(all_players)}")

    # Safety limit to prevent excessive memory use
    players = await client.player.search().country("US").get_all(max_results=1000)
```

!!! warning "Memory Usage"
    `get_all()` can consume significant memory for large datasets. The IFPA API has 100,000+ ranked players. Use `iterate()` for large datasets.

## Error Handling

Async exceptions work the same as sync:

```python
from ifpa_api import IfpaApiError, PlayersNeverMetError

async with AsyncIfpaClient() as client:
    # Handle API errors - player not found
    try:
        player = await client.player.get(999999999)  # Non-existent ID
    except IfpaApiError as e:
        print(f"Error: {e.message}")
        print(f"Status: {e.status_code}")
        print(f"URL: {e.request_url}")

    # Handle domain-specific errors - players never met
    try:
        # John Sosoka vs World #1 - they never competed
        pvp = await client.player(50104).pvp(1)
    except PlayersNeverMetError as e:
        print(f"Players {e.player1_id} and {e.player2_id} never competed")
```

## Rate Limiting

The async client doesn't implement rate limiting. If you need it, implement it yourself:

### Using aiolimiter

```bash
pip install aiolimiter
```

```python
from aiolimiter import AsyncLimiter
from ifpa_api import AsyncIfpaClient

# Allow 10 requests per second
rate_limit = AsyncLimiter(10, 1)

async with AsyncIfpaClient() as client:
    for player_id in range(1000, 1100):
        async with rate_limit:
            player = await client.player.get_or_none(player_id)
            if player:
                print(f"Found: {player.first_name}")
```

### Using Custom Semaphore

```python
import asyncio

# Limit to 5 concurrent requests
semaphore = asyncio.Semaphore(5)

async def fetch_player(client, player_id):
    async with semaphore:
        return await client.player.get_or_none(player_id)

async with AsyncIfpaClient() as client:
    tasks = [fetch_player(client, pid) for pid in range(1000, 1100)]
    players = await asyncio.gather(*tasks)
```

## Retry Logic

Implement retry logic for transient failures:

### Using tenacity

```bash
pip install tenacity
```

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from ifpa_api import AsyncIfpaClient, IfpaApiError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def fetch_player_with_retry(client, player_id):
    return await client.player.get(player_id)

async with AsyncIfpaClient() as client:
    # Automatically retries on failure (up to 3 attempts)
    player = await fetch_player_with_retry(client, 25584)  # Dwayne Smith
    print(f"Successfully fetched: {player.first_name}")
```

## Integration Examples

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from ifpa_api import AsyncIfpaClient, IfpaApiError

app = FastAPI()

# Reuse client across requests
client = AsyncIfpaClient()

@app.on_event("startup")
async def startup():
    global client
    client = AsyncIfpaClient()

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.get("/players/{player_id}")
async def get_player(player_id: int):
    try:
        player = await client.player.get(player_id)
        return {
            "id": player.player_id,
            "name": f"{player.first_name} {player.last_name}",
            "rank": player.player_stats.current_wppr_rank
        }
    except IfpaApiError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)
```

### aiohttp

```python
from aiohttp import web
from ifpa_api import AsyncIfpaClient

async def handle_player(request):
    player_id = int(request.match_info['player_id'])
    client = request.app['ifpa_client']

    player = await client.player.get_or_none(player_id)
    if not player:
        raise web.HTTPNotFound(text="Player not found")

    return web.json_response({
        "id": player.player_id,
        "name": f"{player.first_name} {player.last_name}"
    })

app = web.Application()
app['ifpa_client'] = AsyncIfpaClient()
app.router.add_get('/players/{player_id}', handle_player)

async def on_cleanup(app):
    await app['ifpa_client'].close()

app.on_cleanup.append(on_cleanup)
web.run_app(app)
```

## Performance Considerations

### Connection Pooling

The async client uses httpx's connection pooling:

```python
# Default pool: 100 connections
# Connections are reused across requests within the same client instance
async with AsyncIfpaClient() as client:
    # These requests reuse connections
    for i in range(1000):
        player = await client.player.get_or_none(i)
```

### Concurrent Request Limits

Be mindful of overwhelming the API:

```python
# BAD: Too many concurrent requests
async with AsyncIfpaClient() as client:
    tasks = [client.player.get(i) for i in range(10000)]
    await asyncio.gather(*tasks)  # May overwhelm API

# GOOD: Use semaphore to limit concurrency
semaphore = asyncio.Semaphore(10)

async def fetch_with_limit(client, player_id):
    async with semaphore:
        return await client.player.get_or_none(player_id)

async with AsyncIfpaClient() as client:
    tasks = [fetch_with_limit(client, i) for i in range(10000)]
    results = await asyncio.gather(*tasks)
```

### Pydantic Validation

Pydantic's `model_validate()` is synchronous but very fast (Rust-based in v2). For most use cases, this is not a bottleneck. If profiling shows validation is slow:

```python
import asyncio

# Optional: Move validation to thread pool
async def validate_in_thread(model, data):
    return await asyncio.to_thread(model.model_validate, data)
```

## Best Practices

### 1. Always Use Context Managers

```python
# ✅ GOOD: Automatic cleanup
async with AsyncIfpaClient() as client:
    player = await client.player.get(25584)  # Dwayne Smith
    # Connections automatically closed when exiting context

# ❌ BAD: Manual cleanup required
client = AsyncIfpaClient()
player = await client.player.get(25584)
# Forgot to close! Leaks connections and causes ResourceWarning
```

### 2. Reuse Clients

```python
# ✅ GOOD: Reuse client for multiple requests
async with AsyncIfpaClient() as client:
    for player_id in [25584, 47585, 52913]:  # Idaho community
        player = await client.player.get(player_id)
        print(f"{player.first_name} {player.last_name}")

# ❌ BAD: Creating client for each request
for player_id in [25584, 47585, 52913]:
    async with AsyncIfpaClient() as client:  # Wasteful - new connection pool each time!
        player = await client.player.get(player_id)
```

### 3. Use Concurrent Requests

```python
# ✅ GOOD: Concurrent fetching (3x faster!)
players = await asyncio.gather(
    client.player.get(25584),  # Dwayne Smith
    client.player.get(47585),  # Debbie Smith
    client.player.get(52913)   # Dave Fellows
)

# ❌ BAD: Sequential fetching (slower, wastes async benefits)
players = []
for player_id in [25584, 47585, 52913]:
    player = await client.player.get(player_id)
    players.append(player)
```

### 4. Handle Errors Properly

```python
# ✅ GOOD: Specific error handling
try:
    player = await client.player.get(25584)  # Dwayne Smith
    rankings = await client.player(25584).rankings()
except PlayersNeverMetError:
    # Handle specific case when checking PvP
    print("Players have never competed together")
except IfpaApiError as e:
    # Handle general API errors (404, 500, etc.)
    print(f"API Error: {e.message} (Status: {e.status_code})")

# ❌ BAD: Catching all exceptions
try:
    player = await client.player.get(25584)
except Exception:
    pass  # What went wrong? Silent failures are dangerous!
```

### 5. Use Appropriate Timeout

```python
# ✅ GOOD: Reasonable timeout for your use case
client = AsyncIfpaClient(timeout=30.0)  # Long-running queries

# ❌ BAD: Too short timeout
client = AsyncIfpaClient(timeout=1.0)  # May timeout on slow connections
```

## Troubleshooting

### ResourceWarning: unclosed transport

**Problem:** Forgot to close client

**Solution:** Use `async with` context manager

```python
async with AsyncIfpaClient() as client:
    player = await client.player.get(25584)  # Dwayne Smith
```

### RuntimeError: Event loop is closed

**Problem:** Trying to use async client outside async context

**Solution:** Always call async methods from within an async function and use `asyncio.run()`

```python
# ❌ BAD
client = AsyncIfpaClient()
player = await client.player.get(25584)  # SyntaxError! await only works in async functions

# ✅ GOOD
async def main():
    async with AsyncIfpaClient() as client:
        player = await client.player.get(25584)  # Dwayne Smith
        print(f"{player.first_name} {player.last_name}")

asyncio.run(main())
```

### Timeout Errors

**Problem:** Requests taking too long

**Solution:** Increase timeout or check network

```python
# Increase timeout for slow connections or large queries
client = AsyncIfpaClient(timeout=60.0)

# Or handle timeouts gracefully
from httpx import TimeoutException

try:
    player = await client.player.get(25584)  # Dwayne Smith
except IfpaApiError as e:
    if "timeout" in e.message.lower():
        print("Request timed out, try again later")
    else:
        print(f"API Error: {e.message}")
```

## Summary

- Use `AsyncIfpaClient` for async applications
- Always use `async with` context managers
- Add `await` before method calls that make API requests
- Filter methods (`.country()`, `.limit()`) are sync
- Use `asyncio.gather()` for concurrent requests
- Implement rate limiting yourself if needed
- Handle errors with specific exception types
- Reuse clients across multiple requests

For more information, see:

- [Player Guide](../resources/players.md) - Player operations and search
- [Tournament Guide](../resources/tournaments.md) - Tournament operations
- [Director Guide](../resources/directors.md) - Director operations
- [Rankings Guide](../resources/rankings.md) - WPPR rankings
