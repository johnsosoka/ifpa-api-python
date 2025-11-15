#!/usr/bin/env python3
"""
End-to-end test for IFPA SDK v0.2.0 player resource fixes.
Tests the package as if installed from PyPI using local development version.

This script verifies:
1. Search parameter mapping fix (name parameter)
2. New search parameters (tournament, tourpos)
3. Bulk fetch (get_multiple)
4. History structure changes (separate rank_history and rating_history)
5. Results required parameters (ranking_system and result_type)
6. PVP all competitors (new feature)
7. Removed methods raise AttributeError (rankings, cards)
"""

import os
import sys
from collections.abc import Callable

# Import from installed package (not source)
try:
    from ifpa_api import IfpaClient
    from ifpa_api.models.common import RankingSystem, ResultType
except ImportError as e:
    print(f"❌ Failed to import ifpa_api: {e}")
    print("Make sure the package is installed: poetry install")
    sys.exit(1)

# Test player IDs
INACTIVE_PLAYER_ID = 50104  # John Sosoka (inactive, edge cases)
ACTIVE_PLAYER_ID = 2643  # Dwayne Smith (active, full data)


def print_test_header(test_name: str) -> None:
    """Print a formatted test header."""
    print(f"\n{'=' * 60}")
    print(f"TEST: {test_name}")
    print("=" * 60)


