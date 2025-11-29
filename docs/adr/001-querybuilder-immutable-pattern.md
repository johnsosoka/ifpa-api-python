# ADR 001: QueryBuilder Immutable Pattern

**Status:** Accepted
**Date:** 2025-11-22
**Decision Makers:** Technical Team
**Related:** [Resource API Standards](../development/resource_api_standards.md)

## Context

QueryBuilder classes enable fluent API patterns for constructing complex queries:

```python
results = (client.player.search("Smith")
    .country("US")
    .state("WA")
    .limit(25)
    .get())
```

The decision: Should QueryBuilder instances be **mutable** (methods modify `self`) or **immutable** (methods return new instances)?

### Option 1: Mutable Pattern
```python
def country(self, code: str) -> Self:
    self._params["country"] = code  # Modifies self
    return self
```

**Pros:**
- Simpler implementation
- Slightly better performance (no object copying)
- Common in some builder patterns

**Cons:**
- Cannot reuse base queries safely
- Side effects make debugging harder
- Unpredictable behavior when sharing instances

### Option 2: Immutable Pattern (via `_clone()`)
```python
def country(self, code: str) -> Self:
    clone = self._clone()  # Create new instance
    clone._params["country"] = code
    return clone
```

**Pros:**
- Query reuse without side effects
- Predictable behavior
- Enables composition patterns
- Easier to debug (no hidden mutations)

**Cons:**
- Slightly more complex implementation
- Minimal performance overhead from copying

## Decision

**Adopt the immutable pattern** for all QueryBuilder implementations.

### Rationale

The immutable pattern enables powerful composition and reuse patterns:

```python
# Create reusable base query
us_query = client.player.search().country("US")

# Derive multiple queries - each is independent
wa_players = us_query.state("WA").get()
or_players = us_query.state("OR").get()
ca_players = us_query.state("CA").get()

# Base query unchanged - can continue using
midwest = us_query.state("IL").get()
```

With mutable pattern, this would fail because `.state("WA")` modifies `us_query`, corrupting all subsequent uses.

### Implementation Requirements

1. **All filter methods must use `_clone()`:**
   ```python
   def filter_method(self, value: str) -> Self:
       clone = self._clone()  # REQUIRED
       clone._params["key"] = value
       return clone
   ```

2. **`_clone()` performs shallow copy with explicit params copy:**
   ```python
   def _clone(self) -> Self:
       clone = copy(self)  # Shallow copy
       clone._params = self._params.copy()  # Deep copy params dict
       return clone
   ```

3. **Never modify `self._params` directly in filter methods**

## Consequences

### Positive
- **Query Reuse:** Users can create base queries and derive variations
- **Predictability:** No hidden mutations, easier to reason about code
- **Testing:** Immutable objects easier to test and mock
- **Concurrency:** Safe to use in concurrent contexts (though HTTP client may not be)

### Negative
- **Memory:** Creates new objects for each method call (negligible impact)
- **Performance:** Minimal overhead from copying small parameter dictionaries
- **Learning Curve:** Developers familiar with mutable builders may find this unexpected

### Mitigation
- Document immutable behavior clearly in QueryBuilder docstrings
- Provide examples demonstrating query reuse patterns
- Include warning in code review checklist about using `_clone()`

## Examples

### Correct Implementation
```python
class PlayerQueryBuilder(QueryBuilder[PlayerSearchResponse]):
    def country(self, country_code: str) -> Self:
        clone = self._clone()  # Creates new instance
        clone._params["country"] = country_code
        return clone
```

### Incorrect Implementation (Anti-Pattern)
```python
class PlayerQueryBuilder(QueryBuilder[PlayerSearchResponse]):
    def country(self, country_code: str) -> Self:
        self._params["country"] = country_code  # WRONG: Mutates self
        return self
```

## Alternatives Considered

### Builder with `.build()` Terminal Method
```python
query = (client.player.search("Smith")
    .country("US")
    .state("WA")
    .build())  # Terminal operation
results = query.execute()
```

**Rejected because:**
- Extra method call for no benefit
- Less fluent API (two-step: build → execute)
- Still requires immutability for safe reuse

### Explicit Copy Method
```python
base = client.player.search().country("US")
wa_query = base.copy().state("WA")
or_query = base.copy().state("OR")
```

**Rejected because:**
- Burdens users with explicit copying
- Easy to forget `.copy()` and introduce bugs
- Less ergonomic API

## References

- [Effective Python: Item 23 - Accept Functions Instead of Classes for Simple Interfaces](https://effectivepython.com/)
- [Python Patterns - Immutable Objects](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- QueryBuilder base implementation: `src/ifpa_api/core/query_builder.py`

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-22 | Technical Team | Initial ADR documenting immutable pattern decision |
