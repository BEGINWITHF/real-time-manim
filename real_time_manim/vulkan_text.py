"""Compatibility shim: text / bezier rendering moved to ``real_time_manim.render.text``.

The old import path stays importable; it only re-exports what the
old module defined.
"""

# ruff: noqa: F401  -- this module IS a re-export surface.

from real_time_manim.render.text import (
    TextMixin,
)

__all__ = [
    "TextMixin",
]
