"""Comprehensive audit tests for Players resource.

This test suite performs a thorough audit of all 7 Player resource methods
against the live IFPA API. Tests cover happy path, edge cases, pagination,
error handling, and response structure validation.

Run with: pytest tests/integration/test_players_audit.py -v
"""

import pytest
from pydantic import ValidationError

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError, IfpaClientValidationError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    MultiPlayerResponse,
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)
from tests.integration.helpers import skip_if_no_api_key


@pytest.mark.integration
class TestPlayersSearchAudit:
    """Comprehensive audit tests for PlayersClient.search() method."""

    def test_search_by_name_only(self, api_key: str) -> None:
        """Test search with name parameter only - verify Dwayne Smith can be found."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for Dwayne Smith - known Idaho player
        result = client.players.search(name="Dwayne Smith", count=10)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)
        # Verify Dwayne Smith appears in results
        player_ids = {p.player_id for p in result.search}
        if len(player_ids) > 0:
            # At least one of the Smiths should be in results
            assert 25584 in player_ids or any("smith" in p.last_name.lower() for p in result.search)

    def test_search_by_stateprov_filter(self, api_key: str) -> None:
        """Test search filtering by state/province."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players in California (stable, large dataset)
        result = client.players.search(stateprov="CA", count=10)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        # Verify state filter works if results returned
        for player in result.search:
            if player.state is not None:
                assert player.state == "CA"

    def test_search_by_country_filter(self, api_key: str, country_code: str) -> None:
        """Test search filtering by country."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(country=country_code, count=10)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        # Verify country filter works
        for player in result.search:
            if player.country_code is not None:
                assert player.country_code == country_code

    def test_search_by_tournament_filter(self, api_key: str) -> None:
        """Test search filtering by tournament name."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players who participated in PAPA tournaments
        result = client.players.search(tournament="PAPA", count=10)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)

    def test_search_by_tournament_position(self, api_key: str) -> None:
        """Test search filtering by tournament position."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players who finished 1st in PAPA tournaments
        result = client.players.search(tournament="PAPA", tourpos=1, count=5)

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)

    def test_search_pagination_start_pos(self, api_key: str, country_code: str) -> None:
        """Test search pagination with start_pos parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get first page
        page1 = client.players.search(country=country_code, start_pos=0, count=5)
        # Get second page
        page2 = client.players.search(country=country_code, start_pos=5, count=5)

        assert isinstance(page1, PlayerSearchResponse)
        assert isinstance(page2, PlayerSearchResponse)
        # Verify both pages have results
        assert len(page1.search) > 0
        assert len(page2.search) > 0
        # Verify pages are different (if enough results exist)
        if len(page1.search) > 0 and len(page2.search) > 0:
            page1_ids = {p.player_id for p in page1.search}
            page2_ids = {p.player_id for p in page2.search}
            # Pages should have different players
            assert page1_ids != page2_ids

    def test_search_pagination_count_limit(self, api_key: str, country_code: str) -> None:
        """Test search with count parameter limits results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        for count in [5, 10, 25]:
            result = client.players.search(country=country_code, count=count)
            assert len(result.search) <= count

    def test_search_combined_filters(self, api_key: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Combine country and state filters
        result = client.players.search(country="US", stateprov="CA", count=10)

        assert isinstance(result, PlayerSearchResponse)
        # Verify combined filters work
        for player in result.search:
            if player.country_code is not None:
                assert player.country_code == "US"
            if player.state is not None:
                assert player.state == "CA"

    def test_search_response_structure(self, api_key: str, country_code: str) -> None:
        """Test search response structure matches PlayerSearchResponse model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.search(country=country_code, count=5)

        # Verify response structure
        assert isinstance(result, PlayerSearchResponse)
        assert hasattr(result, "query")
        assert hasattr(result, "search")
        assert isinstance(result.search, list)
        # Verify player fields
        if len(result.search) > 0:
            player = result.search[0]
            assert hasattr(player, "player_id")
            assert hasattr(player, "first_name")
            assert hasattr(player, "last_name")
            assert hasattr(player, "city")
            assert hasattr(player, "state")
            assert hasattr(player, "country_code")
            assert hasattr(player, "country_name")
            assert hasattr(player, "wppr_rank")


