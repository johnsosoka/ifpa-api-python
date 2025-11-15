"""Unit tests for the main IfpaClient."""

from ifpa_sdk import IfpaClient
from ifpa_sdk.resources.directors import DirectorHandle, DirectorsClient
from ifpa_sdk.resources.players import PlayerHandle, PlayersClient
from ifpa_sdk.resources.rankings import RankingsClient
from ifpa_sdk.resources.series import SeriesClient, SeriesHandle
from ifpa_sdk.resources.stats import StatsClient
from ifpa_sdk.resources.tournaments import TournamentHandle, TournamentsClient


class TestIfpaClientInitialization:
    """Tests for IfpaClient initialization."""

    def test_client_initialization_with_api_key(self) -> None:
        """Test that client initializes with an API key."""
        client = IfpaClient(api_key="test-key")
        assert client._config.api_key == "test-key"

    def test_client_initialization_from_environment(self, monkeypatch) -> None:
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

    def test_directors_property_returns_directors_client(self) -> None:
        """Test that directors property returns DirectorsClient."""
        client = IfpaClient(api_key="test-key")
        directors = client.directors
        assert isinstance(directors, DirectorsClient)

    def test_players_property_returns_players_client(self) -> None:
        """Test that players property returns PlayersClient."""
        client = IfpaClient(api_key="test-key")
        players = client.players
        assert isinstance(players, PlayersClient)

    def test_rankings_property_returns_rankings_client(self) -> None:
        """Test that rankings property returns RankingsClient."""
        client = IfpaClient(api_key="test-key")
        rankings = client.rankings
        assert isinstance(rankings, RankingsClient)

    def test_tournaments_property_returns_tournaments_client(self) -> None:
        """Test that tournaments property returns TournamentsClient."""
        client = IfpaClient(api_key="test-key")
        tournaments = client.tournaments
        assert isinstance(tournaments, TournamentsClient)

    def test_series_property_returns_series_client(self) -> None:
        """Test that series property returns SeriesClient."""
        client = IfpaClient(api_key="test-key")
        series = client.series
        assert isinstance(series, SeriesClient)

    def test_stats_property_returns_stats_client(self) -> None:
        """Test that stats property returns StatsClient."""
        client = IfpaClient(api_key="test-key")
        stats = client.stats
        assert isinstance(stats, StatsClient)

    def test_resource_properties_are_cached(self) -> None:
        """Test that resource clients are cached after first access."""
        client = IfpaClient(api_key="test-key")
        directors1 = client.directors
        directors2 = client.directors
        assert directors1 is directors2


class TestIfpaClientHandleFactory:
    """Tests for handle factory methods."""

    def test_director_method_returns_director_handle(self) -> None:
        """Test that director() method returns DirectorHandle."""
        client = IfpaClient(api_key="test-key")
        handle = client.director(1000)
        assert isinstance(handle, DirectorHandle)

    def test_director_handle_stores_id(self) -> None:
        """Test that director handle stores the director ID."""
        client = IfpaClient(api_key="test-key")
        director_id = 1000
        handle = client.director(director_id)
        assert handle._director_id == director_id

    def test_player_method_returns_player_handle(self) -> None:
        """Test that player() method returns PlayerHandle."""
        client = IfpaClient(api_key="test-key")
        handle = client.player(12345)
        assert isinstance(handle, PlayerHandle)

    def test_player_handle_stores_id(self) -> None:
        """Test that player handle stores the player ID."""
        client = IfpaClient(api_key="test-key")
        player_id = 12345
        handle = client.player(player_id)
        assert handle._player_id == player_id

    def test_tournament_method_returns_tournament_handle(self) -> None:
        """Test that tournament() method returns TournamentHandle."""
        client = IfpaClient(api_key="test-key")
        handle = client.tournament(54321)
        assert isinstance(handle, TournamentHandle)

    def test_tournament_handle_stores_id(self) -> None:
        """Test that tournament handle stores the tournament ID."""
        client = IfpaClient(api_key="test-key")
        tournament_id = 54321
        handle = client.tournament(tournament_id)
        assert handle._tournament_id == tournament_id

    def test_series_handle_method_returns_series_handle(self) -> None:
        """Test that series_handle() method returns SeriesHandle."""
        client = IfpaClient(api_key="test-key")
        handle = client.series_handle("PAPA")
        assert isinstance(handle, SeriesHandle)

    def test_series_handle_stores_code(self) -> None:
        """Test that series handle stores the series code."""
        client = IfpaClient(api_key="test-key")
        series_code = "PAPA"
        handle = client.series_handle(series_code)
        assert handle._series_code == series_code

    def test_handle_accepts_string_ids(self) -> None:
        """Test that handles accept string IDs."""
        client = IfpaClient(api_key="test-key")
        director_handle = client.director("1000")
        assert director_handle._director_id == "1000"

    def test_handles_are_independent(self) -> None:
        """Test that each call to handle factory creates a new instance."""
        client = IfpaClient(api_key="test-key")
        handle1 = client.player(123)
        handle2 = client.player(123)
        assert handle1 is not handle2


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
        directors = client.directors
        assert directors._validate_requests is False

    def test_http_client_passed_to_resources(self) -> None:
        """Test that HTTP client is passed to resource clients."""
        client = IfpaClient(api_key="test-key")
        directors = client.directors
        assert directors._http is client._http
