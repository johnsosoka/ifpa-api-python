# Rankings

Access various IFPA ranking systems including WPPR, women's, youth, and more.

## Main WPPR Rankings

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Get top 100 players
rankings = client.rankings.wppr(start_pos=0, count=100)
for entry in rankings.rankings:
    print(f"{entry.rank}. {entry.player_name}: {entry.rating}")
```

## Women's Rankings

```python
women = client.rankings.women(start_pos=0, count=50)
```

## Youth Rankings

```python
youth = client.rankings.youth(start_pos=0, count=50)
```

## Professional Circuit Rankings

```python
pro = client.rankings.pro(start_pos=0, count=50)
```

## Country Rankings

```python
countries = client.rankings.by_country(start_pos=0, count=25)
for entry in countries.country_rankings:
    print(f"{entry.rank}. {entry.country_name}: {entry.total_players} players")
```

## Filter by Country

```python
# Get US rankings only
us_rankings = client.rankings.wppr(country="US", count=100)
```

For complete examples, see the [README](https://github.com/jscom/ifpa-sdk#rankings).