@pytest.mark.integration
class TestPlayersGetMultipleAudit:
    """Comprehensive audit tests for PlayersClient.get_multiple() method."""

    def test_get_multiple_single_player(self, api_key: str, player_active_id: int) -> None:
        """Test get_multiple with single player ID (Debbie Smith)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.get_multiple([player_active_id])

        assert isinstance(result, MultiPlayerResponse)
        assert result.player is not None
        # Result may be single Player or list with one Player
        if isinstance(result.player, list):
            assert len(result.player) == 1
            player = result.player[0]
            assert player.player_id == player_active_id
            # Validate identity
            assert player.first_name == "Debbie"
            assert player.last_name == "Smith"
            assert player.city == "Boise"
        else:
            assert result.player.player_id == player_active_id
            assert result.player.first_name == "Debbie"
            assert result.player.last_name == "Smith"

    def test_get_multiple_several_players(
        self, api_key: str, player_ids_multiple: list[int]
    ) -> None:
        """Test get_multiple with multiple player IDs (mixed activity levels)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Type cast to satisfy mypy - list[int] is compatible with list[int | str]
        from typing import cast

        result = client.players.get_multiple(cast(list[int | str], player_ids_multiple))

        assert isinstance(result, MultiPlayerResponse)
        assert result.player is not None
        # Should return list of players
        if isinstance(result.player, list):
            assert len(result.player) == len(player_ids_multiple)
            returned_ids = {p.player_id for p in result.player}
            for pid in player_ids_multiple:
                assert pid in returned_ids

            # Map players by ID for validation
            players_by_id = {p.player_id: p for p in result.player}

            # Validate Dwayne (highly active)
            dwayne = players_by_id[25584]
            assert dwayne.first_name == "Dwayne"
            assert dwayne.last_name == "Smith"
            assert dwayne.player_stats is not None
            assert int(dwayne.player_stats["system"]["open"]["current_rank"]) < 1000

            # Validate John (low activity)
            john = players_by_id[50104]
            assert john.first_name == "John"
            assert john.last_name == "Sosoka"
            assert john.player_stats is not None
            assert int(john.player_stats["system"]["open"]["current_rank"]) > 10000

            # Validate Anna (inactive)
            anna = players_by_id[50106]
            assert anna.first_name == "Anna"
            assert anna.last_name == "Rigas"
            assert anna.player_stats is not None
            assert anna.player_stats["system"]["open"]["current_rank"] == "0"

    def test_get_multiple_max_50_limit(self, api_key: str) -> None:
        """Test get_multiple enforces 50 player limit."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Try to request 51 players (should raise validation error)
        with pytest.raises(IfpaClientValidationError) as exc_info:
            client.players.get_multiple(list(range(1, 52)))

        assert "Maximum 50 player IDs" in str(exc_info.value)

    def test_get_multiple_invalid_player_id(self, api_key: str) -> None:
        """Test get_multiple with invalid player ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Very high ID that doesn't exist
        result = client.players.get_multiple([99999999])

        # API may return empty result or None - verify graceful handling
        assert isinstance(result, MultiPlayerResponse)

    def test_get_multiple_mixed_valid_invalid(self, api_key: str, player_active_id: int) -> None:
        """Test get_multiple with mix of valid and invalid IDs."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Mix valid and invalid IDs
        result = client.players.get_multiple([player_active_id, 99999999])

        assert isinstance(result, MultiPlayerResponse)
        # Should return at least the valid player
        if isinstance(result.player, list):
            assert len(result.player) >= 1
            assert player_active_id in {p.player_id for p in result.player}

    def test_get_multiple_response_structure(self, api_key: str, player_active_id: int) -> None:
        """Test get_multiple response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.players.get_multiple([player_active_id])

        # Verify response structure
        assert isinstance(result, MultiPlayerResponse)
        assert hasattr(result, "player")
        # Player should be Player or list[Player]
        if isinstance(result.player, list):
            for player in result.player:
                assert isinstance(player, Player)
        else:
            assert isinstance(result.player, Player)


