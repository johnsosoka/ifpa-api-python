# ADR 002: Parameter Overwriting Detection Strategy

**Status:** Accepted
**Date:** 2025-11-22
**Decision Makers:** Technical Team
**Related:** [ADR 001](001-querybuilder-immutable-pattern.md), [Resource API Standards](../development/resource_api_standards.md)

## Context

The immutable QueryBuilder pattern (ADR 001) prevents accidental mutation, but users can still call the same filter method multiple times:

```python
query = (client.player.search("John")
    .country("US")   # Sets country to US
    .country("CA")   # Overwrites country to CA
    .get())
```

**Problem:** The second `.country("CA")` silently overwrites the first value. User expects US results but gets CA results. This causes subtle bugs that are hard to debug.

### Options Considered

#### Option 1: Allow Silent Overwriting (Status Quo)
```python
query.country("US").country("CA")  # CA wins, no error
```

**Pros:**
- Simplest implementation
- Allows intentional overwrites

**Cons:**
- Mistakes go unnoticed
- Debugging nightmare: "Why isn't my country filter working?"
- Inconsistent with principle of explicit errors over implicit behavior

#### Option 2: Warning on Overwrite
```python
import warnings

def country(self, code: str) -> Self:
    clone = self._clone()
    if "country" in clone._params:
        warnings.warn(
            f"Overwriting country: {clone._params['country']} -> {code}",
            UserWarning
        )
    clone._params["country"] = code
    return clone
```

**Pros:**
- Non-breaking change
- Alerts users to potential mistakes

**Cons:**
- Warnings often ignored or disabled
- Still allows mistakes to happen
- Ambiguous whether intentional or error

#### Option 3: Raise ValueError on Overwrite
```python
def country(self, code: str) -> Self:
    clone = self._clone()
    if "country" in clone._params:
        raise ValueError(
            f"country() called multiple times in query chain. "
            f"Previous value: '{clone._params['country']}', "
            f"Attempted value: '{code}'. "
            f"Create a new query to change filters."
        )
    clone._params["country"] = code
    return clone
```

**Pros:**
- Immediate, explicit feedback
- Forces users to acknowledge the issue
- Clear error message guides resolution

**Cons:**
- Breaking change for code that accidentally overwrites
- More restrictive API

#### Option 4: Accumulate Values (Multi-Value Filters)
```python
def country(self, code: str) -> Self:
    clone = self._clone()
    countries = clone._params.get("countries", [])
    countries.append(code)
    clone._params["countries"] = countries
    return clone
```

**Pros:**
- Enables OR logic: `country("US").country("CA")` = US OR CA

**Cons:**
- API doesn't support multi-value filters
- Confusing semantics (does AND or OR apply?)
- Requires backend support

## Decision

**Adopt Option 3: Raise `ValueError` on parameter overwriting.**

### Rationale

1. **Explicit is better than implicit** (Python Zen)
   - Silent overwrites violate this principle
   - Errors should never pass silently

2. **Fail fast, fail loudly**
   - Catching mistakes during development is better than production bugs
   - Clear error messages guide users to correct patterns

3. **Encourages correct usage patterns**
   - Forces users to think about query composition
   - Promotes immutable query reuse (the right pattern)

4. **Minimal disruption**
   - Most accidental overwrites are bugs
   - Intentional overwrites are rare and easily refactored

### Implementation Requirements

1. **All filter methods must check for existing parameter:**
   ```python
   def filter_method(self, value: str) -> Self:
       clone = self._clone()

       # Check for overwrite
       if "param_key" in clone._params:
           raise ValueError(
               f"filter_method() called multiple times in query chain. "
               f"Previous value: '{clone._params['param_key']}', "
               f"Attempted value: '{value}'. "
               f"This is likely a mistake. Create a new query to change filters."
           )

       clone._params["param_key"] = value
       return clone
   ```

