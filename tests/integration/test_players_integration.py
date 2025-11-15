"""Integration tests for PlayersClient and PlayerHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration

Updated to use Idaho Pinball Museum community players as test fixtures:
- Dwayne Smith (25584): Highly active, rank #753
- Debbie Smith (47585): Active, rank #7078
- Dave Fellows (52913): Active, rank #3303
- John Sosoka (50104): Low activity, rank #47572
- Anna Rigas (50106): Inactive since 2017
"""

from typing import cast

import pytest
from pydantic import ValidationError

from ifpa_api.client import IfpaClient
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import PlayerSearchResponse
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestPlayersClientIntegration:
    """Integration tests for PlayersClient."""

    def test_search_players(self, api_key: str, country_code: str, count_medium: int) -> None:
        """Test searching for players with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # API requires at least one search parameter
        result = client.players.search(country=country_code, count=count_medium)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None

    def test_search_players_with_filters(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test searching players with location filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(country=country_code, count=count_small)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        # If results exist, verify they match filter
        if len(result.search) > 0:
            for player in result.search:
                if player.country_code:
                    assert player.country_code == country_code

    def test_search_with_multiple_filters(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test search with multiple filter combinations."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test country + count combination
        result = client.players.search(country=country_code, count=count_small)
        assert isinstance(result.search, list)
        # Note: API may not always respect count parameter for broad searches like country-only
        # Just verify we got results
        assert len(result.search) > 0, "Should return some results"

    def test_search_with_tournament_and_position(self, api_key: str, count_small: int) -> None:
        """Test search filtering by tournament and position.

        Searches for top finishers (position 1) in PAPA tournaments.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players with top finishes in PAPA tournaments
        result = client.players.search(tournament="PAPA", tourpos=1, count=count_small)
        assert isinstance(result.search, list)