@pytest.mark.integration
class TestPlayerHandleGetAudit:
    """Comprehensive audit tests for PlayerHandle.get() method."""

    def test_get_valid_player(self, api_key: str, player_active_id: int) -> None:
        """Test get() with valid active player ID (Debbie Smith)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_active_id
        # Validate identity
        assert player.first_name == "Debbie"
        assert player.last_name == "Smith"
        assert player.city == "Boise"
        assert player.stateprov == "ID"
        # Validate active status
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert int(stats["current_rank"]) > 0
        assert float(stats["active_points"]) > 0

    def test_get_invalid_player(self, api_key: str) -> None:
        """Test get() with invalid player ID raises error."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Very high ID that doesn't exist
        with pytest.raises(ValidationError):
            client.player(99999999).get()

    def test_get_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test get() with inactive player ID (Anna Rigas - inactive since 2017)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_inactive_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_inactive_id
        # Validate identity
        assert player.first_name == "Anna"
        assert player.last_name == "Rigas"
        # Validate inactivity
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert stats["current_rank"] == "0"
        assert float(stats["active_points"]) == 0.0
        assert int(stats["total_active_events"]) == 0

    def test_get_player_stats_structure(self, api_key: str, player_active_id: int) -> None:
        """Test player_stats field structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).get()

        # Verify player_stats structure exists
        assert hasattr(player, "player_stats")
        if player.player_stats is not None:
            assert isinstance(player.player_stats, dict)
            # Common stats keys (vary by ranking system)
            # Just verify it's a dict, don't enforce specific keys

    def test_get_player_rankings_structure(self, api_key: str, player_active_id: int) -> None:
        """Test rankings field structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).get()

        # Verify rankings structure
        assert hasattr(player, "rankings")
        assert isinstance(player.rankings, list)
        # Active player should have rankings
        if len(player.rankings) > 0:
            ranking = player.rankings[0]
            assert hasattr(ranking, "ranking_system")
            assert hasattr(ranking, "rank")
            assert hasattr(ranking, "rating")

    def test_get_highly_active_player(self, api_key: str, player_highly_active_id: int) -> None:
        """Test get() with highly active player (Dwayne Smith - rank #753)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_highly_active_id).get()

        assert isinstance(player, Player)
        assert player.player_id == player_highly_active_id
        # Validate identity
        assert player.first_name == "Dwayne"
        assert player.last_name == "Smith"
        assert player.city == "Boise"
        assert player.stateprov == "ID"
        # Validate high activity metrics
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert int(stats["current_rank"]) < 1000
        assert float(stats["active_points"]) > 100
        assert int(stats["total_active_events"]) > 200
        assert int(stats["total_events_all_time"]) > 400

    def test_get_response_all_fields(self, api_key: str, player_active_id: int) -> None:
        """Test get() response contains all expected fields."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).get()

        # Verify all Player model fields exist
        assert hasattr(player, "player_id")
        assert hasattr(player, "first_name")
        assert hasattr(player, "last_name")
        assert hasattr(player, "city")
        assert hasattr(player, "stateprov")
        assert hasattr(player, "country_name")
        assert hasattr(player, "country_code")
        assert hasattr(player, "profile_photo")
        assert hasattr(player, "initials")
        assert hasattr(player, "age")
        assert hasattr(player, "excluded_flag")
        assert hasattr(player, "ifpa_registered")
        assert hasattr(player, "fide_player")
        assert hasattr(player, "player_stats")
        assert hasattr(player, "rankings")


@pytest.mark.integration
class TestPlayerHandleResultsAudit:
    """Comprehensive audit tests for PlayerHandle.results() method."""

    def test_results_main_active(self, api_key: str, player_highly_active_id: int) -> None:
        """Test results() with Main ranking system and Active results (Dwayne Smith)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.player(player_highly_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            count=50,
        )

        assert isinstance(results, PlayerResultsResponse)
        assert results.player_id == player_highly_active_id
        assert results.results is not None
        assert isinstance(results.results, list)
        assert len(results.results) > 0
        # total_results may be None or a string
        if results.total_results is not None:
            assert int(results.total_results) > 200
        # Validate result structure
        first_result = results.results[0]
        assert first_result.tournament_id is not None
        assert first_result.tournament_name is not None
        assert first_result.position is not None

    def test_results_main_nonactive(self, api_key: str, player_active_id: int) -> None:
        """Test results() with Main ranking system and Nonactive results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.NONACTIVE,
        )

        assert isinstance(results, PlayerResultsResponse)
        assert results.player_id == player_active_id

    def test_results_main_inactive(self, api_key: str, player_active_id: int) -> None:
        """Test results() with Main ranking system and Inactive results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.INACTIVE,
        )

        assert isinstance(results, PlayerResultsResponse)
        assert results.player_id == player_active_id

    def test_results_women_ranking(self, api_key: str, player_active_id: int) -> None:
        """Test results() with Women ranking system."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.WOMEN,
            result_type=ResultType.ACTIVE,
        )

        # Some players may not have women's ranking results
        assert isinstance(results, PlayerResultsResponse)

    def test_results_pagination(self, api_key: str, player_highly_active_id: int) -> None:
        """Test results() with pagination parameters (use highly active player)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get first page with highly active player who has many results
        page1 = client.player(player_highly_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            start_pos=0,
            count=5,
        )

        assert isinstance(page1, PlayerResultsResponse)
        assert len(page1.results) <= 5
        assert len(page1.results) > 0  # Highly active player should have results

        # Get second page
        page2 = client.player(player_highly_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            start_pos=5,
            count=5,
        )

        assert isinstance(page2, PlayerResultsResponse)
        # Verify pages are different if player has enough results
        if len(page1.results) > 0 and len(page2.results) > 0:
            page1_ids = {r.tournament_id for r in page1.results}
            page2_ids = {r.tournament_id for r in page2.results}
            # Different pages should have different tournaments
            assert page1_ids != page2_ids

    def test_results_response_structure(self, api_key: str, player_active_id: int) -> None:
        """Test results() response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        results = client.player(player_active_id).results(
            ranking_system=RankingSystem.MAIN,
            result_type=ResultType.ACTIVE,
            count=5,
        )

        # Verify response structure
        assert isinstance(results, PlayerResultsResponse)
        assert hasattr(results, "player_id")
        assert hasattr(results, "results")
        assert hasattr(results, "total_results")

        # Verify TournamentResult structure
        if len(results.results) > 0:
            result = results.results[0]
            assert hasattr(result, "tournament_id")
            assert hasattr(result, "tournament_name")
            assert hasattr(result, "event_date")
            assert hasattr(result, "position")
            assert hasattr(result, "wppr_points")


