# Models Reference

The SDK uses Pydantic models for type-safe request and response handling.

## Common Enums

### TimePeriod

```python
class TimePeriod(str, Enum):
    PAST = "past"
    FUTURE = "future"
```

Used for filtering director tournaments by time period.

### RankingSystem

```python
class RankingSystem(str, Enum):
    MAIN = "main"
    WOMEN = "women"
    YOUTH = "youth"
    VIRTUAL = "virtual"
    PRO = "pro"
```

Different IFPA ranking systems.

### ResultType

```python
class ResultType(str, Enum):
    ACTIVE = "active"
    NONACTIVE = "nonactive"
    INACTIVE = "inactive"
```

Player result activity status.

### TournamentType

```python
class TournamentType(str, Enum):
    OPEN = "open"
    WOMEN = "women"
    YOUTH = "youth"
```

Tournament type classifications.

## Player Models

### Player

Main player profile model with fields including:

- `player_id`: int
- `first_name`: str
- `last_name`: str
- `city`: str
- `stateprov`: str
- `country_name`: str
- `current_wppr_rank`: int
- `current_wppr_value`: float
- `active_events`: int
- `highest_rank`: int
- `highest_rank_date`: str

### PlayerSearchResponse

Response from player search with:

- `players`: list[Player]
- `total_count`: int

### PvpComparison

Head-to-head comparison with:

- `player1_name`: str
- `player2_name`: str
- `player1_wins`: int
- `player2_wins`: int
- `ties`: int
- `total_meetings`: int
- `tournaments`: list[PvpTournament]

## Rankings Models

### RankingsResponse

Rankings list response with:

- `rankings`: list[RankingEntry]
- `total_count`: int

### RankingEntry

Individual ranking entry with:

- `rank`: int
- `player_id`: int
- `player_name`: str
- `country_name`: str
- `rating`: float

## Tournament Models

### Tournament

Tournament information with:

- `tournament_id`: int
- `tournament_name`: str
- `city`: str
- `stateprov`: str
- `country_name`: str
- `event_date`: str
- `player_count`: int
- `tournament_director`: str

### TournamentSearchResponse

Search results with:

- `tournaments`: list[Tournament]
- `total_count`: int

## Director Models

### Director

Director profile with:

- `director_id`: int
- `first_name`: str
- `last_name`: str
- `email`: str
- `city`: str
- `stateprov`: str
- `country_name`: str

## Series Models

### SeriesListResponse

List of series with:

- `series`: list[Series]

### Series

Series information with:

- `series_code`: str
- `series_name`: str
- `active`: bool

## Reference Models

### CountryListResponse

Response from countries endpoint with:

- `country`: list[Country]

### Country

Country information with:

- `country_id`: int
- `country_name`: str
- `country_code`: str
- `active_flag`: str

### StateProvListResponse

Response from state/province endpoint with:

- `stateprov`: list[CountryRegions]

### CountryRegions

Country with regions with:

- `country_id`: int
- `country_name`: str
- `country_code`: str
- `regions`: list[Region]

### Region

State or province information with:

- `region_name`: str
- `region_code`: str

For complete model definitions, see the source code in `src/ifpa_api/models/`.