2. **Error messages must be helpful:**
   - State what happened (duplicate call)
   - Show previous and attempted values
   - Suggest resolution (create new query)

3. **Apply to all filter methods:**
   - LocationFiltersMixin: `.country()`, `.state()`, `.city()`
   - PaginationMixin: `.limit()`, `.offset()`
   - Resource-specific filters: `.tournament()`, `.date_range()`, etc.

## Consequences

### Positive
- **Catches Bugs Early:** Users see errors during development, not production
- **Clear Debugging:** Error message shows exactly what was overwritten
- **Encourages Best Practices:** Pushes users toward immutable query reuse
- **Consistent API:** Same behavior across all filters

### Negative
- **Breaking Change:** Code with accidental overwrites will error (but this is good!)
- **More Restrictive:** Cannot intentionally overwrite (must create new query)
- **Code Review Burden:** Developers must remember to add check to new filters

### Mitigation

**For Breaking Change:**
- Include in v4.0 release notes as breaking change
- Provide migration guide showing correct patterns
- Most overwrites are bugs, so impact minimal

**For Intentional Overwrites (rare):**
```python
# Before (broke silently or errors now)
query = base_query.country("US").country("CA")

# After (correct pattern)
base = client.player.search()
us_query = base.country("US")
ca_query = base.country("CA")
```

## Examples

### Error Scenario
```python
>>> query = (client.player.search("Smith")
...     .country("US")
...     .state("WA")
...     .country("CA"))  # Oops! Duplicate country
ValueError: country() called multiple times in query chain.
Previous value: 'US', Attempted value: 'CA'.
This is likely a mistake. Create a new query to change filters.
```

### Correct Usage Patterns

**Pattern 1: Single Filter Value**
```python
# Correct - each filter called once
results = (client.player.search("Smith")
    .country("US")
    .state("WA")
    .limit(25)
    .get())
```

**Pattern 2: Query Reuse (Immutable Pattern)**
```python
# Create base query
us_query = client.player.search().country("US")

# Derive queries - each is independent
wa_results = us_query.state("WA").get()
or_results = us_query.state("OR").get()
```

**Pattern 3: Conditional Filters**
```python
# Build query conditionally
query = client.player.search("Smith")

if user_country:
    query = query.country(user_country)

if user_state:
    query = query.state(user_state)

results = query.get()
```

## Alternatives Rejected

### Separate `.reset_filter()` Method
```python
query.country("US").reset_country().country("CA")
```

**Rejected because:**
- Clutters API with reset methods for every filter
- Still error-prone (forgetting reset)
- Better to create new query

### `.override()` Context Manager
```python
with query.override():
    query = query.country("CA")  # Allowed in override context
```

**Rejected because:**
- Overly complex for rare use case
- Violates immutability principle
- No clear benefit over creating new query

## Testing Requirements

All filter methods must have tests verifying ValueError on duplicate calls:

```python
def test_country_filter_overwrite_raises_error():
    """Test that calling country() twice raises ValueError."""
    client = IfpaClient(api_key="test-key")
    query = client.player.search()

    with pytest.raises(ValueError, match="country\\(\\) called multiple times"):
        query.country("US").country("CA")
```

## Migration Guide

**Old Code (Now Errors):**
```python
# Accidental overwrite
query = query.country("US").country("CA")  # ValueError!
```

**New Code (Correct):**
```python
# Create new query to change filter
us_query = client.player.search().country("US")
ca_query = client.player.search().country("CA")

# Or use base query pattern
base = client.player.search()
us_query = base.country("US")
ca_query = base.country("CA")
```

## References

- Python Zen: "Errors should never pass silently"
- [PEP 20 -- The Zen of Python](https://www.python.org/dev/peps/pep-0020/)
- QueryBuilder implementation: `src/ifpa_api/core/query_builder.py`
- Mixin implementations: `src/ifpa_api/core/base.py`

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-22 | Technical Team | Initial ADR documenting parameter overwriting detection strategy |