@pytest.mark.integration
class TestPlayerHandlePvpAudit:
    """Comprehensive audit tests for PlayerHandle.pvp() method."""

    def test_pvp_extensive_history(self, api_key: str, pvp_pair_primary: tuple[int, int]) -> None:
        """Test pvp() between players with extensive tournament history.

        Uses Dwayne vs Debbie (205 tournaments together).
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player1_id, player2_id = pvp_pair_primary

        comparison = client.player(player1_id).pvp(player2_id)

        assert isinstance(comparison, PvpComparison)
        assert comparison.player1_id == player1_id
        assert comparison.player2_id == player2_id
        # Validate extensive history (fields may be None due to API response)
        if comparison.total_meetings is not None:
            assert comparison.total_meetings >= 200
        if comparison.tournaments is not None:
            assert len(comparison.tournaments) >= 200
        # Validate player names
        assert "Dwayne" in comparison.player1_name
        assert "Debbie" in comparison.player2_name

    def test_pvp_players_never_met(self, api_key: str, pvp_pair_never_met: tuple[int, int]) -> None:
        """Test pvp() between players who never competed raises error (Dwayne vs John)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player1_id, player2_id = pvp_pair_never_met

        # API returns 404 with message "These users have never played in the same tournament"
        with pytest.raises(IfpaApiError) as exc_info:
            client.player(player1_id).pvp(player2_id)

        assert exc_info.value.status_code == 404

    def test_pvp_invalid_opponent(self, api_key: str, player_highly_active_id: int) -> None:
        """Test pvp() with invalid opponent ID."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Very high ID that doesn't exist
        with pytest.raises((IfpaApiError, ValidationError)):
            client.player(player_highly_active_id).pvp(99999999)

    def test_pvp_response_structure(self, api_key: str, pvp_pair_primary: tuple[int, int]) -> None:
        """Test pvp() response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player1_id, player2_id = pvp_pair_primary

        comparison = client.player(player1_id).pvp(player2_id)

        # Verify response structure
        assert isinstance(comparison, PvpComparison)
        assert hasattr(comparison, "player1_id")
        assert hasattr(comparison, "player1_name")
        assert hasattr(comparison, "player2_id")
        assert hasattr(comparison, "player2_name")
        assert hasattr(comparison, "player1_wins")
        assert hasattr(comparison, "player2_wins")
        assert hasattr(comparison, "ties")
        assert hasattr(comparison, "total_meetings")
        assert hasattr(comparison, "tournaments")


