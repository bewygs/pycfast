"""Base class for every CFAST components (Fire, Device, Material, ...)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class CFASTComponent(ABC):
    """Base class for all CFAST components."""

    _initialized: bool = False

    #: Fixed-length sequence attributes normalized to tuple on assignment.
    _TUPLE_FIELDS: ClassVar[frozenset[str]] = frozenset()

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an attribute, validating the component if already initialized."""
        if isinstance(value, list) and key in self._TUPLE_FIELDS:
            value = tuple(value)
        object.__setattr__(self, key, value)
        if key.startswith("_") or not self._initialized:
            return
        self._validate()

    @abstractmethod
    def _validate(self) -> None:
        """
        Validate component-specific rules.

        Subclasses must implement their own validation rules.
        """
