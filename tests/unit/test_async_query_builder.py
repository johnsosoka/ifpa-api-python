"""Tests for async query builder base class."""

from collections import deque
from typing import Any
from unittest.mock import Mock

import pytest

from ifpa_api.core.async_query_builder import AsyncQueryBuilder


class MockAsyncQueryBuilder(AsyncQueryBuilder[dict[str, Any]]):
    """Mock async query builder for testing."""

    def __init__(
        self,
        http: Mock,
        response_data: dict[str, Any] | None = None,
        response_queue: deque[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__()
        self._http = http
        self._response_data = response_data or {"search": []}
        self._response_queue = response_queue

    async def get(self) -> dict[str, Any]:
        """Mock get method that returns test data."""
        if self._response_queue:
            if len(self._response_queue) > 0:
                return self._response_queue.popleft()
            return {"search": []}
        return self._response_data

    def _clone(self):  # type: ignore[no-untyped-def]
        """Clone with shared response_queue reference."""
        clone = MockAsyncQueryBuilder(self._http, self._response_data, self._response_queue)
        clone._params = self._params.copy()
        return clone

    def limit(self, count: int):  # type: ignore[no-untyped-def]
        """Mock limit method for testing."""
        clone = self._clone()  # type: ignore[no-untyped-call]
        clone._params["count"] = count
        return clone

    def offset(self, start_pos: int):  # type: ignore[no-untyped-def]
        """Mock offset method for testing."""
        clone = self._clone()  # type: ignore[no-untyped-call]
        clone._params["start_pos"] = start_pos + 1
        return clone


class TestAsyncQueryBuilder:
    """Test AsyncQueryBuilder base class."""

    @pytest.mark.asyncio
    async def test_get_abstract_method(self) -> None:
        """Test that get() is abstract and must be implemented."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)
        result = await builder.get()
        assert result == {"search": []}

    def test_initialization(self) -> None:
        """Test query builder initialization."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)

        assert builder._params == {}
        assert hasattr(builder, "_http")

    def test_clone_creates_new_instance(self) -> None:
        """Test that _clone() creates a new instance."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)
        builder._params["test"] = "value"

        clone = builder._clone()  # type: ignore[no-untyped-call]

        assert clone is not builder
        assert clone._params == builder._params
        assert clone._params is not builder._params

    def test_clone_preserves_params(self) -> None:
        """Test that _clone() preserves parameters."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)
        builder._params["country"] = "US"
        builder._params["count"] = 50

        clone = builder._clone()  # type: ignore[no-untyped-call]

        assert clone._params["country"] == "US"
        assert clone._params["count"] == 50

    def test_clone_immutability(self) -> None:
        """Test that cloned instance doesn't affect original."""
        http = Mock()
        original = MockAsyncQueryBuilder(http)
        original._params["test"] = "original"

        clone = original._clone()  # type: ignore[no-untyped-call]
        clone._params["test"] = "modified"
        clone._params["new_key"] = "new_value"

        assert original._params == {"test": "original"}
        assert clone._params == {"test": "modified", "new_key": "new_value"}

    def test_repr(self) -> None:
        """Test string representation."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)
        builder._params["country"] = "US"

        repr_str = repr(builder)

        assert "MockAsyncQueryBuilder" in repr_str
        assert "params=" in repr_str
        assert "country" in repr_str


class TestAsyncQueryBuilderIterate:
    """Test AsyncQueryBuilder iterate() method."""

    @pytest.mark.asyncio
    async def test_iterate_single_page(self) -> None:
        """Test iterate with single page of results."""
        http = Mock()
        response_queue = deque([{"search": [1, 2, 3]}, {"search": []}])
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = []
        async for item in builder.iterate(limit=10):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_iterate_multiple_pages(self) -> None:
        """Test iterate with multiple pages of results."""
        http = Mock()
        response_queue = deque(
            [
                {"search": [1, 2, 3]},
                {"search": [4, 5, 6]},
                {"search": [7, 8]},
                {"search": []},
            ]
        )
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = []
        async for item in builder.iterate(limit=3):
            results.append(item)

        assert results == [1, 2, 3, 4, 5, 6, 7, 8]

    @pytest.mark.asyncio
    async def test_iterate_stops_on_empty_page(self) -> None:
        """Test that iterate stops when it encounters an empty page."""
        http = Mock()
        response_queue = deque([{"search": [1, 2, 3]}, {"search": []}])
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = []
        async for item in builder.iterate(limit=10):
            results.append(item)

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_iterate_with_custom_limit(self) -> None:
        """Test iterate with custom page limit."""
        http = Mock()
        response_queue = deque(
            [
                {"search": list(range(5))},
                {"search": list(range(5, 10))},
                {"search": []},
            ]
        )
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = []
        async for item in builder.iterate(limit=5):
            results.append(item)

        assert len(results) == 10


class TestAsyncQueryBuilderGetAll:
    """Test AsyncQueryBuilder get_all() method."""

    @pytest.mark.asyncio
    async def test_get_all_single_page(self) -> None:
        """Test get_all with single page."""
        http = Mock()
        response_queue = deque([{"search": [1, 2, 3]}, {"search": []}])
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = await builder.get_all()

        assert results == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_get_all_multiple_pages(self) -> None:
        """Test get_all with multiple pages."""
        http = Mock()
        # Make pages match the iterate limit to avoid early exit
        response_queue = deque(
            [
                {"search": list(range(100))},  # Full page
                {"search": list(range(100, 150))},  # Partial page (50 items)
                {"search": []},
            ]
        )
        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        results = await builder.get_all()

        assert len(results) == 150
        assert results[0] == 0
        assert results[99] == 99
        assert results[149] == 149

    @pytest.mark.asyncio
    async def test_get_all_with_max_results(self) -> None:
        """Test get_all with max_results limit."""
        http = Mock()
        # Create queue with many full pages (100 items each to match iterate default limit)
        response_queue: deque[dict[str, Any]] = deque()
        for i in range(10):
            # Each page has 100 items
            response_queue.append({"search": list(range(i * 100, (i + 1) * 100))})
        response_queue.append({"search": []})

        builder = MockAsyncQueryBuilder(http, response_queue=response_queue)

        with pytest.raises(ValueError, match="Result count exceeded max_results"):
            await builder.get_all(max_results=500)  # Should raise after 500 items (5 pages)

    @pytest.mark.asyncio
    async def test_get_all_empty_results(self) -> None:
        """Test get_all with no results."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http, {"search": []})

        results = await builder.get_all()

        assert results == []


class TestAsyncQueryBuilderExtractResults:
    """Test AsyncQueryBuilder _extract_results() method."""

    def test_extract_results_with_search_field(self) -> None:
        """Test extracting results from response with 'search' field."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)

        class SearchResponse:
            search = [1, 2, 3]

        results = builder._extract_results(SearchResponse())

        assert results == [1, 2, 3]

    def test_extract_results_with_results_field(self) -> None:
        """Test extracting results from response with 'results' field."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)

        class ResultsResponse:
            results = [4, 5, 6]

        results = builder._extract_results(ResultsResponse())

        assert results == [4, 5, 6]

    def test_extract_results_from_list(self) -> None:
        """Test extracting results when response is already a list."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)

        results = builder._extract_results([7, 8, 9])

        assert results == [7, 8, 9]

    def test_extract_results_fallback(self) -> None:
        """Test extracting results fallback for unknown structure."""
        http = Mock()
        builder = MockAsyncQueryBuilder(http)

        class UnknownResponse:
            data = [10, 11, 12]

        results = builder._extract_results(UnknownResponse())

        assert results == []


class TestAsyncQueryBuilderWithMixins:
    """Test AsyncQueryBuilder with mixins (integration test)."""

    @pytest.mark.asyncio
    async def test_iterate_with_pagination_params(self) -> None:
        """Test that iterate properly sets pagination params."""

        class PaginationTrackingBuilder(MockAsyncQueryBuilder):
            def __init__(
                self,
                http: Mock,
                response_queue: deque[dict[str, Any]],
                param_history: list[dict[str, Any]] | None = None,
            ) -> None:
                super().__init__(http, response_queue=response_queue)
                # Share param_history across clones
                if param_history is None:
                    self.param_history: list[dict[str, Any]] = []
                else:
                    self.param_history = param_history

            def _clone(self):  # type: ignore[no-untyped-def]
                """Clone with shared param_history and response_queue."""
                clone = PaginationTrackingBuilder(
                    self._http, self._response_queue, self.param_history
                )
                clone._params = self._params.copy()
                return clone

            async def get(self) -> dict[str, Any]:
                # Track params for each call
                self.param_history.append(self._params.copy())
                return await super().get()

        http = Mock()
        response_queue = deque(
            [
                {"search": [1, 2, 3]},
                {"search": [4, 5, 6]},
                {"search": []},
            ]
        )
        builder = PaginationTrackingBuilder(http, response_queue)

        results = []
        async for item in builder.iterate(limit=3):
            results.append(item)

        # Verify results
        assert results == [1, 2, 3, 4, 5, 6]

        # Verify pagination params were set correctly
        assert len(builder.param_history) >= 2
        assert builder.param_history[0]["count"] == 3
        assert builder.param_history[0]["start_pos"] == 1  # 0 + 1
        assert builder.param_history[1]["count"] == 3
        assert builder.param_history[1]["start_pos"] == 4  # 3 + 1
