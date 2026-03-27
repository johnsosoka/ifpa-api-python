# Practical Examples

Real-world use cases and patterns for the IFPA API Python SDK.

---

## 1. Batch Player Lookup with Error Handling

Fetch multiple players efficiently while handling missing players gracefully.

**Use case:** Building a leaderboard, importing player data, or validating a list of player IDs.

```python
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.player import Player

client = IfpaClient()

# List of player IDs to look up
player_ids = [25584, 47585, 52913, 50104, 999999]  # 999999 likely doesn't exist
players: list[Player] = []
errors: list[tuple[int, int]] = []  # (player_id, status_code)

for player_id in player_ids:
    try:
        player = client.player.get(player_id)
        players.append(player)
        print(f"✓ Found: {player.first_name} {player.last_name}")
    except IfpaApiError as e:
        if e.status_code == 404:
            print(f"✗ Player {player_id} not found")
            errors.append((player_id, 404))
        elif e.status_code == 429:
            print(f"⚠ Rate limited on player {player_id}")
            errors.append((player_id, 429))
        else:
            print(f"⚠ API error {e.status_code} for player {player_id}: {e.message}")
            errors.append((player_id, e.status_code))

print(f"\nSummary: Found {len(players)} of {len(player_ids)} players")
if errors:
    print(f"Errors: {len(errors)} players could not be retrieved")
```

---

## 2. Caching API Responses with @lru_cache

Avoid repeated API calls for frequently accessed data using Python's built-in caching.

**Use case:** Web applications, dashboards, or scripts that access the same players or tournaments multiple times.

```python
from functools import lru_cache
from ifpa_api import IfpaClient
from ifpa_api.models.player import Player
from ifpa_api.models.tournaments import Tournament

client = IfpaClient()

@lru_cache(maxsize=128)
def get_player_cached(player_id: int) -> Player:
    """Get player with caching to avoid repeated API calls."""
    return client.player.get(player_id)

@lru_cache(maxsize=64)
def get_tournament_cached(tournament_id: int) -> Tournament:
    """Get tournament with caching."""
    return client.tournament.get(tournament_id)

# First call hits the API
player1 = get_player_cached(25584)
print(f"First call: {player1.first_name} {player1.last_name}")

# Second call uses cache (no API request)
player2 = get_player_cached(25584)
print(f"Second call: {player2.first_name} {player2.last_name} (from cache)")

# Check cache statistics
print(f"\nCache info: {get_player_cached.cache_info()}")

# Clear cache if needed (e.g., after long-running process)
# get_player_cached.cache_clear()
```

---

## 3. Rate Limiting / Retry Logic

Implement exponential backoff for production scripts that may hit API rate limits.

**Use case:** Batch processing, data imports, or any automated script making many API calls.

```python
import time
from ifpa_api import IfpaClient, IfpaApiError
from ifpa_api.models.player import Player

client = IfpaClient()

def get_with_backoff(player_id: int, max_retries: int = 3) -> Player:
    """Get player with exponential backoff on rate limits.

    Args:
        player_id: IFPA player ID
        max_retries: Maximum number of retry attempts

    Returns:
        Player object

    Raises:
        IfpaApiError: If all retries exhausted or non-retryable error
    """
    for attempt in range(max_retries):
        try:
            return client.player.get(player_id)
        except IfpaApiError as e:
            # Rate limited (429) or server errors (5xx) - retry with backoff
            if e.status_code in (429, 500, 502, 503, 504):
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"Rate limited (attempt {attempt + 1}), waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            # Other errors or retries exhausted - raise
            raise

# Use in batch processing
player_ids = [25584, 47585, 52913, 50104]

for pid in player_ids:
    try:
        player = get_with_backoff(pid)
        print(f"✓ {player.first_name} {player.last_name}")
    except IfpaApiError as e:
        print(f"✗ Failed to get player {pid}: {e.status_code} - {e.message}")
        # Continue with next player instead of crashing
        continue
```

---

## 4. Exporting Data to CSV

Export rankings or search results to CSV for analysis in spreadsheet applications.

**Use case:** Creating reports, sharing data with tournament organizers, or offline analysis.

