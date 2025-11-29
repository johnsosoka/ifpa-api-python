# ADR 003: Convenience Methods vs Callable Pattern

**Status:** Accepted
**Date:** 2025-11-22
**Decision Makers:** Technical Team
**Related:** [Resource API Standards](../development/resource_api_standards.md)

## Context

Resources with ID-based operations support two access patterns:

### Pattern 1: Callable Pattern (Legacy)
```python
player = client.player(12345).details()
rankings = client.player(12345).rankings()
results = client.player(12345).results()
```

### Pattern 2: Convenience Methods (New)
```python
player = client.player.get(12345)
# But rankings/results still use callable pattern:
rankings = client.player(12345).rankings()
results = client.player(12345).results()
```

**Decision needed:** Which pattern should be primary? Should both coexist?

## Options Considered

### Option 1: Callable Pattern Only (Status Quo Before v0.4)
```python
player = client.player(12345).details()
rankings = client.player(12345).rankings()
```

**Pros:**
- Consistent: All ID-based operations use same pattern
- Fluent: Chain from resource to operation

**Cons:**
- Verbose: Two-step access for simple detail fetch
- Unfamiliar: Unusual pattern for Python developers
- Discoverable: Harder to find operations (hidden in context)

### Option 2: Convenience Methods Only
```python
player = client.player.get(12345)
rankings = client.player.get_rankings(12345)
results = client.player.get_results(12345)
```

**Pros:**
- Pythonic: Familiar method-based API
- Flat: All operations at same level (client.resource.operation)
- Discoverable: IDE autocomplete shows all operations

**Cons:**
- Repetitive: Must pass ID to every method
- Parameter explosion: Complex operations need many params
- Long method names: `get_results(id, system, type, start, count)` gets unwieldy

### Option 3: Hybrid Approach (Adopted)
```python
# Simple details access: Convenience method
player = client.player.get(12345)
player = client.player.get_or_none(12345)  # None on 404
exists = client.player.exists(12345)  # Boolean check

# Complex operations: Context pattern
rankings = client.player(12345).rankings()
results = client.player(12345).results(system=RankingSystem.MAIN, type=ResultType.ACTIVE)
pvp = client.player(12345).pvp(opponent_id=67890)
```

**Pros:**
- Best of both worlds: Simple things simple, complex things manageable
- Pythonic primary access: `.get()` matches Django ORM, SQLAlchemy patterns
- Context for complexity: Multi-parameter operations grouped logically
- Gradual migration: Add convenience methods without breaking existing code

**Cons:**
- Two patterns: Need to document when to use each
- Partial inconsistency: Details different from other operations

## Decision

**Adopt Option 3: Hybrid Approach**

### Guiding Principles

1. **Use convenience methods for primary resource access:**
   - `.get(id)` - Get resource, raise on 404
   - `.get_or_none(id)` - Get resource, return None on 404
   - `.exists(id)` - Check if resource exists

2. **Use context pattern for:**
   - Multi-parameter operations (rankings, results, pvp)
   - Domain-specific operations unique to resource
   - Operations requiring additional context

3. **Deprecate callable for simple details:**
   - `client.player(id).details()` deprecated in favor of `.get(id)`
   - Context methods (rankings, results, etc.) remain as-is

### Rationale

**Why convenience methods for details:**
```python
# More Pythonic, matches familiar patterns
player = client.player.get(12345)

# vs verbose callable
player = client.player(12345).details()
```

**Why context pattern for complex operations:**
```python
# Context groups related operations naturally
rankings = client.player(12345).rankings()
results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player(12345).pvp(67890)

# vs unwieldy flat methods
rankings = client.player.get_rankings(12345)
results = client.player.get_results(12345, RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player.get_pvp(12345, 67890)
```

### Implementation Requirements

1. **All resources with IDs must implement:**
   ```python
   def get(self, resource_id: int | str) -> Resource:
       """Get resource by ID."""
       return self(resource_id).details()

   def get_or_none(self, resource_id: int | str) -> Resource | None:
       """Get resource, return None on 404."""
       try:
           return self.get(resource_id)
       except IfpaApiError as e:
           if e.status_code == 404:
               return None
           raise

   def exists(self, resource_id: int | str) -> bool:
       """Check if resource exists."""
       return self.get_or_none(resource_id) is not None
   ```

