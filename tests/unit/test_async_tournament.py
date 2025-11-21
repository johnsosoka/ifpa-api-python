"""Unit tests for async tournament resource."""

from typing import Any

import pytest
from httpx import Response

from ifpa_api.core.async_http import _AsyncHttpClient
from ifpa_api.core.config import Config
from ifpa_api.core.exceptions import (
    IfpaClientValidationError,
    TournamentNotLeagueError,
)
from ifpa_api.models.tournaments import (
    Tournament,
    TournamentFormatsListResponse,
    TournamentSearchResponse,
)
from ifpa_api.resources.tournament.async_client import AsyncTournamentClient
from ifpa_api.resources.tournament.async_context import AsyncTournamentContext
from ifpa_api.resources.tournament.async_query_builder import AsyncTournamentQueryBuilder


@pytest.fixture
def config() -> Config:
    """Create test configuration."""
    return Config(api_key="test-key", base_url="https://api.ifpapinball.com", timeout=30)


@pytest.fixture
def async_http_client(config: Config) -> _AsyncHttpClient:
    """Create async HTTP client for testing."""
    return _AsyncHttpClient(config)


@pytest.fixture
def async_tournament_client(async_http_client: _AsyncHttpClient) -> AsyncTournamentClient:
    """Create async tournament client for testing."""
    return AsyncTournamentClient(async_http_client, validate_requests=False)


# AsyncTournamentClient tests


@pytest.mark.asyncio
async def test_tournament_client_callable_returns_context(
    async_tournament_client: AsyncTournamentClient,
) -> None:
    """Test that calling tournament client returns AsyncTournamentContext."""
    context = async_tournament_client(12345)
    assert isinstance(context, AsyncTournamentContext)
    assert context._resource_id == 12345


