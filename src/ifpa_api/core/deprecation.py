"""Deprecation utilities for the IFPA SDK.

This module provides utilities for deprecating methods and classes in a consistent way,
with clear migration guidance for users.
"""

import functools
import warnings
from collections.abc import Callable
from typing import Any, TypeVar

# Type variable for decorated function
F = TypeVar("F", bound=Callable[..., Any])


def deprecated(
    *,
    replacement: str,
    version: str = "1.0.0",
    additional_info: str | None = None,
) -> Callable[[F], F]:
    """Decorator to mark methods/functions as deprecated.

    This decorator issues a DeprecationWarning when the decorated function is called,
    providing clear guidance on what method should be used instead.

    Args:
        replacement: The new method/function name that should be used instead
        version: Version when the deprecated feature will be removed (default: "1.0.0")
        additional_info: Optional additional migration guidance

    Returns:
        Decorator function

    Example:
        ```python
        class PlayerClient:
            @deprecated(replacement="player.get(player_id)", version="1.0.0")
            def __call__(self, player_id: int | str) -> _PlayerContext:
                return _PlayerContext(self._http, player_id, self._validate_requests)

            def get(self, player_id: int | str) -> Player:
                '''Get player by ID.'''
                return self(player_id).details()
        ```
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build deprecation message
            message_parts = [
                f"{func.__name__}() is deprecated and will be removed in version {version}.",
                f"Use {replacement} instead.",
            ]

            if additional_info:
                message_parts.append(additional_info)

            message = " ".join(message_parts)

            # Issue warning
            warnings.warn(
                message,
                category=DeprecationWarning,
                stacklevel=2,
            )

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def issue_deprecation_warning(
    old_name: str,
    new_name: str,
    version: str = "1.0.0",
    additional_info: str | None = None,
) -> None:
    """Issue a deprecation warning for a method or feature.

    This function can be called directly within a method to issue a deprecation warning,
    useful for cases where the decorator pattern isn't suitable.

    Args:
        old_name: Name of the deprecated method/feature
        new_name: Name of the replacement method/feature
        version: Version when the deprecated feature will be removed
        additional_info: Optional additional migration guidance

    Example:
        ```python
        def query(self, name: str = "") -> PlayerQueryBuilder:
            '''Deprecated: Use search() instead.'''
            issue_deprecation_warning(
                old_name="query()",
                new_name="search()",
                version="1.0.0",
                additional_info="The search() method provides the same functionality.",
            )
            return self.search(name)
        ```
    """
    message_parts = [
        f"{old_name} is deprecated and will be removed in version {version}.",
        f"Use {new_name} instead.",
    ]

    if additional_info:
        message_parts.append(additional_info)

    message = " ".join(message_parts)

    warnings.warn(
        message,
        category=DeprecationWarning,
        stacklevel=3,  # Skip this function and the calling function
    )
