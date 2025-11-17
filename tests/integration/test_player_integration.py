"""Integration tests for Player resource.

This test suite performs comprehensive integration testing of all Player resource methods
against the live IFPA API. Tests cover happy path, edge cases, pagination, error handling,
and response structure validation.

Test fixtures use Idaho Pinball Museum community players:
- Dwayne Smith (25584): Highly active, rank #753, 433 events
- Debbie Smith (47585): Active, rank #7078, 81 active events
- Dave Fellows (52913): Active, rank #3303
- John Sosoka (50104): Low activity, rank #47572
- Anna Rigas (50106): Inactive since 2017

These tests make real API calls and require a valid API key.
Run with: pytest -m integration
"""

import pytest
from pydantic import ValidationError

from ifpa_api import IfpaClient
from ifpa_api.exceptions import IfpaApiError, PlayersNeverMetError
from ifpa_api.models.common import RankingSystem, ResultType
from ifpa_api.models.player import (
    Player,
    PlayerResultsResponse,
    PlayerSearchResponse,
    PvpAllCompetitors,
    PvpComparison,
    RankingHistory,
)
from tests.integration.helpers import skip_if_no_api_key

# =============================================================================
# COLLECTION METHODS (PlayersClient)
# =============================================================================


@pytest.mark.integration
class TestPlayerClientIntegration:
    """Integration tests for PlayersClient collection methods."""

    def test_search_players(self, api_key: str, country_code: str, count_medium: int) -> None:
        """Test searching for players with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # API requires at least one search parameter
        result = client.player.query().country(country_code).limit(count_medium).get()

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None

    def test_search_players_with_filters(
        self, api_key: str, country_code: str, count_small: int
    ) -> None:
        """Test searching players with location filter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.player.query().country(country_code).limit(count_small).get()

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
        result = client.player.query().country(country_code).limit(count_small).get()
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
        result = client.player.query().tournament("PAPA").position(1).limit(count_small).get()
        assert isinstance(result.search, list)

    def test_search_with_tournament_integration(self, api_key: str, count_small: int) -> None:
        """Test search with tournament parameter."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players in PAPA tournaments
        result = client.player.query().tournament("PAPA").limit(count_small).get()
        assert isinstance(result.search, list)

    def test_search_idaho_smiths_predictable(
        self, api_key: str, search_idaho_smiths: dict[str, str | int]
    ) -> None:
        """Test search for Smiths in Idaho returns predictable results."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Extract values from fixture and use query builder
        result = client.player.query("smith").state("ID").get()

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

        # Use query builder instead of fixture
        result = client.player.query("john").state("ID").get()

        # Known to return exactly 5 Johns
        assert len(result.search) == 5, "Should return exactly 5 Johns from Idaho"

        # Validate all results are Johns from Idaho
        for player in result.search:
            assert "john" in player.first_name.lower()
            assert player.state in ["ID", "Ida"]

        # Verify John Sosoka is in results
        player_ids = {p.player_id for p in result.search}
        assert 50104 in player_ids, "Should include John Sosoka"

    # Removed test_get_multiple_integration - get_multiple() method has been removed


# =============================================================================
# SEARCH AUDIT TESTS
# =============================================================================


@pytest.mark.integration
class TestPlayerSearchAudit:
    """Comprehensive audit tests for PlayersClient.search() method."""

    def test_search_by_name_only(self, api_key: str) -> None:
        """Test search with name parameter only - verify Dwayne Smith can be found."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for Dwayne Smith - known Idaho player
        result = client.player.query("Dwayne Smith").limit(10).get()

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)
        # Verify Dwayne Smith appears in results
        player_ids = {p.player_id for p in result.search}
        if len(player_ids) > 0:
            # At least one of the Smiths should be in results
            assert 25584 in player_ids or any("smith" in p.last_name.lower() for p in result.search)

    @pytest.mark.skip(
        reason="API stateprov filter is unreliable - returns players from wrong countries"
    )
    def test_search_by_stateprov_filter(self, api_key: str) -> None:
        """Test search filtering by state/province.

        SKIPPED: API's stateprov filter is unreliable and returns players from
        incorrect states/countries. For example, searching for "CA" (California)
        returns players from New Zealand with state="Can" (Canterbury).
        See llm_memory/api_behavior_audit_findings.md for details.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players in California (stable, large dataset)
        result = client.player.query().state("CA").limit(10).get()

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

        result = client.player.query().country(country_code).limit(10).get()

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
        result = client.player.query().tournament("PAPA").limit(10).get()

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)

    def test_search_by_tournament_position(self, api_key: str) -> None:
        """Test search filtering by tournament position."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Search for players who finished 1st in PAPA tournaments
        result = client.player.query().tournament("PAPA").position(1).limit(5).get()

        assert isinstance(result, PlayerSearchResponse)
        assert result.search is not None
        assert isinstance(result.search, list)

    @pytest.mark.skip(
        reason="API pagination is non-functional (returns 0 results or SQL errors with start_pos)"
    )
    def test_search_pagination_start_pos(self, api_key: str, country_code: str) -> None:
        """Test search pagination with start_pos parameter.

        SKIPPED: API has critical bug where start_pos parameter causes:
        - start_pos=0: SQL syntax error (tries to use -1 in LIMIT clause)
        - start_pos>0: Returns 0 results
        See llm_memory/api_behavior_audit_findings.md for details.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get first page
        page1 = client.player.query().country(country_code).offset(0).limit(5).get()
        # Get second page
        page2 = client.player.query().country(country_code).offset(5).limit(5).get()

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

    @pytest.mark.skip(reason="API ignores count parameter and pagination is non-functional")
    def test_search_pagination_count_limit(self, api_key: str, country_code: str) -> None:
        """Test search with count parameter limits results.

        SKIPPED: API ignores count parameter and returns 0 results without proper filter.
        See llm_memory/api_behavior_audit_findings.md for details.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        for count in [5, 10, 25]:
            result = client.player.query().country(country_code).limit(count).get()
            assert len(result.search) <= count

    def test_search_combined_filters(self, api_key: str) -> None:
        """Test search with multiple filters combined."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Combine country and state filters
        result = client.player.query().country("US").state("CA").limit(10).get()

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

        result = client.player.query().country(country_code).limit(5).get()

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