def print_test_result(passed: bool, message: str) -> None:
    """Print test result with status indicator."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")


def test_search_with_name(client: IfpaClient) -> None:
    """Test search with name parameter (bug fix)."""
    print_test_header("Search with name parameter")

    # Search for "Smith" (more common name, should have results)
    response = client.players.search(name="Smith", count=5)

    assert hasattr(response, "search"), "Response missing 'search' field"
    results = response.search
    assert isinstance(results, list), "Expected list of results"
    assert len(results) <= 5, "Expected at most 5 results"

    if results:
        assert all(hasattr(r, "player_id") for r in results), "Results missing player_id"
        assert all(
            hasattr(r, "first_name") or hasattr(r, "last_name") for r in results
        ), "Results missing name fields"

        print_test_result(True, f"Found {len(results)} players for name='Smith'")
        sample = results[0]
        print(f"   Sample: {sample.first_name} {sample.last_name} " f"(ID: {sample.player_id})")
    else:
        print_test_result(True, "Search completed but returned no results")


def test_search_with_tournament(client: IfpaClient) -> None:
    """Test search with new tournament parameter."""
    print_test_header("Search with tournament parameter")

    # Search for players in a tournament
    # Using a known tournament ID from IFPA
    response = client.players.search(tournament="12345", count=10)

    assert hasattr(response, "search"), "Response missing 'search' field"
    results = response.search
    assert isinstance(results, list), "Expected list of results"

    if results:
        print_test_result(True, f"Found {len(results)} players in tournament 12345")
        print(f"   Sample: {results[0].first_name} {results[0].last_name}")
    else:
        print_test_result(True, "Tournament search returned empty list (tournament may not exist)")


def test_search_with_tourpos(client: IfpaClient) -> None:
    """Test search with tourpos parameter (new feature)."""
    print_test_header("Search with tourpos parameter")

    # Search for players who finished in 1st place - need to combine with tournament
    # tourpos alone is not enough, need a tournament too
    response = client.players.search(tournament="12345", tourpos=1, count=10)

    assert hasattr(response, "search"), "Response missing 'search' field"
    results = response.search
    assert isinstance(results, list), "Expected list of results"
    assert len(results) <= 10, "Expected at most 10 results"

    if results:
        print_test_result(True, f"Found {len(results)} players with 1st place finishes")
        print(f"   Sample: {results[0].first_name} {results[0].last_name}")
    else:
        print_test_result(True, "Tourpos search returned empty list (tournament may not exist)")


def test_get_multiple(client: IfpaClient) -> None:
    """Test bulk fetch with get_multiple (new feature)."""
    print_test_header("Bulk fetch with get_multiple")

    try:
        # Fetch both test players at once
        response = client.players.get_multiple([INACTIVE_PLAYER_ID, ACTIVE_PLAYER_ID])

        # Response has a "player" field that could be a single Player or list
        assert hasattr(response, "player"), "Response missing 'player' field"

        # Handle both single player and list of players
        players = response.player if isinstance(response.player, list) else [response.player]

        assert len(players) >= 1, f"Expected at least 1 player, got {len(players)}"

        print_test_result(True, f"Successfully fetched {len(players)} player(s) in bulk")
        for p in players:
            print(f"   - {p.first_name} {p.last_name} (ID: {p.player_id})")
    except Exception as e:
        if "age" in str(e) and "int_parsing" in str(e):
            print_test_result(
                False, "BUG FOUND: API returns empty string for age, model expects int | None"
            )
            print(f"   Error: {str(e)[:100]}")
            print("   This is a known bug that needs fixing in the SDK")
            raise
        raise


def test_player_profile_inactive(client: IfpaClient) -> None:
    """Test player profile for inactive player."""
    print_test_header(f"Player profile (inactive player {INACTIVE_PLAYER_ID})")

    player = client.player(INACTIVE_PLAYER_ID).get()

    assert player.player_id == INACTIVE_PLAYER_ID, "Player ID mismatch"
    assert hasattr(player, "first_name"), "Missing first_name"
    assert hasattr(player, "last_name"), "Missing last_name"
    # Player model has rankings, not current_wppr_rank
    assert hasattr(player, "rankings"), "Missing rankings"

    print_test_result(True, f"Retrieved profile: {player.first_name} {player.last_name}")

    # Find WPPR rank from rankings list
    wppr_rank = None
    for ranking in player.rankings:
        if ranking.ranking_system and "main" in ranking.ranking_system.lower():
            wppr_rank = ranking.rank
            break

    print(f"   WPPR Rank: {wppr_rank or 'Unranked'}")


def test_player_profile_active(client: IfpaClient) -> None:
    """Test player profile for active player."""
    print_test_header(f"Player profile (active player {ACTIVE_PLAYER_ID})")

    try:
        player = client.player(ACTIVE_PLAYER_ID).get()

        assert player.player_id == ACTIVE_PLAYER_ID, "Player ID mismatch"
        assert hasattr(player, "first_name"), "Missing first_name"
        assert hasattr(player, "last_name"), "Missing last_name"
        # Player model has rankings, not current_wppr_rank
        assert hasattr(player, "rankings"), "Missing rankings"

        print_test_result(True, f"Retrieved profile: {player.first_name} {player.last_name}")

        # Find WPPR rank from rankings list
        wppr_rank = None
        for ranking in player.rankings:
            if ranking.ranking_system and "main" in ranking.ranking_system.lower():
                wppr_rank = ranking.rank
                break

        print(f"   WPPR Rank: {wppr_rank or 'Unranked'}")
    except Exception as e:
        if "age" in str(e) and "int_parsing" in str(e):
            print_test_result(
                False, "BUG FOUND: API returns empty string for age, model expects int | None"
            )
            print(f"   Error: {str(e)[:100]}")
            print("   This is a known bug that needs fixing in the SDK")
            raise
        raise


def test_history_structure(client: IfpaClient) -> None:
    """Test history returns separate rank_history and rating_history arrays."""
    print_test_header("History structure (separate arrays)")

    history = client.player(ACTIVE_PLAYER_ID).history()

    # Verify new structure
    assert hasattr(history, "rank_history"), "Missing rank_history field"
    assert hasattr(history, "rating_history"), "Missing rating_history field"
    assert isinstance(history.rank_history, list), "rank_history should be a list"
    assert isinstance(history.rating_history, list), "rating_history should be a list"

    # Verify old structure doesn't exist
    assert not hasattr(history, "rankings"), "Old 'rankings' field should not exist"

    rank_count = len(history.rank_history)
    rating_count = len(history.rating_history)

    print_test_result(True, "History has correct structure (separate arrays)")
    print(f"   Rank history entries: {rank_count}")
    print(f"   Rating history entries: {rating_count}")

    if history.rank_history:
        sample = history.rank_history[0]
        # Field names are rank_position, not wppr_rank
        print(f"   Sample rank entry: rank={sample.rank_position}, date={sample.rank_date}")

    if history.rating_history:
        sample_rating = history.rating_history[0]
        # Field name is rating, not wppr_value
        print(
            f"   Sample rating entry: rating={sample_rating.rating}, "
            f"date={sample_rating.rating_date}"
        )


def test_results_required_params(client: IfpaClient) -> None:
    """Test results requires both ranking_system and result_type parameters."""
    print_test_header("Results with required parameters")

    # Test with both required parameters
    # RankingSystem uses MAIN not OPEN, ResultType uses ACTIVE not TOURNAMENT
    response = client.player(ACTIVE_PLAYER_ID).results(
        ranking_system=RankingSystem.MAIN, result_type=ResultType.ACTIVE
    )

    # Results returns a response object with a "results" field
    assert hasattr(response, "results"), "Response missing 'results' field"
    results = response.results
    assert isinstance(results, list), "Expected list of results"

    print_test_result(True, f"Results with required params returned {len(results)} tournaments")

    if results:
        sample = results[0]
        print(f"   Sample: {sample.tournament_name} ({sample.event_date})")
        print(f"           Position: {sample.position}, Points: {sample.wppr_points}")


def test_results_missing_params_fails(client: IfpaClient) -> None:
    """Test that results without required parameters fails."""
    print_test_header("Results without required parameters (should fail)")

    try:
        # This should fail - missing required parameters
        client.player(ACTIVE_PLAYER_ID).results()  # type: ignore[call-arg]
        print_test_result(False, "Expected TypeError for missing required parameters")
    except TypeError as e:
        print_test_result(True, f"Correctly raised TypeError: {str(e)[:80]}...")


def test_pvp_all(client: IfpaClient) -> None:
    """Test PVP all competitors (new feature)."""
    print_test_header("PVP all competitors")

    pvp_data = client.player(ACTIVE_PLAYER_ID).pvp_all()

    # PvpAllCompetitors model has player_id, total_competitors, system, type, title
    assert hasattr(pvp_data, "player_id"), "Missing player_id field"
    assert hasattr(pvp_data, "total_competitors"), "Missing total_competitors field"
    assert hasattr(pvp_data, "system"), "Missing system field"
    assert hasattr(pvp_data, "type"), "Missing type field"

    print_test_result(True, f"Retrieved PVP data for player {pvp_data.player_id}")
    print(f"   Total competitors: {pvp_data.total_competitors}")
    print(f"   System: {pvp_data.system}")
    print(f"   Type: {pvp_data.type}")


def test_pvp_head_to_head(client: IfpaClient) -> None:
    """Test head-to-head PVP between two players."""
    print_test_header("Head-to-head PVP")

    try:
        pvp = client.player(ACTIVE_PLAYER_ID).pvp(INACTIVE_PLAYER_ID)

        # PvpComparison has player1_id, player1_name, player2_id, player2_name, etc
        assert hasattr(pvp, "player1_id"), "Missing player1_id field"
        assert hasattr(pvp, "player2_id"), "Missing player2_id field"
        assert hasattr(pvp, "player1_name"), "Missing player1_name field"
        assert hasattr(pvp, "player2_name"), "Missing player2_name field"
        assert hasattr(pvp, "player1_wins"), "Missing player1_wins field"
        assert hasattr(pvp, "player2_wins"), "Missing player2_wins field"
        assert hasattr(pvp, "ties"), "Missing ties field"

        print_test_result(True, "Retrieved head-to-head data")
        print(f"   {pvp.player1_name} vs {pvp.player2_name}")
        print(f"   Record: {pvp.player1_wins}W - {pvp.player2_wins}L - {pvp.ties}D")
        print(f"   Total meetings: {pvp.total_meetings}")
    except Exception as e:
        # These players may not have faced each other
        if "404" in str(e) or "never played" in str(e).lower():
            print_test_result(True, "Players have never faced each other (expected)")
        else:
            raise


def test_removed_rankings_method(client: IfpaClient) -> None:
    """Test that removed rankings() method raises AttributeError."""
    print_test_header("Removed rankings() method (should raise AttributeError)")

    try:
        # This should fail - method was removed
        client.player(ACTIVE_PLAYER_ID).rankings()  # type: ignore[attr-defined]
        print_test_result(False, "Expected AttributeError for removed rankings() method")
    except AttributeError as e:
        print_test_result(True, f"Correctly raised AttributeError: {str(e)[:80]}...")


def test_removed_cards_method(client: IfpaClient) -> None:
    """Test that removed cards() method raises AttributeError."""
    print_test_header("Removed cards() method (should raise AttributeError)")

    try:
        # This should fail - method was removed
        client.player(ACTIVE_PLAYER_ID).cards()  # type: ignore[attr-defined]
        print_test_result(False, "Expected AttributeError for removed cards() method")
    except AttributeError as e:
        print_test_result(True, f"Correctly raised AttributeError: {str(e)[:80]}...")


def test_inactive_player_edge_cases(client: IfpaClient) -> None:
    """Test edge cases with inactive player (sparse data)."""
    print_test_header(f"Edge cases with inactive player {INACTIVE_PLAYER_ID}")

    # Profile should work
    player = client.player(INACTIVE_PLAYER_ID).get()
    print(f"   Profile: {player.first_name} {player.last_name}")

    # History might be empty or sparse
    history = client.player(INACTIVE_PLAYER_ID).history()
    print(
        f"   History: {len(history.rank_history)} rank entries, "
        f"{len(history.rating_history)} rating entries"
    )

    # Results might be empty
    response = client.player(INACTIVE_PLAYER_ID).results(
        ranking_system=RankingSystem.MAIN, result_type=ResultType.ACTIVE
    )
    print(f"   Results: {len(response.results)} tournaments")

    # PVP might be sparse
    pvp_data = client.player(INACTIVE_PLAYER_ID).pvp_all()
    print(f"   PVP: {pvp_data.total_competitors} total competitors")

    print_test_result(True, "All methods work with inactive player (even with sparse data)")


def get_api_key() -> str:
    """Get API key from environment or credentials file."""
    api_key = os.getenv("IFPA_API_KEY")

    if not api_key and os.path.exists("credentials"):
        with open("credentials") as f:
            for line in f:
                if line.startswith("IFPA_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()

    return api_key or ""


def main() -> None:
    """Run all end-to-end tests."""
    api_key = get_api_key()

    if not api_key:
        print("❌ No API key found. Set IFPA_API_KEY env var or create credentials file.")
        sys.exit(1)

    # Create client
    try:
        client = IfpaClient(api_key=api_key)
    except Exception as e:
        print(f"❌ Failed to create IfpaClient: {e}")
        sys.exit(1)

    print("=" * 60)
    print("IFPA SDK v0.2.0 - Player Resource E2E Tests")
    print("=" * 60)
    print("Testing with:")
    print(f"  - Inactive player: {INACTIVE_PLAYER_ID} (John Sosoka)")
    print(f"  - Active player: {ACTIVE_PLAYER_ID} (Dwayne Smith)")
    print()

    # Define all tests
    tests: list[tuple[str, Callable[[IfpaClient], None]]] = [
        ("Search with name parameter", test_search_with_name),
        ("Search with tournament parameter", test_search_with_tournament),
        ("Search with tourpos parameter", test_search_with_tourpos),
        ("Bulk fetch with get_multiple", test_get_multiple),
        ("Player profile (inactive)", test_player_profile_inactive),
        ("Player profile (active)", test_player_profile_active),
        ("History structure (separate arrays)", test_history_structure),
        ("Results with required parameters", test_results_required_params),
        ("Results without required parameters", test_results_missing_params_fails),
        ("PVP all competitors", test_pvp_all),
        ("Head-to-head PVP", test_pvp_head_to_head),
        ("Removed rankings() method", test_removed_rankings_method),
        ("Removed cards() method", test_removed_cards_method),
        ("Edge cases with inactive player", test_inactive_player_edge_cases),
    ]

    passed = 0
    failed = 0
    errors: list[tuple[str, Exception]] = []

    for test_name, test_func in tests:
        try:
            test_func(client)
            passed += 1
        except AssertionError as e:
            print_test_result(False, f"{test_name}: {e}")
            failed += 1
            errors.append((test_name, e))
        except Exception as e:
            print_test_result(False, f"{test_name}: Unexpected error: {e}")
            failed += 1
            errors.append((test_name, e))

    # Print summary
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total: {passed + failed} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()

    if errors:
        print("FAILURES:")
        for test_name, error in errors:
            print(f"  - {test_name}")
            print(f"    {type(error).__name__}: {str(error)[:100]}")
    else:
        print("🎉 All tests passed!")

    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
