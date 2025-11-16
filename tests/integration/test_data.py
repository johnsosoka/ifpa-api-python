"""Shared test data fixtures for integration tests.

Test player selection rationale:
- Idaho Pinball Museum community provides stable, predictable test data
- Dwayne Smith (25584): Rank #753, 433 events, 375 PVP competitors - Highly active
- Debbie Smith (47585): Rank #7078, 247 events, 92 PVP competitors - Active
- Dave Fellows (52913): Rank #3303, 359 events, 150 PVP competitors - Active
- John Sosoka (50104): Rank #47572, 4 events, 0 PVP competitors - Low activity (project owner)
- Anna Rigas (50106): Not ranked, last played 2017 - Truly inactive (John's wife)
- Extensive PVP history: 197-305 tournaments together between Dwayne, Debbie, and Dave

All IDs verified against live IFPA API on 2025-11-15.
"""

import pytest

# === PRIMARY TEST PLAYERS (Idaho Pinball Community) ===

# Highly active player (top 1000 ranked)
TEST_PLAYER_HIGHLY_ACTIVE_ID = 25584  # Dwayne Smith - Rank #753, 433 events

# Active players (ranked, regular participation)
TEST_PLAYER_ACTIVE_ID_1 = 47585  # Debbie Smith - Rank #7078, 247 events
TEST_PLAYER_ACTIVE_ID_2 = 52913  # Dave Fellows - Rank #3303, 359 events

# Low activity player (ranked but minimal events)
TEST_PLAYER_LOW_ACTIVITY_ID = 50104  # John Sosoka - Rank #47572, 4 events

# Truly inactive player (last played 2017, not ranked)
TEST_PLAYER_INACTIVE_ID = 50106  # Anna Rigas - Not ranked, 0 active events

# === PVP TEST PAIRS (Confirmed Tournament History) ===

# Primary PVP pair (205 tournaments together)
TEST_PVP_PAIR_PRIMARY = (25584, 47585)  # Dwayne vs Debbie

# Alternative PVP pairs for additional testing
TEST_PVP_PAIR_ALT_1 = (25584, 52913)  # Dwayne vs Dave (305 tournaments)
TEST_PVP_PAIR_ALT_2 = (47585, 52913)  # Debbie vs Dave (197 tournaments)

# Players who have never competed (for PlayersNeverMetError testing)
# NOTE: Previous pair (25584, 50104) was incorrect - they competed in 3 tournaments
TEST_PVP_NEVER_MET = (50104, 1)  # John Sosoka vs World #1 (never met)

# === PLAYER GROUPS ===

# Mixed activity levels for get_multiple testing
TEST_PLAYER_IDS_MULTIPLE = [25584, 50104, 50106]  # Highly active, low, inactive

# All active Idaho players
TEST_PLAYER_IDS_ACTIVE = [25584, 47585, 52913]  # Dwayne, Debbie, Dave

# All Idaho players (for community testing)
TEST_PLAYER_IDS_IDAHO = [25584, 47585, 52913, 50104]

# === KNOWN-GOOD SEARCH PATTERNS ===

# Search returns exactly 2 Smiths from Idaho
TEST_SEARCH_IDAHO_SMITHS = {"name": "Smith", "stateprov": "ID", "count": 10}

# Search returns exactly 5 Johns from Idaho
TEST_SEARCH_IDAHO_JOHNS = {"name": "John", "stateprov": "ID", "count": 5}

# Search returns Dave Fellows in results
TEST_SEARCH_IDAHO_DAVE = {"name": "Dave", "stateprov": "ID", "count": 20}

# Search returns PAPA winners (large, stable dataset)
TEST_SEARCH_PAPA_WINNERS = {"tournament": "PAPA", "tourpos": 1, "count": 10}

# === COMMON TEST PARAMETERS ===

TEST_COUNTRY_CODE = "US"
TEST_STATE_CODE = "ID"
TEST_CITY_BOISE = "Boise"

TEST_COUNT_SMALL = 5
TEST_COUNT_MEDIUM = 10
TEST_COUNT_LARGE = 50

# === TOURNAMENT DATA ===

# Known stable tournament ID
TEST_TOURNAMENT_ID = 7070  # PAPA 17 (2014) - well-known historical tournament

# Date ranges for testing
TEST_YEAR_START = 2020
TEST_YEAR_END = 2024

# === DIRECTOR DATA ===

# Active tournament director with stable history
TEST_DIRECTOR_ACTIVE_ID = 1533  # Josh Rainwater - 13 tournaments, 120 unique players, Columbia SC

# Common director search patterns
TEST_DIRECTOR_SEARCH_JOSH = {"name": "Josh", "count": 30}  # Returns ~26 directors


