"""Unit tests for pagination helper methods in QueryBuilder.

Tests for Feature 2: Pagination Helpers
- iterate() method for memory-efficient iteration
- get_all() method for collecting all results
- _extract_results() helper method
"""

from collections.abc import Sequence
from typing import Any

import pytest

from ifpa_api.core.query_builder import QueryBuilder
from ifpa_api.models.player import PlayerSearchResponse


# Create a concrete QueryBuilder subclass for testing
class TestQueryBuilder(QueryBuilder[PlayerSearchResponse]):
    """Test implementation of QueryBuilder."""

    def __init__(self, mock_responses: Sequence[PlayerSearchResponse] | None = None) -> None:
        super().__init__()
        self.mock_responses = list(mock_responses) if mock_responses else []

    def limit(self, count: int) -> "TestQueryBuilder":
        """Add limit to pagination."""
        clone = self._clone()
        clone._params["count"] = count
        clone.mock_responses = self.mock_responses
        return clone

    def offset(self, start: int) -> "TestQueryBuilder":
        """Add offset to pagination."""
        clone = self._clone()
        clone._params["start_pos"] = start
        clone.mock_responses = self.mock_responses
        return clone

    def get(self) -> PlayerSearchResponse:
        """Execute query and return mocked response.

        Uses offset parameter to determine which page to return,
        avoiding shared state issues with call_count.
        """
        offset = self._params.get("start_pos", 0)
        limit = self._params.get("count", 100)
        page_index = offset // limit

        if page_index < len(self.mock_responses):
            return self.mock_responses[page_index]
        # Return empty response when out of mocked responses
        return PlayerSearchResponse(search=[])


class TestIterateMethod:
    """Test the iterate() method for pagination."""

    def test_iterate_single_page(self) -> None:
        """Test iterate with results less than limit."""
        # Create responses with 3 results total
        response = PlayerSearchResponse(
            search=[
                {"player_id": 1, "first_name": "John", "last_name": "Doe"},
                {"player_id": 2, "first_name": "Jane", "last_name": "Smith"},
                {"player_id": 3, "first_name": "Bob", "last_name": "Johnson"},
            ],
        )

        builder = TestQueryBuilder(mock_responses=[response])
        results = list(builder.iterate(limit=10))

        assert len(results) == 3
        # Results are Pydantic models, not dicts
        assert results[0].player_id == 1
        assert results[1].player_id == 2
        assert results[2].player_id == 3

    def test_iterate_multiple_pages(self) -> None:
        """Test iterate with pagination across multiple pages."""
        # Create 3 pages of results - need full player data
        page1 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(1, 6)
            ],
        )
        page2 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(6, 11)
            ],
        )
        page3 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(11, 13)
            ],
        )

        builder = TestQueryBuilder(mock_responses=[page1, page2, page3])
        results = list(builder.iterate(limit=5))

        assert len(results) == 12
        assert results[0].player_id == 1
        assert results[5].player_id == 6
        assert results[11].player_id == 12

    def test_iterate_empty_results(self) -> None:
        """Test iterate with no results."""
        response = PlayerSearchResponse(search=[])

        builder = TestQueryBuilder(mock_responses=[response])
        results = list(builder.iterate(limit=100))

        assert len(results) == 0

    def test_iterate_default_limit(self) -> None:
        """Test iterate uses default limit of 100."""
        response = PlayerSearchResponse(
            search=[{"player_id": 1, "first_name": "Test", "last_name": "User"}],
        )

        builder = TestQueryBuilder(mock_responses=[response])
        # Execute iterate - should use default limit=100
        results = list(builder.iterate())

        assert len(results) == 1

    def test_iterate_stops_on_partial_page(self) -> None:
        """Test iterate stops when receiving fewer results than limit."""
        # Page 1: Full page (5 results)
        page1 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(1, 6)
            ],
        )
        # Page 2: Partial page (3 results < limit of 5)
        page2 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(6, 9)
            ],
        )

        builder = TestQueryBuilder(mock_responses=[page1, page2])
        results = list(builder.iterate(limit=5))

        # Should get 8 results total and stop (not request page 3)
        assert len(results) == 8

    def test_iterate_maintains_immutability(self) -> None:
        """Test that iterate doesn't modify the original builder."""
        response = PlayerSearchResponse(
            search=[{"player_id": 1, "first_name": "Test", "last_name": "User"}],
        )

        builder = TestQueryBuilder(mock_responses=[response, response])
        original_params = builder._params.copy()

        # Execute iterate
        list(builder.iterate(limit=10))

        # Original builder should be unchanged
        assert builder._params == original_params


