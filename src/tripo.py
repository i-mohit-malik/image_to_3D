"""Legacy compatibility module.

This module exists to preserve the public import path `src.tripo` for older
code. New code should prefer `src.tripo_client` and instantiate `TripoClient`.
"""

from tripo_client import TripoClient  # noqa: F401

__all__ = ["TripoClient"]
