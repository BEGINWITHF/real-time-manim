"""Compatibility shim: shape senders moved to ``real_time_manim.render.shapes``.

The old import path stays importable; it only re-exports what the
old module defined.
"""

# ruff: noqa: F401  -- this module IS a re-export surface.

from real_time_manim.render.shapes import (
    ShapeMixin,
)

__all__ = [
    "ShapeMixin",
]
