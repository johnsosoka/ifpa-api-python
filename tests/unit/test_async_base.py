"""Tests for async core base classes and mixins."""

from typing import Any
from unittest.mock import Mock

import pytest

from ifpa_api.core.async_base import (
    AsyncBaseResourceClient,
    AsyncBaseResourceContext,
    LocationFiltersMixin,
    PaginationMixin,
)
from ifpa_api.core.async_query_builder import AsyncQueryBuilder


class TestAsyncBaseResourceContext:
    """Test AsyncBaseResourceContext initialization."""

    def test_initialization_with_int_id(self) -> None:
        """Test async context initialization with integer resource ID."""
        http = Mock()
        context = AsyncBaseResourceContext[int](http, 12345, validate_requests=True)

        assert context._http is http
        assert context._resource_id == 12345
        assert context._validate_requests is True

    def test_initialization_with_string_id(self) -> None:
        """Test async context initialization with string resource ID."""
        http = Mock()
        context = AsyncBaseResourceContext[str](http, "PAPA", validate_requests=False)

        assert context._http is http
        assert context._resource_id == "PAPA"
        assert context._validate_requests is False

    def test_initialization_with_union_id(self) -> None:
        """Test async context initialization with int | str resource ID."""
        http = Mock()
        context_int = AsyncBaseResourceContext[int | str](http, 12345, validate_requests=True)
        context_str = AsyncBaseResourceContext[int | str](http, "PAPA", validate_requests=True)

        assert context_int._resource_id == 12345
        assert context_str._resource_id == "PAPA"


class TestAsyncBaseResourceClient:
    """Test AsyncBaseResourceClient initialization."""

    def test_initialization(self) -> None:
        """Test async client initialization."""
        http = Mock()
        client = AsyncBaseResourceClient(http, validate_requests=True)

        assert client._http is http
        assert client._validate_requests is True

    def test_initialization_with_validation_disabled(self) -> None:
        """Test async client initialization with validation disabled."""
        http = Mock()
        client = AsyncBaseResourceClient(http, validate_requests=False)

        assert client._http is http
        assert client._validate_requests is False


class TestLocationFiltersMixinWithAsync:
    """Test LocationFiltersMixin methods with async query builder."""

    class MockAsyncQueryBuilder(AsyncQueryBuilder[dict[str, Any]], LocationFiltersMixin):
        """Mock async query builder with LocationFiltersMixin."""

        def __init__(self, http: Mock) -> None:
            super().__init__()
            self._http = http

        async def get(self) -> dict[str, Any]:
            """Return params dict for testing."""
            return self._params

    def test_country_filter(self) -> None:
        """Test country filter method."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.country("US")

        assert result._params["country"] == "US"
        assert result is not builder  # Immutable pattern

    def test_state_filter(self) -> None:
        """Test state filter method."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.state("WA")

        assert result._params["stateprov"] == "WA"
        assert result is not builder

    def test_city_filter(self) -> None:
        """Test city filter method."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.city("Seattle")

        assert result._params["city"] == "Seattle"
        assert result is not builder

    def test_filter_chaining(self) -> None:
        """Test chaining multiple location filters."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.country("US").state("WA").city("Seattle")

        assert result._params["country"] == "US"
        assert result._params["stateprov"] == "WA"
        assert result._params["city"] == "Seattle"

    def test_immutability(self) -> None:
        """Test that filters create new instances (immutable pattern)."""
        http = Mock()
        base = self.MockAsyncQueryBuilder(http)

        us_query = base.country("US")
        ca_query = base.country("CA")

        assert base._params == {}
        assert us_query._params["country"] == "US"
        assert ca_query._params["country"] == "CA"

    @pytest.mark.asyncio
    async def test_get_with_filters(self) -> None:
        """Test that get() works with filters applied."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result_builder = builder.country("US").state("WA")
        params = await result_builder.get()

        assert params["country"] == "US"
        assert params["stateprov"] == "WA"


class TestPaginationMixinWithAsync:
    """Test PaginationMixin methods with async query builder."""

    class MockAsyncQueryBuilder(AsyncQueryBuilder[dict[str, Any]], PaginationMixin):
        """Mock async query builder with PaginationMixin."""

        def __init__(self, http: Mock) -> None:
            super().__init__()
            self._http = http

        async def get(self) -> dict[str, Any]:
            """Return params dict for testing."""
            return self._params

    def test_limit_filter(self) -> None:
        """Test limit method."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.limit(50)

        assert result._params["count"] == 50
        assert result is not builder  # Immutable pattern

    def test_offset_filter(self) -> None:
        """Test offset method."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.offset(25)

        assert result._params["start_pos"] == 26
        assert result is not builder

    def test_pagination_chaining(self) -> None:
        """Test chaining limit and offset."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result = builder.offset(25).limit(50)

        assert result._params["start_pos"] == 26
        assert result._params["count"] == 50

    def test_immutability(self) -> None:
        """Test that pagination methods create new instances."""
        http = Mock()
        base = self.MockAsyncQueryBuilder(http)

        page1 = base.limit(25).offset(0)
        page2 = base.limit(25).offset(25)

        assert base._params == {}
        assert page1._params["count"] == 25
        assert page1._params["start_pos"] == 1
        assert page2._params["count"] == 25
        assert page2._params["start_pos"] == 26

    @pytest.mark.asyncio
    async def test_get_with_pagination(self) -> None:
        """Test that get() works with pagination applied."""
        http = Mock()
        builder = self.MockAsyncQueryBuilder(http)

        result_builder = builder.limit(25).offset(50)
        params = await result_builder.get()

        assert params["count"] == 25
        assert params["start_pos"] == 51


