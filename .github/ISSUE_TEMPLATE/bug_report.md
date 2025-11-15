---
name: Bug Report
about: Report a bug or unexpected behavior in the IFPA API client
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## Bug Description

A clear and concise description of the bug.

## Steps to Reproduce

1. Install the package: `pip install ifpa-api`
2. Run the following code:
```python
# Your code here
```
3. Observe the error

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened, including error messages and stack traces.

```
Paste error message or stack trace here
```

## Environment

- **IFPA API Version**: (e.g., 0.2.0)
- **Python Version**: (e.g., 3.11.5)
- **Operating System**: (e.g., macOS 14.0, Ubuntu 22.04, Windows 11)
- **Installation Method**: (e.g., pip, poetry)

## Additional Context

Add any other context about the problem here, such as:
- Does this happen consistently or intermittently?
- Are you using any specific configuration or environment variables?
- Have you tried any workarounds?

## Minimal Reproducible Example

If possible, provide a minimal, complete, and verifiable example that demonstrates the issue:

```python
from ifpa_api import IfpaClient

# Minimal code that reproduces the issue
client = IfpaClient(api_key="your_key_here")
# ...
```

## Possible Solution

(Optional) If you have suggestions on how to fix this bug, please share them here.