@pytest.mark.integration
class TestPlayerHandleIntegration:
    """Integration tests for PlayerHandle."""

    def test_get_player(self, api_key: str, player_active_id: int) -> None:
        """Test getting player details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)
        from ifpa_api.models.player import Player

        # Use known test player fixture (Debbie Smith - 47585)
        player = client.player(player_active_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_active_id
        # Validate actual player characteristics
        assert player.first_name == "Debbie"
        assert player.last_name == "Smith"
        assert player.city == "Boise"
        assert player.stateprov == "ID"

    def test_player_results(self, api_key: str, player_active_id: int, count_small: int) -> None:
        """Test getting player tournament results with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use known test player fixture (Debbie Smith - 47585, has 81 active events)
        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            count=count_small,
        )

        assert results.player_id == player_active_id
        assert results.results is not None
        assert len(results.results) > 0, "Active player should have tournament results"

    def test_player_history(self, api_key: str, player_active_id: int) -> None:
        """Test getting player ranking history with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use known test player fixture (active, with history data)
        history = client.player(player_active_id).history()

        assert history.player_id == player_active_id
        assert hasattr(history, "rank_history")
        assert hasattr(history, "rating_history")
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)

    def test_pvp_all_integration(self, api_key: str, player_active_id: int) -> None:
        """Test pvp_all with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with known active player (Debbie Smith - 47585, has 92 PVP competitors)
        summary = client.player(player_active_id).pvp_all()
        assert summary.player_id == player_active_id
        assert isinstance(summary.total_competitors, int)
        assert summary.total_competitors > 80, "Active player should have many PVP competitors"
        assert summary.system is not None

    def test_get_multiple_integration(self, api_key: str, player_ids_multiple: list[int]) -> None:
        """Test get_multiple with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with multiple test players (25584 highly active, 50104 low activity, 50106 inactive)
        result = client.players.get_multiple(cast(list[int | str], player_ids_multiple))
        assert result.player is not None
        # Verify we got a list of players
        if isinstance(result.player, list):
            assert len(result.player) == len(player_ids_multiple)
            assert all(p.player_id in player_ids_multiple for p in result.player)

            # Validate mixed activity levels
            players_by_id = {p.player_id: p for p in result.player}
            # Dwayne (25584) - highly active, should be top 1000
            if 25584 in players_by_id:
                dwayne = players_by_id[25584]
                assert dwayne.player_stats is not None
                dwayne_rank = int(dwayne.player_stats["system"]["open"]["current_rank"])
                assert dwayne_rank < 1000, "Highly active player should be ranked in top 1000"
            # Anna (50106) - inactive, should not be ranked
            if 50106 in players_by_id:
                anna = players_by_id[50106]
                assert anna.player_stats is not None
                anna_rank = anna.player_stats["system"]["open"]["current_rank"]
                assert anna_rank == "0", "Inactive player should not be ranked"

    def test_search_with_tournament_integration(self, api_key: str, count_small: int) -> None:
        """Test search with tournament parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players in PAPA tournaments
        result = client.players.search(tournament="PAPA", count=count_small)
        assert isinstance(result.search, list)

    def test_history_structure_integration(self, api_key: str, player_active_id: int) -> None:
        """Test history returns correct structure with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Test with player fixture (has history data)
        history = client.player(player_active_id).history()

        # Verify dual-array structure
        assert hasattr(history, "rank_history")
        assert hasattr(history, "rating_history")
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)
        assert history.system is not None
        assert history.active_flag in ["Y", "N"]

    def test_get_player_not_found(self, api_key: str) -> None:
        """Test that getting non-existent player raises appropriate error.

        Uses a very high player ID that is extremely unlikely to exist.
        The API returns None for non-existent players, which Pydantic
        validates as an error.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist - API returns None which fails validation
        with pytest.raises(ValidationError):
            client.player(99999999).get()

    def test_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test getting an inactive player still returns valid data."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get inactive player (Anna Rigas - 50106, last played 2017)
        player = client.player(player_inactive_id).get()

        assert player.player_id == player_inactive_id
        assert player is not None
        # Validate inactive player characteristics
        assert player.first_name == "Anna"
        assert player.last_name == "Rigas"
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert stats["current_rank"] == "0", "Inactive player should not be ranked"
        assert float(stats["active_points"]) == 0.0, "Inactive player should have no active points"

    def test_search_idaho_smiths_predictable(
        self, api_key: str, search_idaho_smiths: dict[str, str | int]
    ) -> None:
        """Test search for Smiths in Idaho returns predictable results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(**search_idaho_smiths)  # type: ignore[arg-type]

        # Predictable count (at least 2, currently 3 including Aviana Smith)
        assert len(result.search) >= 2, "Should return at least 2 Smiths from Idaho"

        # Verify expected core players present
        player_ids = {p.player_id for p in result.search}
        assert 25584 in player_ids, "Should include Dwayne Smith"
        assert 47585 in player_ids, "Should include Debbie Smith"

        # Validate all results match search criteria
        for player in result.search:
            assert "smith" in player.last_name.lower()
            assert player.state == "ID"

    def test_search_idaho_johns_count(
        self, api_key: str, search_idaho_johns: dict[str, str | int]
    ) -> None:
        """Test search for Johns in Idaho returns exactly 5 results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(**search_idaho_johns)  # type: ignore[arg-type]

        # Known to return exactly 5 Johns
        assert len(result.search) == 5, "Should return exactly 5 Johns from Idaho"

        # Validate all results are Johns from Idaho
        for player in result.search:
            assert "john" in player.first_name.lower()
            assert player.state in ["ID", "Ida"]

        # Verify John Sosoka is in results
        player_ids = {p.player_id for p in result.search}
        assert 50104 in player_ids, "Should include John Sosoka"

    def test_pvp_confirmed_history(self, api_key: str, pvp_pair_primary: tuple[int, int]) -> None:
        """Test PVP between players with extensive tournament history."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Dwayne vs Debbie (205 tournaments together)
        player1_id, player2_id = pvp_pair_primary

        comparison = client.player(player1_id).pvp(player2_id)

        # Validate PVP comparison
        assert comparison.player1_id == player1_id
        assert comparison.player2_id == player2_id
        assert comparison.player1_name == "Dwayne Smith"
        assert comparison.player2_name == "Debbie Smith"
        # API returns tournaments list, should have extensive history
        assert len(comparison.tournaments) >= 200, "Should have extensive tournament history"

    def test_pvp_players_never_met(self, api_key: str, player_highly_active_id: int) -> None:
        """Test PVP between players who never competed raises proper error."""
        skip_if_no_api_key()
        from ifpa_api.exceptions import PlayersNeverMetError

        client = IfpaClient(api_key=api_key)

        # Use very high player ID that doesn't exist (guaranteed never met)
        fake_player_id = 99999

        with pytest.raises(PlayersNeverMetError) as exc_info:
            client.player(player_highly_active_id).pvp(fake_player_id)

        assert exc_info.value.player_id == player_highly_active_id
        assert exc_info.value.opponent_id == fake_player_id

    def test_highly_active_player_characteristics(
        self, api_key: str, player_highly_active_id: int
    ) -> None:
        """Test highly active player has expected characteristics."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Dwayne Smith - rank #753, 433 events
        player = client.player(player_highly_active_id).get()

        # Validate identity
        assert player.player_id == player_highly_active_id
        assert player.first_name == "Dwayne"
        assert player.last_name == "Smith"
        assert player.city == "Boise"
        assert player.stateprov == "ID"

        # Validate activity metrics
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert int(stats["current_rank"]) < 1000, "Should be top 1000 ranked"
        assert float(stats["active_points"]) > 100, "Should have substantial active points"
        assert int(stats["total_active_events"]) > 200, "Should have many active events"
        assert int(stats["total_events_all_time"]) > 400, "Should have extensive history"

    def test_pvp_all_highly_active(self, api_key: str, player_highly_active_id: int) -> None:
        """Test pvp_all for highly active player returns many competitors."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Dwayne Smith - 375 competitors
        pvp = client.player(player_highly_active_id).pvp_all()

        assert pvp.player_id == player_highly_active_id
        assert pvp.total_competitors > 300, "Highly active player should have many competitors"
        assert pvp.system == "MAIN"
        assert pvp.type == "all"

    def test_pvp_all_inactive_zero_competitors(self, api_key: str, player_inactive_id: int) -> None:
        """Test pvp_all for inactive player returns zero competitors."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Anna Rigas - 0 competitors (inactive since 2017)
        pvp = client.player(player_inactive_id).pvp_all()

        assert pvp.player_id == player_inactive_id
        assert pvp.total_competitors == 0, "Inactive player should have no competitors"