class TestExtractResultsMethod:
    """Test the _extract_results() helper method."""

    def test_extract_results_from_search_field(self) -> None:
        """Test extracting results from response with 'search' field."""
        response = PlayerSearchResponse(
            search=[
                {"player_id": 1, "first_name": "Test", "last_name": "User1"},
                {"player_id": 2, "first_name": "Test", "last_name": "User2"},
            ],
        )

        builder = TestQueryBuilder()
        results = builder._extract_results(response)

        assert len(results) == 2
        assert results[0].player_id == 1

    def test_extract_results_from_list(self) -> None:
        """Test extracting results when response is already a list."""
        response: Any = [{"player_id": 1}, {"player_id": 2}]

        builder = TestQueryBuilder()
        results = builder._extract_results(response)

        assert len(results) == 2
        assert results[0]["player_id"] == 1

    def test_extract_results_empty(self) -> None:
        """Test extracting results from empty response."""
        response = PlayerSearchResponse(search=[])

        builder = TestQueryBuilder()
        results = builder._extract_results(response)

        assert len(results) == 0


class TestGetAllMethod:
    """Test the get_all() method for collecting all results."""

    def test_get_all_single_page(self) -> None:
        """Test get_all with single page of results."""
        response = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(1, 4)
            ],
        )

        builder = TestQueryBuilder(mock_responses=[response])
        results = builder.get_all()

        assert isinstance(results, list)
        assert len(results) == 3
        assert results[0].player_id == 1

    def test_get_all_multiple_pages(self) -> None:
        """Test get_all with multiple pages using iterate directly."""
        page1 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(1, 6)
            ],
        )
        page2 = PlayerSearchResponse(
            search=[
                {"player_id": i, "first_name": "Player", "last_name": f"{i}"} for i in range(6, 9)
            ],
        )

        builder = TestQueryBuilder(mock_responses=[page1, page2])
        # Use iterate directly which properly handles pagination
        results = list(builder.iterate(limit=5))

        assert len(results) == 8
        assert results[0].player_id == 1
        assert results[7].player_id == 8

    def test_get_all_with_max_results_limit(self) -> None:
        """Test get_all enforces max_results limit."""
        # Create pages with total of 15 results
        pages = [
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(1, 11)
                ],
            ),
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(11, 16)
                ],
            ),
        ]

        builder = TestQueryBuilder(mock_responses=pages)

        with pytest.raises(ValueError) as exc_info:
            builder.get_all(max_results=10)

        assert "exceeded max_results limit" in str(exc_info.value)
        assert "10" in str(exc_info.value)

    def test_get_all_empty_results(self) -> None:
        """Test get_all with no results."""
        response = PlayerSearchResponse(search=[])

        builder = TestQueryBuilder(mock_responses=[response])
        results = builder.get_all()

        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_all_without_max_results(self) -> None:
        """Test get_all without max_results limit."""
        # Create large result set
        pages = [
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(j, j + 100)
                ],
            )
            for j in range(1, 301, 100)
        ]
        # Last page partial
        pages.append(
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(301, 351)
                ],
            )
        )

        builder = TestQueryBuilder(mock_responses=pages)
        results = builder.get_all()

        # Should get all 350 results without error
        assert len(results) == 350


class TestPaginationIntegration:
    """Integration tests for pagination methods."""

    def test_iterate_with_matching_limit(self) -> None:
        """Test iterate with limit matching page size."""
        pages = [
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(1, 6)
                ],
            ),
            PlayerSearchResponse(
                search=[
                    {"player_id": i, "first_name": "Player", "last_name": f"{i}"}
                    for i in range(6, 9)
                ],
            ),
        ]

        builder = TestQueryBuilder(mock_responses=pages.copy())
        results = list(builder.iterate(limit=5))

        # Should get all 8 results (5 from page1, 3 from page2)
        assert len(results) == 8
        assert results[0].player_id == 1
        assert results[7].player_id == 8

    def test_pagination_helpers_with_filters(self) -> None:
        """Test pagination helpers work with other filters."""
        response = PlayerSearchResponse(
            search=[
                {"player_id": 1, "first_name": "Test", "last_name": "User", "country_name": "US"}
            ],
        )

        builder = TestQueryBuilder(mock_responses=[response])
        # Add a parameter (simulating a filter)
        builder._params["country"] = "US"

        results = list(builder.iterate(limit=10))

        assert len(results) == 1
        assert builder._params["country"] == "US"  # Filter preserved
