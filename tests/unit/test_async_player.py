"""Unit tests for async player resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import IfpaApiError, PlayersNeverMetError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import Player, PlayerSearchResponse
from ifpa_api.resources.player.async_client import AsyncPlayerClient
from ifpa_api.resources.player.async_context import AsyncPlayerContext
from ifpa_api.resources.player.async_query_builder import AsyncPlayerQueryBuilder


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_player_client(async_http_client: _AsyncHttpClient) -> AsyncPlayerClient:
    """Create async player client for testing."""
    return AsyncPlayerClient(async_http_client, validate_requests=False)


# AsyncPlayerClient tests


@pytest.mark.asyncio
async def test_player_client_callable_returns_context(
    async_player_client: AsyncPlayerClient,
) -> None:
    """Test that calling player client returns AsyncPlayerContext."""
    context = async_player_client(12345)
    assert isinstance(context, AsyncPlayerContext)
    assert context._resource_id == 12345


@pytest.mark.asyncio
async def test_player_get(
    async_player_client: AsyncPlayerClient, respx_mock: Any, async_http_client: _AsyncHttpClient
) -> None:
    """Test AsyncPlayerClient.get() method."""
    player_data = {
        "player": [
            {
                "player_id": 12345,
                "first_name": "John",
                "last_name": "Doe",
                "city": "Seattle",
                "stateprov": "WA",
                "country_code": "US",
                "country_name": "United States",
                "initials": "JD",
                "age": 30,
                "excluded_flag": "N",
                "ifpa_registered": "Y",
                "current_wppr_rank": 100,
                "last_month_rank": 105,
                "last_year_rank": 110,
                "highest_rank": 95,
                "highest_rank_date": "2024-01-15",
                "current_wppr_value": "50.25",
                "wppr_points_all_time": "500.75",
                "best_finish": 1,
                "best_finish_count": 5,
                "average_finish": 3.5,
                "average_finish_last_five": 2.8,
                "area_code": "206",
                "area_code_two": "425",
                "area_code_three": "",
                "player_stats_url": "https://www.ifpapinball.com/player.php?p=12345",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=player_data)
    )

    player = await async_player_client.get(12345)

    assert isinstance(player, Player)
    assert player.player_id == 12345
    assert player.first_name == "John"
    assert player.last_name == "Doe"


@pytest.mark.asyncio
async def test_player_get_or_none_found(
    async_player_client: AsyncPlayerClient, respx_mock: Any
) -> None:
    """Test get_or_none when player exists."""
    player_data = {
        "player": [
            {
                "player_id": 12345,
                "first_name": "Jane",
                "last_name": "Smith",
                "city": "Portland",
                "stateprov": "OR",
                "country_code": "US",
                "country_name": "United States",
                "initials": "JS",
                "age": 25,
                "excluded_flag": "N",
                "ifpa_registered": "Y",
                "current_wppr_rank": 50,
                "last_month_rank": 52,
                "last_year_rank": 55,
                "highest_rank": 48,
                "highest_rank_date": "2024-02-20",
                "current_wppr_value": "75.50",
                "wppr_points_all_time": "750.25",
                "best_finish": 1,
                "best_finish_count": 10,
                "average_finish": 2.5,
                "average_finish_last_five": 2.0,
                "area_code": "503",
                "area_code_two": "",
                "area_code_three": "",
                "player_stats_url": "https://www.ifpapinball.com/player.php?p=12345",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=player_data)
    )

    player = await async_player_client.get_or_none(12345)

    assert player is not None
    assert player.first_name == "Jane"


@pytest.mark.asyncio
async def test_player_get_or_none_not_found(
    async_player_client: AsyncPlayerClient, respx_mock: Any
) -> None:
    """Test get_or_none when player does not exist (404)."""
    respx_mock.get("https://api.ifpapinball.com/player/99999").mock(
        return_value=Response(404, json={"error": "Player not found"})
    )

    player = await async_player_client.get_or_none(99999)

    assert player is None


@pytest.mark.asyncio
async def test_player_get_or_none_reraises_non_404(
    async_player_client: AsyncPlayerClient, respx_mock: Any
) -> None:
    """Test get_or_none re-raises non-404 errors."""
    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(500, json={"error": "Internal server error"})
    )

    with pytest.raises(IfpaApiError) as exc_info:
        await async_player_client.get_or_none(12345)

    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_player_exists_true(async_player_client: AsyncPlayerClient, respx_mock: Any) -> None:
    """Test exists returns True when player found."""
    player_data = {
        "player": [
            {
                "player_id": 12345,
                "first_name": "John",
                "last_name": "Doe",
                "city": "Seattle",
                "stateprov": "WA",
                "country_code": "US",
                "country_name": "United States",
                "initials": "JD",
                "age": 30,
                "excluded_flag": "N",
                "ifpa_registered": "Y",
                "current_wppr_rank": 100,
                "last_month_rank": 105,
                "last_year_rank": 110,
                "highest_rank": 95,
                "highest_rank_date": "2024-01-15",
                "current_wppr_value": "50.25",
                "wppr_points_all_time": "500.75",
                "best_finish": 1,
                "best_finish_count": 5,
                "average_finish": 3.5,
                "average_finish_last_five": 2.8,
                "area_code": "206",
                "area_code_two": "425",
                "area_code_three": "",
                "player_stats_url": "https://www.ifpapinball.com/player.php?p=12345",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=player_data)
    )

    exists = await async_player_client.exists(12345)

    assert exists is True


@pytest.mark.asyncio
async def test_player_exists_false(async_player_client: AsyncPlayerClient, respx_mock: Any) -> None:
    """Test exists returns False when player not found."""
    respx_mock.get("https://api.ifpapinball.com/player/99999").mock(
        return_value=Response(404, json={"error": "Player not found"})
    )

    exists = await async_player_client.exists(99999)

    assert exists is False


@pytest.mark.asyncio
async def test_player_search_returns_query_builder(
    async_player_client: AsyncPlayerClient,
) -> None:
    """Test search() returns AsyncPlayerQueryBuilder."""
    builder = async_player_client.search("John")

    assert isinstance(builder, AsyncPlayerQueryBuilder)
    assert builder._params["name"] == "John"


@pytest.mark.asyncio
async def test_player_search_without_name(async_player_client: AsyncPlayerClient) -> None:
    """Test search() without name returns empty builder."""
    builder = async_player_client.search()

    assert isinstance(builder, AsyncPlayerQueryBuilder)
    assert "name" not in builder._params


# AsyncPlayerContext tests


@pytest.mark.asyncio
async def test_player_context_details(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test AsyncPlayerContext.details() method."""
    player_data = {
        "player": [
            {
                "player_id": 12345,
                "first_name": "Alice",
                "last_name": "Johnson",
                "city": "Boston",
                "stateprov": "MA",
                "country_code": "US",
                "country_name": "United States",
                "initials": "AJ",
                "age": 28,
                "excluded_flag": "N",
                "ifpa_registered": "Y",
                "current_wppr_rank": 75,
                "last_month_rank": 78,
                "last_year_rank": 80,
                "highest_rank": 70,
                "highest_rank_date": "2024-03-10",
                "current_wppr_value": "60.00",
                "wppr_points_all_time": "600.00",
                "best_finish": 1,
                "best_finish_count": 8,
                "average_finish": 3.0,
                "average_finish_last_five": 2.5,
                "area_code": "617",
                "area_code_two": "",
                "area_code_three": "",
                "player_stats_url": "https://www.ifpapinball.com/player.php?p=12345",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345").mock(
        return_value=Response(200, json=player_data)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    player = await context.details()

    assert isinstance(player, Player)
    assert player.player_id == 12345
    assert player.first_name == "Alice"


@pytest.mark.asyncio
async def test_player_context_pvp_all(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test AsyncPlayerContext.pvp_all() method."""
    pvp_data = {
        "player_id": 12345,
        "total_competitors": 150,
        "system": "MAIN",
        "type": "all",
        "title": "",
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345/pvp").mock(
        return_value=Response(200, json=pvp_data)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    result = await context.pvp_all()

    assert result.total_competitors == 150


@pytest.mark.asyncio
async def test_player_context_pvp_success(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test AsyncPlayerContext.pvp() with successful comparison."""
    pvp_data = {
        "player1_id": 12345,
        "player1_name": "John Doe",
        "player2_id": 67890,
        "player2_name": "Jane Smith",
        "player1_wins": 5,
        "player2_wins": 3,
        "ties": 1,
        "total_meetings": 9,
        "tournaments": [
            {
                "tournament_id": 1,
                "tournament_name": "Test Tournament",
                "event_date": "2024-01-15",
                "player_1_position": 1,
                "player_2_position": 2,
                "winner_player_id": 12345,
            }
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345/pvp/67890").mock(
        return_value=Response(200, json=pvp_data)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    result = await context.pvp(67890)

    assert result.player1_id == 12345
    assert result.player2_id == 67890
    assert result.player1_wins == 5
    assert result.player2_wins == 3


@pytest.mark.asyncio
async def test_player_context_pvp_never_met_404(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test AsyncPlayerContext.pvp() raises PlayersNeverMetError on 404."""
    respx_mock.get("https://api.ifpapinball.com/player/12345/pvp/99999").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)

    with pytest.raises(PlayersNeverMetError) as exc_info:
        await context.pvp(99999)

    assert exc_info.value.player_id == 12345
    assert exc_info.value.opponent_id == 99999


@pytest.mark.asyncio
async def test_player_context_pvp_error_response(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test AsyncPlayerContext.pvp() handles error response with code 404."""
    # API can return HTTP 200 with error payload containing code: "404"
    error_response = {"code": "404", "message": "Players never met"}

    respx_mock.get("https://api.ifpapinball.com/player/12345/pvp/99999").mock(
        return_value=Response(200, json=error_response)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)

    with pytest.raises(PlayersNeverMetError) as exc_info:
        await context.pvp(99999)

    assert exc_info.value.player_id == 12345
    assert exc_info.value.opponent_id == 99999


@pytest.mark.asyncio
async def test_player_context_results(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test AsyncPlayerContext.results() method."""
    results_data = {
        "results": [
            {
                "tournament_id": 1,
                "tournament_name": "Test Tournament",
                "event_date": "2024-01-15",
                "event_name": "Test Event",
                "position": 1,
            }
        ],
        "player_id": 12345,
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345/results/main/active").mock(
        return_value=Response(200, json=results_data)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    result = await context.results(RankingSystem.MAIN, ResultType.ACTIVE)

    assert result.player_id == 12345
    assert len(result.results) == 1


@pytest.mark.asyncio
async def test_player_context_results_with_pagination(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test AsyncPlayerContext.results() with pagination params."""
    results_data = {
        "results": [],
        "player_id": 12345,
        "ranking_system": "main",
        "result_type": "active",
    }

    respx_mock.get(
        "https://api.ifpapinball.com/player/12345/results/main/active",
        params={"start_pos": 0, "count": 25},
    ).mock(return_value=Response(200, json=results_data))

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    result = await context.results(RankingSystem.MAIN, ResultType.ACTIVE, start_pos=0, count=25)

    assert result.player_id == 12345


@pytest.mark.asyncio
async def test_player_context_history(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test AsyncPlayerContext.history() method."""
    history_data = {
        "player_id": 12345,
        "system": "MAIN",
        "active_flag": "Y",
        "rank_history": [
            {
                "rank_date": "2024-01-01",
                "rank_position": "100",
                "wppr_points": "50.25",
                "tournaments_played_count": "25",
            }
        ],
        "rating_history": [{"rating_date": "2024-01-01", "rating": "50.25"}],
    }

    respx_mock.get("https://api.ifpapinball.com/player/12345/rank_history").mock(
        return_value=Response(200, json=history_data)
    )

    context = AsyncPlayerContext(async_http_client, 12345, validate_requests=False)
    result = await context.history()

    assert result.player_id == 12345
    assert len(result.rank_history) == 1


# AsyncPlayerQueryBuilder tests


@pytest.mark.asyncio
async def test_query_builder_query_method(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder query() method."""
    builder = AsyncPlayerQueryBuilder(async_http_client)
    new_builder = builder.query("Smith")

    assert new_builder._params["name"] == "Smith"
    assert "name" not in builder._params  # Original unchanged


@pytest.mark.asyncio
async def test_query_builder_tournament_filter(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder tournament() filter."""
    builder = AsyncPlayerQueryBuilder(async_http_client)
    new_builder = builder.tournament("PAPA")

    assert new_builder._params["tournament"] == "PAPA"
    assert "tournament" not in builder._params


@pytest.mark.asyncio
async def test_query_builder_position_filter(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder position() filter."""
    builder = AsyncPlayerQueryBuilder(async_http_client)
    new_builder = builder.position(1)

    assert new_builder._params["tourpos"] == 1
    assert "tourpos" not in builder._params


@pytest.mark.asyncio
async def test_query_builder_country_filter(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder country() filter from mixin."""
    builder = AsyncPlayerQueryBuilder(async_http_client)
    new_builder = builder.country("US")

    assert new_builder._params["country"] == "US"
    assert "country" not in builder._params


@pytest.mark.asyncio
async def test_query_builder_chained_filters(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder with chained filters."""
    builder = AsyncPlayerQueryBuilder(async_http_client)
    new_builder = builder.query("Smith").country("US").state("WA").limit(25)

    assert new_builder._params["name"] == "Smith"
    assert new_builder._params["country"] == "US"
    assert new_builder._params["stateprov"] == "WA"
    assert new_builder._params["count"] == 25
    assert len(builder._params) == 0  # Original unchanged


@pytest.mark.asyncio
async def test_query_builder_get(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test query builder get() execution."""
    search_data = {
        "search": [
            {
                "player_id": 12345,
                "first_name": "John",
                "last_name": "Smith",
                "city": "Seattle",
                "stateprov": "WA",
                "country_name": "United States",
                "country_code": "US",
                "wppr_rank": "100",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/search", params={"name": "Smith"}).mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncPlayerQueryBuilder(async_http_client).query("Smith")
    result = await builder.get()

    assert isinstance(result, PlayerSearchResponse)
    assert len(result.search) == 1
    assert result.search[0].first_name == "John"


@pytest.mark.asyncio
async def test_query_builder_first(async_http_client: _AsyncHttpClient, respx_mock: Any) -> None:
    """Test query builder first() method."""
    search_data = {
        "search": [
            {
                "player_id": 12345,
                "first_name": "Alice",
                "last_name": "Johnson",
                "city": "Boston",
                "stateprov": "MA",
                "country_name": "United States",
                "country_code": "US",
                "wppr_rank": "75",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/search", params={"name": "Alice"}).mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncPlayerQueryBuilder(async_http_client).query("Alice")
    result = await builder.first()

    assert result.first_name == "Alice"
    assert result.player_id == 12345


@pytest.mark.asyncio
async def test_query_builder_first_no_results(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first() raises IndexError when no results."""
    search_data: dict[str, Any] = {"search": []}

    respx_mock.get("https://api.ifpapinball.com/player/search", params={"name": "Nobody"}).mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncPlayerQueryBuilder(async_http_client).query("Nobody")

    with pytest.raises(IndexError) as exc_info:
        await builder.first()

    assert "no results" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_query_builder_first_or_none_found(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() returns result."""
    search_data = {
        "search": [
            {
                "player_id": 12345,
                "first_name": "Bob",
                "last_name": "Smith",
                "city": "Portland",
                "stateprov": "OR",
                "country_name": "United States",
                "country_code": "US",
                "wppr_rank": "50",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/player/search", params={"name": "Bob"}).mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncPlayerQueryBuilder(async_http_client).query("Bob")
    result = await builder.first_or_none()

    assert result is not None
    assert result.first_name == "Bob"


@pytest.mark.asyncio
async def test_query_builder_first_or_none_not_found(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() returns None when no results."""
    search_data: dict[str, Any] = {"search": []}

    respx_mock.get("https://api.ifpapinball.com/player/search", params={"name": "Nobody"}).mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncPlayerQueryBuilder(async_http_client).query("Nobody")
    result = await builder.first_or_none()

    assert result is None


@pytest.mark.asyncio
async def test_query_builder_immutability(async_http_client: _AsyncHttpClient) -> None:
    """Test query builder immutability pattern."""
    base = AsyncPlayerQueryBuilder(async_http_client)
    us_query = base.country("US")
    wa_query = us_query.state("WA")
    or_query = us_query.state("OR")

    # Original remains unchanged
    assert "country" not in base._params

    # US query has country but not state
    assert us_query._params["country"] == "US"
    assert "stateprov" not in us_query._params

    # WA query has both
    assert wa_query._params["country"] == "US"
    assert wa_query._params["stateprov"] == "WA"

    # OR query has different state
    assert or_query._params["country"] == "US"
    assert or_query._params["stateprov"] == "OR"

    # WA query unchanged
    assert wa_query._params["stateprov"] == "WA"