2. **Context methods remain unchanged:**
   - No convenience wrappers for complex operations
   - Keep domain-specific operations in context

3. **Deprecation warnings for callable details:**
   ```python
   def __call__(self, resource_id: int | str) -> _ResourceContext:
       """DEPRECATED for details access. Use .get() instead."""
       # Warning omitted here to avoid noise on legitimate context usage
       return _ResourceContext(self._http, resource_id, self._validate_requests)
   ```

## Consequences

### Positive
- **Improved Discoverability:** `.get()` appears in IDE autocomplete at client level
- **Pythonic API:** Matches patterns from Django ORM, SQLAlchemy, peewee
- **Convenience:** Common case (get details) is simpler
- **Backward Compatible:** Existing callable code continues to work

### Negative
- **Two Patterns:** Users must learn when to use each
- **Documentation Burden:** Must explain both patterns clearly
- **Partial Consistency:** `.get()` different from `.rankings()`, `.results()`

### Mitigation

**Clear Documentation:**
```python
# In client docstrings and README

# Direct access (preferred for details)
player = client.player.get(12345)

# Context operations (for complex/multi-param methods)
rankings = client.player(12345).rankings()
results = client.player(12345).results(system, type)
```

**IDE Hints:**
```python
def get(self, player_id: int | str) -> Player:
    """Get player by ID (preferred method).

    For other player operations (rankings, results, pvp), use the
    context pattern: client.player(id).rankings()
    """
```

## Examples

### Player Resource
```python
# Primary access: Convenience methods
player = client.player.get(12345)
player = client.player.get_or_none(99999)
if client.player.exists(12345):
    print("Player exists")

# Complex operations: Context pattern
rankings = client.player(12345).rankings()
results = client.player(12345).results(RankingSystem.MAIN, ResultType.ACTIVE)
pvp = client.player(12345).pvp(opponent_id=67890)
history = client.player(12345).history()
```

### Director Resource
```python
# Primary access: Convenience methods
director = client.director.get(1533)
director = client.director.get_or_none(9999)

# Context operations
tournaments = client.director(1533).tournaments(TimePeriod.PAST)
```

### Tournament Resource
```python
# Primary access: Convenience methods
tournament = client.tournament.get(54321)
exists = client.tournament.exists(54321)

# Context operations
results = client.tournament(54321).results()
formats = client.tournament(54321).formats()
league = client.tournament(54321).league()
```

### Series Resource (Special Case)
```python
# Primary access: Convenience methods return standings
standings = client.series.get("NACS")  # Returns standings
exists = client.series.exists("NACS")

# Context operations for region/year operations
region_standings = client.series("NACS").region_standings("NW")
player_card = client.series("NACS").player_card(12345, "NW", 2024)
stats = client.series("NACS").stats("NW")
```

## When to Use Each Pattern

### Use Convenience Methods (`.get()`, `.get_or_none()`, `.exists()`)
- Getting primary resource details
- Checking if resource exists
- Need null-safe access (404 → None)
- One-parameter operations

### Use Context Pattern (`client.resource(id).operation()`)
- Multi-parameter operations
- Domain-specific operations
- Operations requiring additional context beyond ID
- When grouping related operations makes sense

## Future Considerations

### Potential v5.0 Evolution

**Option A: Maintain Hybrid (Likely)**
- Proven to work well in practice
- Users understand the distinction
- No breaking changes needed

**Option B: Full Convenience Methods**
- Replace all context operations with convenience methods
- Breaking change for existing code
- May result in less ergonomic API for complex operations

**Recommendation:** Maintain hybrid approach. It provides the best balance of simplicity and power.

## References

- Django ORM: `.objects.get(pk=1)`, `.objects.get_or_create()`
- SQLAlchemy: `session.query(User).get(1)`
- Python Patterns: [Factory Pattern](https://refactoring.guru/design-patterns/factory-method/python/example)
- Implementation: `src/ifpa_api/resources/player/client.py`

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-22 | Technical Team | Initial ADR documenting convenience methods vs callable pattern |
