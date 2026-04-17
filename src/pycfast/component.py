"""
Base class for every component (Fire, Device, Material, MechcnicalVent) in CFAST.

This module provides a Component Class that will be herited from every component
in the library. This class contain serveral common method used by all component.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CFASTComponent(ABC):
    """Base class for all CFAST components."""

    def __getitem__(self, key: str) -> Any:
        """Get component property by name for dictionary-like access."""
        if not hasattr(self, key):
            raise KeyError(f"Property '{key}' not found in {self.__class__.__name__}")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set component property by name for dictionary-like assignment.

        Validates the object state after setting the attribute to ensure
        all constraints are still satisfied.

        Raises
        ------
        KeyError
            If the property does not exist.
        ValueError
            If setting this value would violate object constraints.
        """
        if not hasattr(self, key):
            raise KeyError(
                f"Cannot set '{key}'. Property does not exist in Compartment."
            )
        old_value = getattr(self, key)
        setattr(self, key, value)
        try:
            self._validate()
        except Exception:
            setattr(self, key, old_value)
            raise

    @abstractmethod
    def _validate(self) -> None:
        """
        Validate component-specific rules.

        Subclasses must implement their own validation rules.
        """