```python
import csv
import json
from datetime import datetime
from ifpa_api import IfpaClient
from ifpa_api.models.rankings import RankingsResponse
from ifpa_api.models.player import PlayerSearchResponse

client = IfpaClient()

# Export top 100 WPPR rankings to CSV
def export_rankings_to_csv(filename: str, count: int = 100) -> None:
    """Export WPPR rankings to a CSV file."""
    rankings: RankingsResponse = client.rankings.wppr(count=count)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Rank', 'Player Name', 'Rating', 'Country', 'State'])

        for entry in rankings.rankings:
            writer.writerow([
                entry.rank,
                entry.player_name,
                entry.rating,
                entry.country_code,
                entry.stateprov or ''
            ])

    print(f"Exported {len(rankings.rankings)} rankings to {filename}")

# Export player search results to CSV
def export_players_to_csv(filename: str, search_results: PlayerSearchResponse) -> None:
    """Export player search results to CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'City', 'State', 'Country', 'WPPR Rank'])

        for player in search_results.search:
            writer.writerow([
                player.player_id,
                f"{player.first_name} {player.last_name}",
                player.city or '',
                player.state or '',
                player.country or '',
                player.wppr_rank or 'Unranked'
            ])

    print(f"Exported {len(search_results.search)} players to {filename}")

# Export to JSON for programmatic use
def export_to_json(data, filename: str) -> None:
    """Export Pydantic models to JSON."""
    with open(filename, 'w') as f:
        if hasattr(data, 'model_dump'):
            # Single model
            json.dump(data.model_dump(), f, indent=2, default=str)
        elif hasattr(data, '__iter__'):
            # List of models
            json.dump([item.model_dump() for item in data], f, indent=2, default=str)

    print(f"Exported to {filename}")

# Example usage
if __name__ == "__main__":
    # Export rankings
    timestamp = datetime.now().strftime("%Y%m%d")
    export_rankings_to_csv(f"wppr_rankings_{timestamp}.csv", count=100)

    # Export search results
    results = client.player.query("Smith").country("US").limit(50).get()
    export_players_to_csv(f"smith_players_{timestamp}.csv", results)

    # Export as JSON for further processing
    export_to_json(results.search, f"smith_players_{timestamp}.json")
```

---

## 5. Tournament Results Analysis

Analyze tournament results to find frequent top finishers or calculate statistics.

**Use case:** Tracking player performance across a series, identifying rising stars, or tournament director analytics.

```python
from collections import Counter, defaultdict
from ifpa_api import IfpaClient
from ifpa_api.models.tournaments import TournamentResultsResponse

client = IfpaClient()

# Analyze top finishers across multiple tournaments
def analyze_top_finishers(tournament_ids: list[int], top_n: int = 10) -> Counter:
    """Count how many times each player finished in the top N.

    Args:
        tournament_ids: List of tournament IDs to analyze
        top_n: Number of top positions to consider (default: 10)

    Returns:
        Counter of player names to top-N finishes
    """
    finisher_counts = Counter()

    for tid in tournament_ids:
        try:
            results: TournamentResultsResponse = client.tournament(tid).results()
            tournament_name = results.tournament_name or f"Tournament {tid}"

            # Count top N finishers
            for result in results.results[:top_n]:
                finisher_counts[result.player_name] += 1

            print(f"✓ Analyzed: {tournament_name}")
        except Exception as e:
            print(f"✗ Failed to get tournament {tid}: {e}")
            continue

    return finisher_counts

# Calculate average finish position for players
def calculate_average_positions(tournament_id: int) -> dict[str, float]:
    """Calculate average finish positions for a tournament's players.

    Note: This is a single tournament example. For multiple tournaments,
    you'd aggregate results across all tournaments.
    """
    results: TournamentResultsResponse = client.tournament(tournament_id).results()

    # Group by country
    country_positions = defaultdict(list)

    for result in results.results:
        country = result.country_code or 'Unknown'
        country_positions[country].append(result.position)

    # Calculate averages
    averages = {
        country: sum(positions) / len(positions)
        for country, positions in country_positions.items()
    }

    return averages

# Find players who improved their position
def find_improving_players(tournament_ids: list[int]) -> list[dict]:
    """Find players who consistently improved across tournaments.

    Args:
        tournament_ids: List of tournament IDs in chronological order

    Returns:
        List of player improvement records
    """
    player_history = defaultdict(list)

    for tid in tournament_ids:
        results: TournamentResultsResponse = client.tournament(tid).results()

        for result in results.results:
            player_history[result.player_name].append({
                'tournament_id': tid,
                'position': result.position,
                'tournament_name': results.tournament_name
            })

    # Find players with improving trends
    improving = []
    for player_name, history in player_history.items():
        if len(history) >= 3:  # Need at least 3 tournaments
            positions = [h['position'] for h in history]
            # Simple check: last position better than first
            if positions[-1] < positions[0]:
                improving.append({
                    'player': player_name,
                    'first_position': positions[0],
                    'last_position': positions[-1],
                    'tournaments': len(history)
                })

    return sorted(improving, key=lambda x: x['first_position'] - x['last_position'], reverse=True)

# Example usage
if __name__ == "__main__":
    # Example tournament IDs (replace with actual IDs)
    tournament_ids = [12345, 12346, 12347]

    print("=== Top 10 Finishers Analysis ===")
    top_finishers = analyze_top_finishers(tournament_ids, top_n=10)
    print("\nMost frequent top-10 finishers:")
    for name, count in top_finishers.most_common(5):
        print(f"  {name}: {count} tournaments")

    print("\n=== Country Performance ===")
    if tournament_ids:
        averages = calculate_average_positions(tournament_ids[0])
        for country, avg_pos in sorted(averages.items(), key=lambda x: x[1]):
            print(f"  {country}: avg position {avg_pos:.1f}")
```