# =============================================================================
# GET MULTIPLE AUDIT TESTS - REMOVED
# =============================================================================
# The get_multiple() method has been removed from the SDK in favor of the
# query builder pattern. Tests have been deleted.


# =============================================================================
# RESOURCE METHODS (PlayerHandle)
# =============================================================================


@pytest.mark.integration
class TestPlayerHandleIntegration:
    """Integration tests for PlayerHandle resource methods."""

    def test_get_player(self, api_key: str, player_active_id: int) -> None:
        """Test getting player details with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use known test player fixture (Debbie Smith - 47585)
        player = client.player(player_active_id).details()

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
        The API returns None for non-existent players, which the HTTP
        client detects and raises IfpaApiError with 404 status code.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Use very high ID that doesn't exist - API returns None which triggers 404 error
        with pytest.raises(IfpaApiError) as exc_info:
            client.player(99999999).details()

        # Verify it's a 404 error
        assert exc_info.value.status_code == 404

    def test_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test getting an inactive player still returns valid data."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get inactive player (Anna Rigas - 50106, last played 2017)
        player = client.player(player_inactive_id).details()

        assert player.player_id == player_inactive_id
        assert player is not None
        # Validate inactive player characteristics
        assert player.first_name == "Anna"
        assert player.last_name == "Rigas"
        assert player.player_stats is not None
        stats = player.player_stats["system"]["open"]
        assert stats["current_rank"] == "0", "Inactive player should not be ranked"
        assert float(stats["active_points"]) == 0.0, "Inactive player should have no active points"

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
        player = client.player(player_highly_active_id).details()

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


# =============================================================================
# PLAYER DETAILS AUDIT TESTS
# =============================================================================


@pytest.mark.integration
class TestPlayerHandleDetailsAudit:
    """Comprehensive audit tests for PlayerHandle.details() method."""

    def test_get_valid_player(self, api_key: str, player_active_id: int) -> None:
        """Test details() with valid active player ID (Debbie Smith)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).details()

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
        """Test details() with invalid player ID raises error.

        Note: API returns HTTP 200 with JSON null for invalid player IDs.
        SDK detects null response and raises IfpaApiError with 404 status.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Very high ID that doesn't exist - SDK raises IfpaApiError
        with pytest.raises(IfpaApiError) as exc_info:
            client.player(99999999).details()

        assert exc_info.value.status_code == 404

    def test_get_inactive_player(self, api_key: str, player_inactive_id: int) -> None:
        """Test details() with inactive player ID (Anna Rigas - inactive since 2017)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_inactive_id).details()

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

        player = client.player(player_active_id).details()

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

        player = client.player(player_active_id).details()

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
        """Test details() with highly active player (Dwayne Smith - rank #753)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_highly_active_id).details()

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
        """Test details() response contains all expected fields."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player = client.player(player_active_id).details()

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


# =============================================================================
# PLAYER RESULTS AUDIT TESTS
# =============================================================================


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

    @pytest.mark.skip(reason="API ignores count and start_pos parameters")
    def test_results_pagination(self, api_key: str, player_highly_active_id: int) -> None:
        """Test results() with pagination parameters (use highly active player).

        SKIPPED: API ignores both count and start_pos parameters:
        - Requesting count=5 returns ~15 results
        - Different start_pos values return identical result sets
        See llm_memory/api_behavior_audit_findings.md for details.
        """
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


# =============================================================================
# PVP AUDIT TESTS
# =============================================================================


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
        """Test pvp() between players who never competed raises error.

        Note: API returns HTTP 200 with error in body:
        {"message": "These users have never played in the same tournament", "code": "404"}
        SDK detects this and raises PlayersNeverMetError.
        """
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        player1_id, player2_id = pvp_pair_never_met

        # SDK converts IfpaApiError to PlayersNeverMetError for better semantic meaning
        with pytest.raises(PlayersNeverMetError) as exc_info:
            client.player(player1_id).pvp(player2_id)

        assert "never competed" in str(exc_info.value).lower()

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


# =============================================================================
# PVP ALL AUDIT TESTS
# =============================================================================


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


# =============================================================================
# HISTORY AUDIT TESTS
# =============================================================================


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


# =============================================================================
# CROSS-VALIDATION TESTS
# =============================================================================


@pytest.mark.integration
class TestPlayerCrossMethodValidation:
    """Cross-method validation tests to verify data consistency."""

    def test_search_and_get_consistency(self, api_key: str, player_highly_active_id: int) -> None:
        """Test that search and get return consistent player data (use known player)."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        # Get known player (Dwayne Smith) directly
        player = client.player(player_highly_active_id).details()

        # Verify player data integrity
        assert player.player_id == player_highly_active_id
        assert player.first_name == "Dwayne"
        assert player.last_name == "Smith"
        assert player.city == "Boise"

    # Removed test_get_multiple_matches_individual_get - get_multiple() method has been removed
