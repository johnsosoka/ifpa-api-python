# Directors

The Directors resource provides access to tournament director information and their tournament history.

## Search for Directors

```python
from ifpa_sdk import IfpaClient

client = IfpaClient()

# Search by name
directors = client.directors.search(name="Josh")
for director in directors.directors:
    print(f"{director.director_id}: {director.first_name} {director.last_name}")
```

## Get Director Details

```python
# Get director profile
director = client.director(1000).get()
print(f"Name: {director.first_name} {director.last_name}")
print(f"Email: {director.email}")
print(f"City: {director.city}, {director.stateprov}")
```

## Get Director's Tournaments

```python
from ifpa_sdk import TimePeriod

# Get past tournaments
past = client.director(1000).tournaments(TimePeriod.PAST)
for tournament in past.tournaments:
    print(f"{tournament.tournament_name} ({tournament.event_date})")

# Get upcoming tournaments
upcoming = client.director(1000).tournaments(TimePeriod.FUTURE)
```

## Get Country Directors

```python
# List all tournament directors by country
country_dirs = client.directors.country_directors()
for director in country_dirs.directors:
    print(f"{director.country}: {director.director_count} directors")
```

For complete examples and detailed usage, see the [README](https://github.com/jscom/ifpa-sdk#directors).