class TestAsyncMixinCombination:
    """Test combining LocationFiltersMixin and PaginationMixin with async."""

    class FullAsyncQueryBuilder(
        AsyncQueryBuilder[dict[str, Any]], LocationFiltersMixin, PaginationMixin
    ):
        """Async query builder with both mixins."""

        def __init__(self, http: Mock) -> None:
            super().__init__()
            self._http = http

        async def get(self) -> dict[str, Any]:
            """Return params dict for testing."""
            return self._params

    def test_combine_location_and_pagination(self) -> None:
        """Test using both location and pagination filters."""
        http = Mock()
        builder = self.FullAsyncQueryBuilder(http)

        result = builder.country("US").state("WA").limit(50).offset(25)

        assert result._params["country"] == "US"
        assert result._params["stateprov"] == "WA"
        assert result._params["count"] == 50
        assert result._params["start_pos"] == 26

    def test_query_reuse_with_both_mixins(self) -> None:
        """Test query reuse pattern with both mixins."""
        http = Mock()
        base = self.FullAsyncQueryBuilder(http)

        # Create reusable base query
        us_query = base.country("US")

        # Derive different queries from base
        wa_page1 = us_query.state("WA").limit(25).offset(0)
        wa_page2 = us_query.state("WA").limit(25).offset(25)
        or_page1 = us_query.state("OR").limit(25).offset(0)

        # Verify base is unchanged
        assert base._params == {}

        # Verify derived queries
        assert wa_page1._params == {
            "country": "US",
            "stateprov": "WA",
            "count": 25,
            "start_pos": 1,
        }
        assert wa_page2._params == {
            "country": "US",
            "stateprov": "WA",
            "count": 25,
            "start_pos": 26,
        }
        assert or_page1._params == {
            "country": "US",
            "stateprov": "OR",
            "count": 25,
            "start_pos": 1,
        }

    @pytest.mark.asyncio
    async def test_async_get_with_all_filters(self) -> None:
        """Test async get() with all filters combined."""
        http = Mock()
        builder = self.FullAsyncQueryBuilder(http)

        result_builder = builder.country("US").state("WA").city("Seattle").limit(50).offset(25)
        params = await result_builder.get()

        assert params["country"] == "US"
        assert params["stateprov"] == "WA"
        assert params["city"] == "Seattle"
        assert params["count"] == 50
        assert params["start_pos"] == 26

    @pytest.mark.asyncio
    async def test_async_query_reuse(self) -> None:
        """Test async query reuse with multiple derivations."""
        http = Mock()
        base = self.FullAsyncQueryBuilder(http)

        # Create reusable base query
        us_query = base.country("US")

        # Execute different derived queries
        wa_result = await us_query.state("WA").get()
        ca_result = await us_query.state("CA").get()

        # Verify each result is independent
        assert wa_result["country"] == "US"
        assert wa_result["stateprov"] == "WA"
        assert ca_result["country"] == "US"
        assert ca_result["stateprov"] == "CA"

        # Verify base is unchanged
        assert base._params == {}
