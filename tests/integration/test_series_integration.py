"""Integration tests for SeriesClient and SeriesHandle.

These tests make real API calls to the IFPA API and require a valid API key.
Run with: pytest -m integration
"""

import pytest

from ifpa_sdk.client import IfpaClient
from ifpa_sdk.models.series import SeriesListResponse
from tests.integration.helpers import get_test_series_code, skip_if_no_api_key


@pytest.mark.integration
class TestSeriesClientIntegration:
    """Integration tests for SeriesClient."""

    def test_list_series(self, api_key: str) -> None:
        """Test listing series with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list()

        assert isinstance(result, SeriesListResponse)
        assert result.series is not None

    def test_list_active_series(self, api_key: str) -> None:
        """Test listing only active series with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        result = client.series.list(active_only=True)

        assert isinstance(result, SeriesListResponse)
        assert result.series is not None
        # If series exist, verify structure
        if len(result.series) > 0:
            first_series = result.series[0]
            assert first_series.series_code is not None
            assert first_series.series_name is not None


@pytest.mark.integration
class TestSeriesHandleIntegration:
    """Integration tests for SeriesHandle."""

    def test_series_standings(self, api_key: str) -> None:
        """Test getting series standings with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        standings = client.series_handle(series_code).standings(count=10)

        assert standings.series_code == series_code
        assert standings.standings is not None

    def test_series_overview(self, api_key: str) -> None:
        """Test getting series overview with real API."""
        skip_if_no_api_key()
        client = IfpaClient(api_key=api_key)

        series_code = get_test_series_code(client)
        assert series_code is not None, "Could not find test series"

        overview = client.series_handle(series_code).overview()

        assert overview.series_code == series_code
        assert overview.series_name is not None