# === FIXTURES ===


@pytest.fixture
def player_highly_active_id() -> int:
    """Highly active player ID for testing.

    Returns:
        Player ID 25584 (Dwayne Smith):
        - Rank: #753 (top 1000)
        - Total events: 433
        - Active events: 218
        - PVP competitors: 375
        - Location: Boise, ID

    Use this fixture for tests requiring a player with extensive tournament
    history, high activity level, and many PVP competitors.

    Example:
        ```python
        def test_highly_active_player(client, player_highly_active_id):
            player = client.player(player_highly_active_id).details()
            assert int(player.player_stats["system"]["open"]["current_rank"]) < 1000
        ```
    """
    return TEST_PLAYER_HIGHLY_ACTIVE_ID


@pytest.fixture
def player_active_id() -> int:
    """Active player ID for testing (primary active player).

    Returns:
        Player ID 47585 (Debbie Smith):
        - Rank: #7078
        - Total events: 247
        - Active events: 81
        - PVP competitors: 92
        - Location: Boise, ID

    Use this fixture for tests requiring an active player with regular
    tournament participation.

    Example:
        ```python
        def test_get_active_player(client, player_active_id):
            player = client.player(player_active_id).details()
            assert player.player_id == player_active_id
        ```
    """
    return TEST_PLAYER_ACTIVE_ID_1


@pytest.fixture
def player_active_id_2() -> int:
    """Secondary active player ID for testing.

    Returns:
        Player ID 52913 (Dave Fellows):
        - Rank: #3303
        - Total events: 359
        - Active events: 189
        - PVP competitors: 150
        - Location: Boise, ID

    Use this fixture when you need a second active player for comparison
    or multi-player tests.

    Example:
        ```python
        def test_compare_active_players(client, player_active_id, player_active_id_2):
            player1 = client.player(player_active_id).details()
            player2 = client.player(player_active_id_2).details()
            assert player1.player_id != player2.player_id
        ```
    """
    return TEST_PLAYER_ACTIVE_ID_2


@pytest.fixture
def player_inactive_id() -> int:
    """Truly inactive player ID for testing.

    Returns:
        Player ID 50106 (Anna Rigas):
        - Rank: Not ranked (0)
        - Total events: 4
        - Active events: 0
        - Last played: 2017-06-01 (8+ years ago)
        - PVP competitors: 0

    Use this fixture for tests requiring a player with no recent activity
    and no current ranking.

    Example:
        ```python
        def test_handle_inactive_player(client, player_inactive_id):
            player = client.player(player_inactive_id).details()
            stats = player.player_stats["system"]["open"]
            assert stats["current_rank"] == "0"
            assert float(stats["active_points"]) == 0.0
        ```
    """
    return TEST_PLAYER_INACTIVE_ID


@pytest.fixture
def pvp_pair_primary() -> tuple[int, int]:
    """Primary PVP test pair with extensive tournament history.

    Returns:
        Tuple (25584, 47585) - Dwayne Smith vs Debbie Smith
        - Competed in 205 tournaments together
        - Both active players from Boise, ID

    Use this fixture for PVP tests requiring players who have actually
    competed together.

    Note: PVP tests will fail due to SDK bug (model expects player1_id,
    API returns nested player_1 structure). Mark tests as expected to fail
    until SDK bug is fixed.

    Example:
        ```python
        def test_pvp_extensive_history(client, pvp_pair_primary):
            player1_id, player2_id = pvp_pair_primary
            comparison = client.player(player1_id).pvp(player2_id)
            assert comparison.total_meetings >= 200
        ```
    """
    return TEST_PVP_PAIR_PRIMARY


@pytest.fixture
def pvp_pair_never_met() -> tuple[int, int]:
    """PVP pair that have never competed together.

    Returns:
        Tuple (50104, 1) - John Sosoka vs World #1 player
        - Have never competed in same tournament
        - API returns 200 with error message in body

    Use this fixture for testing API error handling when players never met.

    Note: API returns HTTP 200 with body:
    {"message":"These users have never played in the same tournament","code":"404"}

    Example:
        ```python
        def test_pvp_never_met_error(client, pvp_pair_never_met):
            from ifpa_api.exceptions import IfpaApiError
            player1_id, player2_id = pvp_pair_never_met
            with pytest.raises(IfpaApiError):
                client.player(player1_id).pvp(player2_id)
        ```
    """
    return TEST_PVP_NEVER_MET