---

## 6. Working with Series Regions

Query series standings and regional data for championship series like NACS.

**Use case:** Tracking regional championship standings, finding series events, or analyzing player performance within a series.

```python
from ifpa_api import IfpaClient
from ifpa_api.models.series import SeriesStandingsResponse, SeriesRegionsResponse

client = IfpaClient()

# Get overall series standings
def get_series_standings(series_code: str, year: int | None = None):
    """Get standings for a championship series.

    Args:
        series_code: Series code (e.g., "NACS" for North American Championship Series)
        year: Optional year filter
    """
    standings: SeriesStandingsResponse = client.series(series_code).standings()

    print(f"=== {series_code} Standings ===")
    print(f"Total players: {len(standings.standings)}")

    # Show top 10
    for i, player in enumerate(standings.standings[:10], 1):
        print(f"{i}. {player.player_name} - {player.total_points} points")

    return standings

# Get regional standings
def get_regional_standings(series_code: str, region_code: str):
    """Get standings for a specific region within a series.

    Args:
        series_code: Series code (e.g., "NACS")
        region_code: Region code (e.g., "OH" for Ohio, "ID" for Idaho)
    """
    standings = client.series(series_code).region_standings(region_code)

    print(f"=== {series_code} - {region_code} Region Standings ===")
    print(f"Total players: {len(standings.standings)}")

    for i, player in enumerate(standings.standings[:10], 1):
        print(f"{i}. {player.player_name} - {player.total_points} points")

    return standings

# List all regions in a series
def list_series_regions(series_code: str):
    """List all available regions for a series."""
    regions: SeriesRegionsResponse = client.series(series_code).regions()

    print(f"=== {series_code} Regions ===")
    print(f"Total regions: {len(regions.regions)}")

    for region in regions.regions:
        print(f"  {region.region_code}: {region.region_name}")
        if hasattr(region, 'player_count'):
            print(f"    Players: {region.player_count}")

    return regions

# Get player card in series context
def get_series_player_card(series_code: str, player_id: int, region_code: str | None = None):
    """Get a player's series performance card.

    Args:
        series_code: Series code
        player_id: IFPA player ID
        region_code: Optional region code for regional card
    """
    if region_code:
        card = client.series(series_code).player_card(player_id, region_code)
        print(f"=== {series_code} - {region_code} Player Card ===")
    else:
        card = client.series(series_code).player_card(player_id)
        print(f"=== {series_code} Player Card ===")

    if hasattr(card, 'player_name'):
        print(f"Player: {card.player_name}")
    if hasattr(card, 'rank'):
        print(f"Rank: {card.rank}")
    if hasattr(card, 'total_points'):
        print(f"Total Points: {card.total_points}")

    return card

# Example: Find top players in your state
def find_top_state_players(state_code: str, series_code: str = "NACS", top_n: int = 5):
    """Find top players from a specific state in a series."""
    standings = client.series(series_code).region_standings(state_code)

    print(f"=== Top {top_n} Players in {state_code} ({series_code}) ===")
    for i, player in enumerate(standings.standings[:top_n], 1):
        print(f"{i}. {player.player_name}")
        if hasattr(player, 'total_points'):
            print(f"   Points: {player.total_points}")
        if hasattr(player, 'event_count'):
            print(f"   Events: {player.event_count}")

# Example usage
if __name__ == "__main__":
    # List all NACS regions
    regions = list_series_regions("NACS")

    # Get overall standings
    standings = get_series_standings("NACS")

    # Get Idaho regional standings
    idaho_standings = get_regional_standings("NACS", "ID")

    # Get a specific player's card
    # player_card = get_series_player_card("NACS", 25584, "ID")
```

---

## Best Practices Summary

1. **Always handle errors** - API calls can fail; use try/except blocks
2. **Cache when appropriate** - Use `@lru_cache` for frequently accessed data
3. **Respect rate limits** - Implement backoff for batch operations
4. **Export for analysis** - CSV/JSON export enables spreadsheet and data science workflows
5. **Batch efficiently** - Process multiple items in loops with proper error handling
6. **Use type hints** - Improves IDE support and catches errors early

## Related Resources

- [Error Handling Guide](error-handling.md) - Detailed error handling patterns
- [Searching Guide](searching.md) - Query builder patterns
- [Pagination Guide](pagination.md) - Handling large result sets
