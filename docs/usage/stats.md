# Statistics

Access global pinball statistics, trends, and machine popularity data.

## Global Statistics

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get global stats
stats = client.stats.global_stats()
print(f"Total Players: {stats.total_players}")
print(f"Total Tournaments: {stats.total_tournaments}")
print(f"Total Countries: {stats.total_countries}")
```

## Top Countries

```python
# Get top countries by player count
top_countries = client.stats.top_countries(limit=10)
for country in top_countries.countries:
    print(f"{country.country_name}: {country.player_count} players")
```

## Machine Popularity

```python
# Get most played machines
machines = client.stats.machine_popularity(period="year")
for machine in machines.machines:
    print(f"{machine.machine_name}: {machine.play_count} plays")
```

For complete examples, see the [README](https://github.com/jscom/ifpa-sdk#statistics).
