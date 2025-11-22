"""Unit tests for Phase 2 naming standardization.

Tests the new .search() methods and collection naming methods,
verifying both functionality and deprecation warnings.
"""

import warnings

import requests_mock

from ifpa_api.client import IfpaClient


class TestPlayerSearchNaming:
    """Test player search naming standardization."""

    def test_search_method_works(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .search() method works correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"results": [{"player_id": 12345, "first_name": "John", "last_name": "Smith"}]},
        )

        client = IfpaClient(api_key="test-key")
        results = client.player.search("John").get()

        assert len(results.search) == 1
        assert results.search[0].player_id == 12345

    def test_query_method_issues_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .query() method issues DeprecationWarning."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={"results": [{"player_id": 12345, "first_name": "John", "last_name": "Smith"}]},
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            results = client.player.query("John").get()

            # Check that warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert ".search()" in str(w[0].message)
            assert "v5.0.0" in str(w[0].message)

        # Verify functionality is identical
        assert len(results.search) == 1
        assert results.search[0].player_id == 12345

    def test_search_and_query_produce_identical_results(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .search() and .query() produce identical results."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search",
            json={
                "results": [
                    {"player_id": 1, "first_name": "John", "last_name": "Smith"},
                    {"player_id": 2, "first_name": "Jane", "last_name": "Smith"},
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        # Use .search() (new way)
        results_search = client.player.search("Smith").country("US").get()

        # Use .query() (old way, suppress warning)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            results_query = client.player.query("Smith").country("US").get()

        # Results should be identical
        assert len(results_search.search) == len(results_query.search)
        assert results_search.search[0].player_id == results_query.search[0].player_id


class TestDirectorSearchNaming:
    """Test director search naming standardization."""

    def test_search_method_works(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .search() method works correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [{"director_id": 1533, "name": "Josh Sharpe"}]},
        )

        client = IfpaClient(api_key="test-key")
        results = client.director.search("Josh").get()

        assert len(results.directors) == 1
        assert results.directors[0].director_id == 1533

    def test_query_method_issues_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .query() method issues DeprecationWarning."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/search",
            json={"directors": [{"director_id": 1533, "name": "Josh Sharpe"}]},
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            results = client.director.query("Josh").get()

            # Check that warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert ".search()" in str(w[0].message)

        # Verify functionality works
        assert len(results.directors) == 1


class TestTournamentSearchNaming:
    """Test tournament search naming standardization."""

    def test_search_method_works(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .search() method works correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "search": [
                    {
                        "tournament_id": 54321,
                        "tournament_name": "PAPA 2024",
                        "event_name": "PAPA World Championship",
                        "country_name": "United States",
                        "stateprov": "PA",
                        "city": "Pittsburgh",
                        "event_date": "2024-08-15",
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        results = client.tournament.search("PAPA").get()

        assert len(results.tournaments) == 1
        assert results.tournaments[0].tournament_id == 54321

    def test_query_method_issues_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .query() method issues DeprecationWarning."""
        mock_requests.get(
            "https://api.ifpapinball.com/tournament/search",
            json={
                "search": [
                    {
                        "tournament_id": 54321,
                        "tournament_name": "PAPA 2024",
                        "event_name": "PAPA World Championship",
                        "country_name": "United States",
                        "stateprov": "PA",
                        "city": "Pittsburgh",
                        "event_date": "2024-08-15",
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            results = client.tournament.query("PAPA").get()

            # Check that warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

        # Verify functionality works
        assert len(results.tournaments) == 1


class TestDirectorCollectionNaming:
    """Test director collection method naming standardization."""

    def test_list_country_directors_works(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .list_country_directors() method works correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "country_directors": [
                    {
                        "player_profile": {
                            "player_id": 1533,
                            "name": "Josh Sharpe",
                            "country_code": "US",
                            "country_name": "United States",
                            "profile_photo": "",
                        }
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        directors = client.director.list_country_directors()

        assert len(directors.country_directors) == 1
        assert directors.country_directors[0].player_profile.player_id == 1533

    def test_country_directors_issues_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .country_directors() method issues DeprecationWarning."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "country_directors": [
                    {
                        "player_profile": {
                            "player_id": 1533,
                            "name": "Josh Sharpe",
                            "country_code": "US",
                            "country_name": "United States",
                            "profile_photo": "",
                        }
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            directors = client.director.country_directors()

            # Check that warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert ".list_country_directors()" in str(w[0].message)
            assert "v5.0.0" in str(w[0].message)

        # Verify functionality is identical
        assert len(directors.country_directors) == 1

    def test_both_methods_produce_identical_results(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that old and new methods produce identical results."""
        mock_requests.get(
            "https://api.ifpapinball.com/director/country",
            json={
                "country_directors": [
                    {
                        "player_profile": {
                            "player_id": 1,
                            "name": "Josh Sharpe",
                            "country_code": "US",
                            "country_name": "United States",
                            "profile_photo": "",
                        }
                    },
                    {
                        "player_profile": {
                            "player_id": 2,
                            "name": "John Doe",
                            "country_code": "CA",
                            "country_name": "Canada",
                            "profile_photo": "",
                        }
                    },
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        # Use new method
        result_new = client.director.list_country_directors()

        # Use old method (suppress warning)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_old = client.director.country_directors()

        # Results should be identical
        assert len(result_new.country_directors) == len(result_old.country_directors)
        assert (
            result_new.country_directors[0].player_profile.player_id
            == result_old.country_directors[0].player_profile.player_id
        )


class TestSeriesCollectionNaming:
    """Test series collection method naming standardization."""

    def test_list_series_works(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .list_series() method works correctly."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "series_code": "NACS",
                        "series_name": "IFPA North American Championship Series",
                    },
                    {"series_code": "PAPA", "series_name": "PAPA Circuit"},
                ]
            },
        )

        client = IfpaClient(api_key="test-key")
        series = client.series.list_series()

        assert len(series.series) == 2
        assert series.series[0].series_code == "NACS"

    def test_list_method_issues_deprecation_warning(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that .list() method issues DeprecationWarning."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {
                        "series_code": "NACS",
                        "series_name": "IFPA North American Championship Series",
                    }
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            series = client.series.list()

            # Check that warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert ".list_series()" in str(w[0].message)
            assert "v5.0.0" in str(w[0].message)

        # Verify functionality is identical
        assert len(series.series) == 1

    def test_list_series_with_active_only_filter(self, mock_requests: requests_mock.Mocker) -> None:
        """Test that .list_series() respects active_only parameter."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list?active_only=true",
            json={"series": [{"series_code": "NACS", "series_name": "IFPA NACS"}]},
        )

        client = IfpaClient(api_key="test-key")
        series = client.series.list_series(active_only=True)

        assert len(series.series) == 1

    def test_both_methods_produce_identical_results(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that old and new methods produce identical results."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={
                "series": [
                    {"series_code": "NACS", "series_name": "NACS"},
                    {"series_code": "PAPA", "series_name": "PAPA"},
                ]
            },
        )

        client = IfpaClient(api_key="test-key")

        # Use new method
        result_new = client.series.list_series()

        # Use old method (suppress warning)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_old = client.series.list()

        # Results should be identical
        assert len(result_new.series) == len(result_old.series)
        assert result_new.series[0].series_code == result_old.series[0].series_code


class TestWarningStackLevel:
    """Test that deprecation warnings have correct stack level."""

    def test_player_query_warning_points_to_caller(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that warning points to the caller's code, not internal implementation."""
        mock_requests.get(
            "https://api.ifpapinball.com/player/search?q=John",
            json={"search": [{"player_id": 12345, "first_name": "John"}]},
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # This line should be reported in the warning
            _ = client.player.query("John")  # noqa: F841

            assert len(w) == 1
            # Stack level 2 ensures warning points to this line, not internal code
            assert w[0].filename == __file__

    def test_series_list_warning_points_to_caller(
        self, mock_requests: requests_mock.Mocker
    ) -> None:
        """Test that warning points to the caller's code."""
        mock_requests.get(
            "https://api.ifpapinball.com/series/list",
            json={"series": [{"series_code": "NACS", "series_name": "NACS"}]},
        )

        client = IfpaClient(api_key="test-key")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # This line should be reported in the warning
            _ = client.series.list()  # noqa: F841

            assert len(w) == 1
            assert w[0].filename == __file__