@pytest.fixture
def player_ids_multiple() -> list[int]:
    """List of player IDs with mixed activity levels.

    Returns:
        List [25584, 50104, 50106]:
        - 25584 (Dwayne): Highly active, rank #753
        - 50104 (John): Low activity, rank #47572
        - 50106 (Anna): Inactive, not ranked

    Use this fixture for testing get_multiple() with diverse player types.

    Example:
        ```python
        def test_get_multiple_mixed(client, player_ids_multiple):
            result = client.player.get_multiple(player_ids_multiple)
            assert len(result.player) == len(player_ids_multiple)
        ```
    """
    return TEST_PLAYER_IDS_MULTIPLE.copy()


@pytest.fixture
def player_ids_active() -> list[int]:
    """List of active Idaho player IDs.

    Returns:
        List [25584, 47585, 52913] - Dwayne, Debbie, Dave
        All are active, ranked players from Boise, ID

    Use this fixture for testing batch operations on active players.

    Example:
        ```python
        def test_get_multiple_active(client, player_ids_active):
            result = client.player.get_multiple(player_ids_active)
            for player in result.player:
                assert int(player.player_stats["system"]["open"]["current_rank"]) > 0
        ```
    """
    return TEST_PLAYER_IDS_ACTIVE.copy()


@pytest.fixture
def search_idaho_smiths() -> dict[str, str | int]:
    """Search pattern returning exactly 2 Smiths from Idaho.

    Returns:
        Dict with name="Smith", stateprov="ID", count=10

    Expected results:
        - Dwayne Smith (25584) - Rank #753
        - Debbie Smith (47585) - Rank #7078

    Use this fixture for testing search with predictable, stable results.

    Example:
        ```python
        def test_search_smiths(client, search_idaho_smiths):
            result = client.player.search(**search_idaho_smiths)
            assert len(result.search) == 2
            player_ids = {p.player_id for p in result.search}
            assert 25584 in player_ids
            assert 47585 in player_ids
        ```
    """
    return TEST_SEARCH_IDAHO_SMITHS.copy()  # type: ignore[return-value]


@pytest.fixture
def search_idaho_johns() -> dict[str, str | int]:
    """Search pattern returning exactly 5 Johns from Idaho.

    Returns:
        Dict with name="John", stateprov="ID", count=5

    Expected results: 5 players named John from Idaho, including:
        - John Sosoka (50104)

    Use this fixture for testing search count accuracy.

    Example:
        ```python
        def test_search_johns_count(client, search_idaho_johns):
            result = client.player.search(**search_idaho_johns)
            assert len(result.search) == 5
            player_ids = {p.player_id for p in result.search}
            assert 50104 in player_ids  # John Sosoka
        ```
    """
    return TEST_SEARCH_IDAHO_JOHNS.copy()  # type: ignore[return-value]


@pytest.fixture
def tournament_id() -> int:
    """Known tournament ID for testing.

    Returns:
        Tournament ID 7070 (PAPA 17 - 2014)
        Well-known historical tournament with reliable data.

    Example:
        ```python
        def test_tournament_results(client, tournament_id):
            results = client.tournament(tournament_id).results()
            assert results is not None
        ```
    """
    return TEST_TOURNAMENT_ID


@pytest.fixture
def country_code() -> str:
    """Default country code for testing.

    Returns:
        Country code "US"

    Example:
        ```python
        def test_search_us_players(client, country_code):
            result = client.player.search(country=country_code, count=5)
            assert result.search is not None
        ```
    """
    return TEST_COUNTRY_CODE


@pytest.fixture
def count_small() -> int:
    """Small count value for testing (5 results).

    Useful for quick tests with minimal API response processing.
    """
    return TEST_COUNT_SMALL


@pytest.fixture
def count_medium() -> int:
    """Medium count value for testing (10 results).

    Useful for testing pagination and moderate result sets.
    """
    return TEST_COUNT_MEDIUM


@pytest.fixture
def count_large() -> int:
    """Large count value for testing (50 results).

    Useful for testing substantial result sets.
    """
    return TEST_COUNT_LARGE


@pytest.fixture
def year_start() -> int:
    """Start year for date range testing (2020)."""
    return TEST_YEAR_START


@pytest.fixture
def year_end() -> int:
    """End year for date range testing (2024)."""
    return TEST_YEAR_END


@pytest.fixture
def director_active_id() -> int:
    """Active tournament director ID for testing.

    Returns:
        Director ID 1533 (Josh Rainwater):
        - Location: Columbia, SC
        - Tournament count: 13
        - Unique player count: 120
        - Has both past and future tournaments

    Use this fixture for tests requiring an active director with tournament history.

    Example:
        ```python
        def test_get_director_details(client, director_active_id):
            director = client.director(director_active_id).details()
            assert director.director_id == director_active_id
            assert director.stats.tournament_count > 0
        ```
    """
    return TEST_DIRECTOR_ACTIVE_ID