@pytest.mark.asyncio
async def test_tournament_get(
    async_tournament_client: AsyncTournamentClient,
    respx_mock: Any,
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test AsyncTournamentClient.get() method."""
    tournament_data = {
        "tournament_id": 12345,
        "tournament_name": "PAPA World Championship",
        "event_date": "2024-01-15",
        "city": "Carnegie",
        "state": "PA",
        "country_code": "US",
        "country_name": "United States",
        "venue": "ReplayFX",
        "director_name": "Josh Sharpe",
        "player_count": 200,
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345").mock(
        return_value=Response(200, json=tournament_data)
    )

    tournament = await async_tournament_client.get(12345)

    assert isinstance(tournament, Tournament)
    assert tournament.tournament_id == 12345
    assert tournament.tournament_name == "PAPA World Championship"


@pytest.mark.asyncio
async def test_tournament_get_or_none_found(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test get_or_none when tournament exists."""
    tournament_data = {
        "tournament_id": 12345,
        "tournament_name": "PAPA World Championship",
        "event_date": "2024-01-15",
        "city": "Carnegie",
        "state": "PA",
        "country_code": "US",
        "country_name": "United States",
        "venue": "ReplayFX",
        "director_name": "Josh Sharpe",
        "player_count": 200,
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345").mock(
        return_value=Response(200, json=tournament_data)
    )

    tournament = await async_tournament_client.get_or_none(12345)

    assert tournament is not None
    assert tournament.tournament_name == "PAPA World Championship"


@pytest.mark.asyncio
async def test_tournament_get_or_none_not_found(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test get_or_none when tournament doesn't exist (404)."""
    respx_mock.get("https://api.ifpapinball.com/tournament/99999").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    tournament = await async_tournament_client.get_or_none(99999)

    assert tournament is None


@pytest.mark.asyncio
async def test_tournament_exists_true(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test exists() returns True when tournament exists."""
    tournament_data = {
        "tournament_id": 12345,
        "tournament_name": "PAPA World Championship",
        "event_date": "2024-01-15",
        "city": "Carnegie",
        "state": "PA",
        "country_code": "US",
        "country_name": "United States",
        "venue": "ReplayFX",
        "director_name": "Josh Sharpe",
        "player_count": 200,
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345").mock(
        return_value=Response(200, json=tournament_data)
    )

    exists = await async_tournament_client.exists(12345)

    assert exists is True


@pytest.mark.asyncio
async def test_tournament_exists_false(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test exists() returns False when tournament doesn't exist."""
    respx_mock.get("https://api.ifpapinball.com/tournament/99999").mock(
        return_value=Response(404, json={"error": "Not found"})
    )

    exists = await async_tournament_client.exists(99999)

    assert exists is False


@pytest.mark.asyncio
async def test_tournament_search_returns_query_builder(
    async_tournament_client: AsyncTournamentClient,
) -> None:
    """Test search() returns AsyncTournamentQueryBuilder."""
    builder = async_tournament_client.search("PAPA")
    assert isinstance(builder, AsyncTournamentQueryBuilder)


@pytest.mark.asyncio
async def test_tournament_list_formats(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test list_formats() method."""
    formats_data = {
        "qualifying_formats": [
            {"format_id": 1, "name": "Swiss", "description": "Swiss-style tournament"}
        ],
        "finals_formats": [
            {"format_id": 10, "name": "Single Elimination", "description": "Bracket style"}
        ],
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/formats").mock(
        return_value=Response(200, json=formats_data)
    )

    response = await async_tournament_client.list_formats()

    assert isinstance(response, TournamentFormatsListResponse)
    assert len(response.qualifying_formats) == 1
    assert len(response.finals_formats) == 1


# AsyncTournamentContext tests


@pytest.mark.asyncio
async def test_tournament_context_details(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context details() method (deprecated)."""
    tournament_data = {
        "tournament_id": 12345,
        "tournament_name": "PAPA World Championship",
        "event_date": "2024-01-15",
        "city": "Carnegie",
        "state": "PA",
        "country_code": "US",
        "country_name": "United States",
        "venue": "ReplayFX",
        "director_name": "Josh Sharpe",
        "player_count": 200,
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345").mock(
        return_value=Response(200, json=tournament_data)
    )

    context = async_tournament_client(12345)
    tournament = await context.details()

    assert isinstance(tournament, Tournament)
    assert tournament.tournament_id == 12345


@pytest.mark.asyncio
async def test_tournament_context_results(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context results() method."""
    results_data = {
        "results": [
            {
                "player_id": 12345,
                "player_name": "John Doe",
                "position": 1,
                "wppr_points": 100.0,
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345/results").mock(
        return_value=Response(200, json=results_data)
    )

    context = async_tournament_client(12345)
    response = await context.results()

    assert len(response.results) == 1
    assert response.results[0].player_name == "John Doe"


@pytest.mark.asyncio
async def test_tournament_context_formats(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context formats() method."""
    formats_data = {"formats": [{"format_id": 1, "format_name": "Swiss", "rounds": 5}]}

    respx_mock.get("https://api.ifpapinball.com/tournament/12345/formats").mock(
        return_value=Response(200, json=formats_data)
    )

    context = async_tournament_client(12345)
    response = await context.formats()

    assert len(response.formats) == 1
    assert response.formats[0].format_name == "Swiss"


@pytest.mark.asyncio
async def test_tournament_context_league_success(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context league() method for league tournament."""
    league_data = {
        "total_sessions": 10,
        "sessions": [{"session_date": "2024-01-15", "player_count": 20}],
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345/league").mock(
        return_value=Response(200, json=league_data)
    )

    context = async_tournament_client(12345)
    response = await context.league()

    assert response.total_sessions == 10
    assert len(response.sessions) == 1


@pytest.mark.asyncio
async def test_tournament_context_league_not_league(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context league() raises TournamentNotLeagueError for non-league tournament."""
    respx_mock.get("https://api.ifpapinball.com/tournament/12345/league").mock(
        return_value=Response(404, json={"error": "Not a league"})
    )

    context = async_tournament_client(12345)

    with pytest.raises(TournamentNotLeagueError):
        await context.league()


@pytest.mark.asyncio
async def test_tournament_context_submissions(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context submissions() method."""
    submissions_data = {
        "submissions": [{"submission_id": 1, "submission_date": "2024-01-20", "status": "approved"}]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345/submissions").mock(
        return_value=Response(200, json=submissions_data)
    )

    context = async_tournament_client(12345)
    response = await context.submissions()

    assert len(response.submissions) == 1
    assert response.submissions[0].status == "approved"


@pytest.mark.asyncio
async def test_tournament_context_related(
    async_tournament_client: AsyncTournamentClient, respx_mock: Any
) -> None:
    """Test context related() method."""
    related_data = {
        "tournament": [
            {
                "tournament_id": 12346,
                "tournament_name": "PAPA 2023",
                "event_name": "PAPA 2023",
                "event_start_date": "2023-01-15",
                "event_end_date": "2023-01-17",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/12345/related").mock(
        return_value=Response(200, json=related_data)
    )

    context = async_tournament_client(12345)
    response = await context.related()

    assert len(response.tournament) == 1
    assert response.tournament[0].tournament_name == "PAPA 2023"


# AsyncTournamentQueryBuilder tests


@pytest.mark.asyncio
async def test_tournament_query_builder_query(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder query() method."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.query("PAPA")

    assert new_builder is not builder  # immutability
    assert new_builder._params["name"] == "PAPA"


@pytest.mark.asyncio
async def test_tournament_query_builder_date_range(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder date_range() filter."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.date_range("2024-01-01", "2024-12-31")

    assert new_builder is not builder
    assert new_builder._params["start_date"] == "2024-01-01"
    assert new_builder._params["end_date"] == "2024-12-31"


@pytest.mark.asyncio
async def test_tournament_query_builder_date_range_requires_both(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test date_range() raises ValueError if only one date provided."""
    builder = AsyncTournamentQueryBuilder(async_http_client)

    with pytest.raises(ValueError, match="Both start_date and end_date must be provided"):
        builder.date_range("2024-01-01", None)

    with pytest.raises(ValueError, match="Both start_date and end_date must be provided"):
        builder.date_range(None, "2024-12-31")


@pytest.mark.asyncio
async def test_tournament_query_builder_date_range_validates_format(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test date_range() validates date format."""
    builder = AsyncTournamentQueryBuilder(async_http_client)

    with pytest.raises(IfpaClientValidationError, match="YYYY-MM-DD format"):
        builder.date_range("2024/01/01", "2024-12-31")

    with pytest.raises(IfpaClientValidationError, match="YYYY-MM-DD format"):
        builder.date_range("2024-01-01", "12-31-2024")


@pytest.mark.asyncio
async def test_tournament_query_builder_tournament_type(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder tournament_type() filter."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.tournament_type("women")

    assert new_builder is not builder
    assert new_builder._params["tournament_type"] == "women"


@pytest.mark.asyncio
async def test_tournament_query_builder_country(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder country() filter."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.country("US")

    assert new_builder is not builder
    assert new_builder._params["country"] == "US"


@pytest.mark.asyncio
async def test_tournament_query_builder_state(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder state() filter."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.state("PA")

    assert new_builder is not builder
    assert new_builder._params["stateprov"] == "PA"


@pytest.mark.asyncio
async def test_tournament_query_builder_city(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder city() filter."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.city("Carnegie")

    assert new_builder is not builder
    assert new_builder._params["city"] == "Carnegie"


@pytest.mark.asyncio
async def test_tournament_query_builder_limit(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder limit() pagination."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.limit(25)

    assert new_builder is not builder
    assert new_builder._params["count"] == 25


@pytest.mark.asyncio
async def test_tournament_query_builder_offset(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test query builder offset() pagination."""
    builder = AsyncTournamentQueryBuilder(async_http_client)
    new_builder = builder.offset(50)

    assert new_builder is not builder
    assert new_builder._params["start_pos"] == 51  # 0-based to 1-based conversion


@pytest.mark.asyncio
async def test_tournament_query_builder_get(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder get() execution."""
    search_data = {
        "tournaments": [
            {
                "tournament_id": 12345,
                "tournament_name": "PAPA World Championship",
                "event_date": "2024-01-15",
                "city": "Carnegie",
                "state": "PA",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)
    results = await builder.query("PAPA").get()

    assert isinstance(results, TournamentSearchResponse)
    assert len(results.tournaments) == 1
    assert results.tournaments[0].tournament_name == "PAPA World Championship"


@pytest.mark.asyncio
async def test_tournament_query_builder_get_validates_date_range(
    async_http_client: _AsyncHttpClient,
) -> None:
    """Test get() validates that both dates are present or both absent."""
    builder = AsyncTournamentQueryBuilder(async_http_client)

    # Manually set only one date to test validation
    builder._params["start_date"] = "2024-01-01"

    with pytest.raises(
        IfpaClientValidationError, match="start_date and end_date must be provided together"
    ):
        await builder.get()


@pytest.mark.asyncio
async def test_tournament_query_builder_first(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first() method."""
    search_data = {
        "tournaments": [
            {
                "tournament_id": 12345,
                "tournament_name": "PAPA World Championship",
                "event_date": "2024-01-15",
                "city": "Carnegie",
                "state": "PA",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)
    tournament = await builder.query("PAPA").first()

    assert tournament.tournament_name == "PAPA World Championship"


@pytest.mark.asyncio
async def test_tournament_query_builder_first_no_results(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first() with no results raises IndexError."""
    search_data: dict[str, Any] = {"tournaments": []}

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)

    with pytest.raises(IndexError, match="Search returned no results"):
        await builder.query("NonExistent").first()


@pytest.mark.asyncio
async def test_tournament_query_builder_first_or_none(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() method."""
    search_data = {
        "tournaments": [
            {
                "tournament_id": 12345,
                "tournament_name": "PAPA World Championship",
                "event_date": "2024-01-15",
                "city": "Carnegie",
                "state": "PA",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)
    tournament = await builder.query("PAPA").first_or_none()

    assert tournament is not None
    assert tournament.tournament_name == "PAPA World Championship"


@pytest.mark.asyncio
async def test_tournament_query_builder_first_or_none_no_results(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder first_or_none() with no results returns None."""
    search_data: dict[str, Any] = {"tournaments": []}

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)
    tournament = await builder.query("NonExistent").first_or_none()

    assert tournament is None


@pytest.mark.asyncio
async def test_tournament_query_builder_chaining(
    async_http_client: _AsyncHttpClient, respx_mock: Any
) -> None:
    """Test query builder method chaining."""
    search_data = {
        "tournaments": [
            {
                "tournament_id": 12345,
                "tournament_name": "PAPA World Championship",
                "event_date": "2024-01-15",
                "city": "Carnegie",
                "state": "PA",
                "country_code": "US",
            }
        ]
    }

    respx_mock.get("https://api.ifpapinball.com/tournament/search").mock(
        return_value=Response(200, json=search_data)
    )

    builder = AsyncTournamentQueryBuilder(async_http_client)
    results = await (
        builder.query("PAPA")
        .country("US")
        .state("PA")
        .date_range("2024-01-01", "2024-12-31")
        .limit(10)
        .get()
    )

    assert isinstance(results, TournamentSearchResponse)
    assert len(results.tournaments) == 1
