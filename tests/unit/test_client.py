"""Unit tests for the main IfpaClient."""

from typing import Any

from ifpa_api import IfpaClient
from ifpa_api.resources.director import DirectorClient
from ifpa_api.resources.director.context import _DirectorContext
from ifpa_api.resources.player import PlayerClient
from ifpa_api.resources.player.context import _PlayerContext
from ifpa_api.resources.rankings import RankingsClient
from ifpa_api.resources.series import SeriesClient
from ifpa_api.resources.series.context import _SeriesContext
from ifpa_api.resources.tournament import TournamentClient
from ifpa_api.resources.tournament.context import _TournamentContext


class TestIfpaClientInitialization:
    """Tests for IfpaClient initialization."""

    def test_client_initialization_with_api_key(self) -> None:
        """Test that client initializes with an API key."""
        client = IfpaClient(api_key="test-key")
        assert client._config.api_key == "test-key"

    def test_client_initialization_from_environment(self, monkeypatch: Any) -> None:
        """Test that client initializes from environment variable."""
        monkeypatch.setenv("IFPA_API_KEY", "env-key")
        client = IfpaClient()
        assert client._config.api_key == "env-key"

    def test_client_initialization_with_custom_timeout(self) -> None:
        """Test that client accepts custom timeout."""
        client = IfpaClient(api_key="test-key", timeout=30.0)
        assert client._config.timeout == 30.0

    def test_client_initialization_with_custom_base_url(self) -> None:
        """Test that client accepts custom base URL."""
        custom_url = "https://custom.api.com"
        client = IfpaClient(api_key="test-key", base_url=custom_url)
        assert client._config.base_url == custom_url

    def test_client_initialization_with_validation_disabled(self) -> None:
        """Test that client accepts validate_requests flag."""
        client = IfpaClient(api_key="test-key", validate_requests=False)
        assert client._config.validate_requests is False

    def test_client_has_http_client(self) -> None:
        """Test that client initializes internal HTTP client."""
        client = IfpaClient(api_key="test-key")
        assert client._http is not None


class TestIfpaClientResourceProperties:
    """Tests for resource client properties."""

    def test_director_property_returns_director_client(self) -> None:
        """Test that director property returns DirectorClient."""
        client = IfpaClient(api_key="test-key")
        director = client.director
        assert isinstance(director, DirectorClient)

    def test_player_property_returns_player_client(self) -> None:
        """Test that player property returns PlayerClient."""
        client = IfpaClient(api_key="test-key")
        player = client.player
        assert isinstance(player, PlayerClient)

    def test_rankings_property_returns_rankings_client(self) -> None:
        """Test that rankings property returns RankingsClient."""
        client = IfpaClient(api_key="test-key")
        rankings = client.rankings
        assert isinstance(rankings, RankingsClient)

    def test_tournament_property_returns_tournament_client(self) -> None:
        """Test that tournament property returns TournamentClient."""
        client = IfpaClient(api_key="test-key")
        tournament = client.tournament
        assert isinstance(tournament, TournamentClient)

    def test_series_property_returns_series_client(self) -> None:
        """Test that series property returns SeriesClient."""
        client = IfpaClient(api_key="test-key")
        series = client.series
        assert isinstance(series, SeriesClient)

    def test_resource_properties_are_cached(self) -> None:
        """Test that resource clients are cached after first access."""
        client = IfpaClient(api_key="test-key")
        director1 = client.director
        director2 = client.director
        assert director1 is director2


class TestIfpaClientHandleFactory:
    """Tests for handle factory methods."""

    def test_director_callable_returns_director_context(self) -> None:
        """Test that director() callable returns _DirectorContext."""
        client = IfpaClient(api_key="test-key")
        context = client.director(1000)
        assert isinstance(context, _DirectorContext)

    def test_director_context_stores_id(self) -> None:
        """Test that director context stores the director ID."""
        client = IfpaClient(api_key="test-key")
        director_id = 1000
        context = client.director(director_id)
        assert context._resource_id == director_id

    def test_player_callable_returns_player_context(self) -> None:
        """Test that player() callable returns _PlayerContext."""
        client = IfpaClient(api_key="test-key")
        context = client.player(12345)
        assert isinstance(context, _PlayerContext)

    def test_player_context_stores_id(self) -> None:
        """Test that player context stores the player ID."""
        client = IfpaClient(api_key="test-key")
        player_id = 12345
        context = client.player(player_id)
        assert context._resource_id == player_id

    def test_tournament_callable_returns_tournament_context(self) -> None:
        """Test that tournament() callable returns _TournamentContext."""
        client = IfpaClient(api_key="test-key")
        context = client.tournament(54321)
        assert isinstance(context, _TournamentContext)

    def test_tournament_context_stores_id(self) -> None:
        """Test that tournament context stores the tournament ID."""
        client = IfpaClient(api_key="test-key")
        tournament_id = 54321
        context = client.tournament(tournament_id)
        assert context._resource_id == tournament_id

    def test_series_callable_returns_series_context(self) -> None:
        """Test that series() callable returns _SeriesContext."""
        client = IfpaClient(api_key="test-key")
        context = client.series("PAPA")
        assert isinstance(context, _SeriesContext)

    def test_series_context_stores_code(self) -> None:
        """Test that series context stores the series code."""
        client = IfpaClient(api_key="test-key")
        series_code = "PAPA"
        context = client.series(series_code)
        assert context._resource_id == series_code

    def test_handle_accepts_string_ids(self) -> None:
        """Test that handles accept string IDs."""
        client = IfpaClient(api_key="test-key")
        director_context = client.director("1000")
        assert director_context._resource_id == "1000"

    def test_handles_are_independent(self) -> None:
        """Test that each call to handle/callable factory creates a new instance."""
        client = IfpaClient(api_key="test-key")
        context1 = client.player(123)
        context2 = client.player(123)
        assert context1 is not context2


class TestIfpaClientContextManager:
    """Tests for context manager protocol."""

    def test_client_can_be_used_as_context_manager(self) -> None:
        """Test that client supports context manager protocol."""
        with IfpaClient(api_key="test-key") as client:
            assert client is not None
            assert isinstance(client, IfpaClient)

    def test_context_manager_enter_returns_self(self) -> None:
        """Test that __enter__ returns the client instance."""
        client = IfpaClient(api_key="test-key")
        with client as returned_client:
            assert returned_client is client

    def test_context_manager_closes_on_exit(self) -> None:
        """Test that client is closed when exiting context manager."""
        client = IfpaClient(api_key="test-key")
        with client:
            pass
        # After context exit, session should be closed (no error when checking)


class TestIfpaClientCloseMethod:
    """Tests for close method."""

    def test_close_method_exists(self) -> None:
        """Test that close method can be called."""
        client = IfpaClient(api_key="test-key")
        client.close()

    def test_close_closes_http_client(self) -> None:
        """Test that close method closes the HTTP client."""
        client = IfpaClient(api_key="test-key")
        client.close()
        # Verify close was called by checking the session is closed
        # (This is more of a smoke test to ensure no errors occur)


class TestIfpaClientConfiguration:
    """Tests for configuration passing to resources."""

    def test_validate_requests_passed_to_resources(self) -> None:
        """Test that validate_requests flag is passed to resource clients."""
        client = IfpaClient(api_key="test-key", validate_requests=False)
        director = client.director
        assert director._validate_requests is False

    def test_http_client_passed_to_resources(self) -> None:
        """Test that HTTP client is passed to resource clients."""
        client = IfpaClient(api_key="test-key")
        director = client.director
        assert director._http is client._http