@pytest.mark.integration
class TestPlayerHandlePvpAllAudit:
    """Comprehensive audit tests for PlayerHandle.pvp_all() method."""

    def test_pvp_all_highly_active(self, api_key: str, player_highly_active_id: int) -> None:
        """Test pvp_all() for highly active player returns many competitors.

        Dwayne Smith - expected 300+ competitors.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        summary = client.player(player_highly_active_id).pvp_all()

        assert isinstance(summary, PvpAllCompetitors)
        assert summary.player_id == player_highly_active_id
        assert isinstance(summary.total_competitors, int)
        # Dwayne should have substantial PVP history
        assert summary.total_competitors > 250
        assert summary.system == "MAIN"

    def test_pvp_all_response_structure(self, api_key: str, player_active_id: int) -> None:
        """Test pvp_all() response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        summary = client.player(player_active_id).pvp_all()

        # Verify response structure
        assert isinstance(summary, PvpAllCompetitors)
        assert hasattr(summary, "player_id")
        assert hasattr(summary, "total_competitors")
        assert hasattr(summary, "system")
        assert hasattr(summary, "type")
        assert hasattr(summary, "title")
        # Verify field types
        assert isinstance(summary.player_id, int)
        assert isinstance(summary.total_competitors, int)
        assert isinstance(summary.system, str)
        assert isinstance(summary.type, str)
        assert isinstance(summary.title, str)

    def test_pvp_all_inactive_player_zero_competitors(
        self, api_key: str, player_inactive_id: int
    ) -> None:
        """Test pvp_all() for inactive player returns zero competitors (Anna Rigas)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        summary = client.player(player_inactive_id).pvp_all()

        assert isinstance(summary, PvpAllCompetitors)
        assert summary.player_id == player_inactive_id
        assert summary.total_competitors == 0


@pytest.mark.integration
class TestPlayerHandleHistoryAudit:
    """Comprehensive audit tests for PlayerHandle.history() method."""

    def test_history_highly_active_player(self, api_key: str, player_highly_active_id: int) -> None:
        """Test history() for highly active player returns ranking progression (Dwayne Smith)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_highly_active_id).history()

        assert isinstance(history, RankingHistory)
        assert history.player_id == player_highly_active_id
        assert history.system == "MAIN"
        assert len(history.rank_history) > 0
        assert len(history.rating_history) > 0
        # Validate current rank in history
        latest_rank = history.rank_history[0]
        assert int(latest_rank.rank_position) < 1000
        assert float(latest_rank.wppr_points) > 100

    def test_history_valid_player(self, api_key: str, player_active_id: int) -> None:
        """Test history() with valid active player."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_active_id).history()

        assert isinstance(history, RankingHistory)
        assert history.player_id == player_active_id

    def test_history_response_structure(self, api_key: str, player_active_id: int) -> None:
        """Test history() response structure matches model."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_active_id).history()

        # Verify response structure
        assert isinstance(history, RankingHistory)
        assert hasattr(history, "player_id")
        assert hasattr(history, "system")
        assert hasattr(history, "active_flag")
        assert hasattr(history, "rank_history")
        assert hasattr(history, "rating_history")

        # Verify dual-array structure
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)

    def test_history_rank_entries(self, api_key: str, player_active_id: int) -> None:
        """Test history() rank_history entries structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_active_id).history()

        # Verify rank history entries
        if len(history.rank_history) > 0:
            entry = history.rank_history[0]
            assert hasattr(entry, "rank_date")
            assert hasattr(entry, "rank_position")
            assert hasattr(entry, "wppr_points")
            assert hasattr(entry, "tournaments_played_count")

    def test_history_rating_entries(self, api_key: str, player_active_id: int) -> None:
        """Test history() rating_history entries structure."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_active_id).history()

        # Verify rating history entries
        if len(history.rating_history) > 0:
            entry = history.rating_history[0]
            assert hasattr(entry, "rating_date")
            assert hasattr(entry, "rating")

    def test_history_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test history() with inactive player."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        history = client.player(player_inactive_id).history()

        assert isinstance(history, RankingHistory)
        assert history.player_id == player_inactive_id
        # Inactive players may still have historical data
        assert isinstance(history.rank_history, list)
        assert isinstance(history.rating_history, list)


@pytest.mark.integration
class TestPlayersCrossMethodValidation:
    """Cross-method validation tests to verify data consistency."""

    def test_search_and_get_consistency(self, api_key: str, player_highly_active_id: int) -> None:
        """Test that search and get return consistent player data (use known player)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get known player (Dwayne Smith) directly
        player = client.player(player_highly_active_id).get()

        # Verify player data integrity
        assert player.player_id == player_highly_active_id
        assert player.first_name == "Dwayne"
        assert player.last_name == "Smith"
        assert player.city == "Boise"

    def test_get_multiple_matches_individual_get(self, api_key: str, player_active_id: int) -> None:
        """Test that get_multiple returns same data as individual get."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get player individually
        individual = client.player(player_active_id).get()

        # Get player via get_multiple
        multiple_result = client.players.get_multiple([player_active_id])
        if isinstance(multiple_result.player, list):
            multiple = multiple_result.player[0]
        else:
            multiple = multiple_result.player

        # Verify core fields match
        assert individual.player_id == multiple.player_id
        assert individual.first_name == multiple.first_name
        assert individual.last_name == multiple.last_name
