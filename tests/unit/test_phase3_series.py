"""Unit tests for Phase 3: Series QueryBuilder implementation.

Tests the SeriesQueryBuilder, .search() method, and deprecation warnings
for the Series resource modernization.
"""

import warnings

import pytest
import requests_mock

from ifpa_api.client import IfpaClient
from ifpa_api.models.series import SeriesListResponse
from ifpa_api.resources.series.query_builder import SeriesQueryBuilder


class TestSeriesQueryBuilder:
    """Test cases for SeriesQueryBuilder fluent API."""

    def test_simple_search_without_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test simple search without name filter returns all series."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "code": "NACS",
                        "title": "North American Circuit Series",
                        "description": "Premier circuit series",
                        "active": True,
                    },
                    {
                        "code": "PAPA",
                        "title": "Professional & Amateur Pinball Association",
                        "description": "Classic series",
                        "active": True,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search().get()

        assert isinstance(results, SeriesListResponse)
        assert len(results.series) == 2
        assert results.series[0].series_code == "NACS"
        assert results.series[1].series_code == "PAPA"

    def test_search_with_name_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test search with name filter performs client-side filtering."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "code": "NACS",
                        "title": "North American Circuit Series",
                        "active": True,
                    },
                    {
                        "code": "PAPA",
                        "title": "Professional & Amateur Pinball Association",
                        "active": True,
                    },
                    {
                        "code": "CIRCUIT",
                        "title": "European Circuit",
                        "active": True,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("Circuit").get()

        # Should filter to only series with "Circuit" in name
        assert isinstance(results, SeriesListResponse)
        assert len(results.series) == 2
        assert results.series[0].series_code == "NACS"
        assert results.series[1].series_code == "CIRCUIT"

    def test_search_by_series_code(self, mock_requests: requests_mock.Mocker) -> None:
        """Test name filter matches series codes as well as names."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit Series", "active": True},
                    {"code": "PAPA", "title": "Professional Pinball", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("NACS").get()

        assert len(results.series) == 1
        assert results.series[0].series_code == "NACS"

    def test_search_case_insensitive(self, mock_requests: requests_mock.Mocker) -> None:
        """Test name filtering is case-insensitive."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit Series", "active": True},
                    {"code": "PAPA", "title": "Professional Pinball", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")

        # Test different cases
        results_lower = client.series.search("circuit").get()
        results_upper = client.series.search("CIRCUIT").get()
        results_mixed = client.series.search("Circuit").get()

        assert len(results_lower.series) == 1
        assert len(results_upper.series) == 1
        assert len(results_mixed.series) == 1
        assert results_lower.series[0].series_code == "NACS"

    def test_active_only_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test active_only filter is sent to API."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list?active_only=true",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search().active_only().get()

        assert len(results.series) == 1
        assert results.series[0].active is True

        # Verify the correct parameter was sent
        assert mock_requests.last_request is not None
        assert "active_only=true" in mock_requests.last_request.query

    def test_active_only_false(self, mock_requests: requests_mock.Mocker) -> None:
        """Test active_only(False) returns inactive series."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list?active_only=false",
            json={
                "series": [
                    {"code": "OLD", "title": "Old Series", "active": False},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search().active_only(False).get()

        assert len(results.series) == 1
        assert "active_only=false" in mock_requests.last_request.query

    def test_combined_filters(self, mock_requests: requests_mock.Mocker) -> None:
        """Test combining name and active_only filters."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list?active_only=true",
            json={
                "series": [
                    {
                        "code": "NACS",
                        "title": "North American Circuit Series",
                        "active": True,
                    },
                    {
                        "code": "CIRCUIT",
                        "title": "European Circuit",
                        "active": True,
                    },
                    {
                        "code": "PAPA",
                        "title": "Professional Pinball",
                        "active": True,
                    },
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("Circuit").active_only().get()

        # Active filter sent to API, name filter applied client-side
        assert len(results.series) == 2
        assert results.series[0].series_code == "NACS"
        assert results.series[1].series_code == "CIRCUIT"

    def test_query_immutability(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that query builder is immutable and can be reused."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list?active_only=true",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "CIRCUIT", "title": "European Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        base_query = client.series.search().active_only()

        # Create two different queries from the same base
        circuit_results = base_query.name("Circuit").get()
        papa_results = base_query.name("PAPA").get()

        # Verify both work correctly and base wasn't mutated
        assert len(circuit_results.series) == 2
        assert len(papa_results.series) == 1
        assert papa_results.series[0].series_code == "PAPA"

    def test_name_parameter_overwrite_raises_error(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that calling name() multiple times raises ValueError."""
        client = IfpaClient(api_key="test-key")

        with pytest.raises(ValueError, match="name\\(\\) called multiple times"):
            client.series.search("Circuit").name("PAPA")

    def test_active_only_parameter_overwrite_raises_error(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that calling active_only() multiple times raises ValueError."""
        client = IfpaClient(api_key="test-key")

        with pytest.raises(ValueError, match="active_only\\(\\) called multiple times"):
            client.series.search().active_only(True).active_only(False)

    def test_first_method(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first() returns first result."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        first_series = client.series.search().first()

        assert first_series.series_code == "NACS"

    def test_first_or_none_with_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first_or_none() returns first result when results exist."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        first_series = client.series.search().first_or_none()

        assert first_series is not None
        assert first_series.series_code == "NACS"

    def test_first_or_none_without_results(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first_or_none() returns None when no results."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={"series": []},
        )

        client = IfpaClient(api_key="test-key")
        first_series = client.series.search("NonExistent").first_or_none()

        assert first_series is None

    def test_first_raises_error_on_empty(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .first() raises ValueError when no results."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={"series": []},
        )

        client = IfpaClient(api_key="test-key")

        with pytest.raises(ValueError, match="No results found"):
            client.series.search("NonExistent").first()

    def test_iterate_method(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .iterate() yields individual series items."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                    {"code": "CIRCUIT", "title": "European Circuit", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        series_list = list(client.series.search().iterate())

        assert len(series_list) == 3
        assert series_list[0].series_code == "NACS"
        assert series_list[1].series_code == "PAPA"
        assert series_list[2].series_code == "CIRCUIT"

    def test_get_all_method(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .get_all() collects all results into a list."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        all_series = client.series.search().get_all()

        assert len(all_series) == 2
        assert all_series[0].series_code == "NACS"

    def test_search_with_initial_name(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .search(name) as shorthand for .search().name(name)."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("NACS").get()

        assert len(results.series) == 1
        assert results.series[0].series_code == "NACS"

    def test_empty_name_filter_returns_all(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that empty string name filter doesn't filter anything."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                    {"code": "PAPA", "title": "PAPA Series", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("").get()

        # Empty string should match everything (substring of everything)
        assert len(results.series) == 2


class TestSeriesClientSearchMethod:
    """Test cases for SeriesClient.search() method."""

    def test_search_returns_query_builder(self, mock_requests: requests_mock.Mocker) -> None:
        """Test .search() returns a SeriesQueryBuilder instance."""
        client = IfpaClient(api_key="test-key")
        builder = client.series.search()

        assert isinstance(builder, SeriesQueryBuilder)

    def test_search_with_name_returns_configured_builder(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test .search(name) returns pre-configured builder."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"code": "NACS", "title": "North American Circuit", "active": True},
                ],
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.series.search("NACS").get()

        assert len(results.series) == 1
        assert results.series[0].series_code == "NACS"


class TestSeriesContextDeprecationWarnings:
    """Test cases for deprecation warnings on Series context methods."""

    def test_standings_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test standings() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/overall_standings",
            json={
                "series_code": "NACS",
                "year": 2025,
                "championship_prize_fund": 10000.0,
                "overall_results": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").standings()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "client.series(code).standings() is deprecated" in str(w[0].message)
            assert "client.series.get(code)" in str(w[0].message)

    def test_region_standings_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test region_standings() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/standings?region_code=OH",
            json={
                "series_code": "NACS",
                "region_code": "OH",
                "region_name": "Ohio",
                "prize_fund": "5000",
                "year": 2025,
                "standings": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").region_standings("OH")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "region_standings() is deprecated" in str(w[0].message)

    def test_player_card_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test player_card() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/player_card/12345?region_code=OH",
            json={
                "player_id": 12345,
                "player_name": "John Smith",
                "player_card": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").player_card(12345, "OH")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "player_card() is deprecated" in str(w[0].message)

    def test_regions_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test regions() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/regions?region_code=OH&year=2025",
            json={
                "series_code": "NACS",
                "year": 2025,
                "active_regions": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").regions("OH", 2025)

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "regions() is deprecated" in str(w[0].message)

    def test_stats_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test stats() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/stats?region_code=OH",
            json={
                "series_code": "NACS",
                "total_events": 50,
                "statistics": {},
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").stats("OH")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "stats() is deprecated" in str(w[0].message)

    def test_tournaments_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test tournaments() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/tournaments?region_code=OH",
            json={
                "series_code": "NACS",
                "region_code": "OH",
                "tournaments": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").tournaments("OH")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "tournaments() is deprecated" in str(w[0].message)

    def test_region_reps_deprecation_warning(self, mock_requests: requests_mock.Mocker) -> None:
        """Test region_reps() issues deprecation warning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/region_reps",
            json={
                "series_code": "NACS",
                "representative": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.series("NACS").region_reps()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "region_reps() is deprecated" in str(w[0].message)

    def test_deprecation_warning_stack_level(self, mock_requests: requests_mock.Mocker) -> None:
        """Test deprecation warnings point to caller's code."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/NACS/overall_standings",
            json={
                "series_code": "NACS",
                "year": 2025,
                "championship_prize_fund": 10000.0,
                "overall_results": [],
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # This line should be identified as the source
            client.series("NACS").standings()

            assert len(w) == 1
            # stacklevel=2 should point to this test function, not the context method
            assert w[0].lineno > 0
