"""Base class for every CFAST components (Fire, Device, Material, ...)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CFASTComponent(ABC):
    """Base class for all CFAST components."""

    _initialized: bool = False

    def __setattr__(self, key: str, value: Any) -> None:
        """Set an attribute, validating the component if already initialized."""
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
