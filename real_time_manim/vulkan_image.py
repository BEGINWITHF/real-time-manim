"""Compatibility shim: textured-quad helpers moved to ``real_time_manim.render.image``.

The old import path stays importable; it only re-exports what the
old module defined.
"""

# ruff: noqa: F401  -- this module IS a re-export surface.

from real_time_manim.render.image import (
    _tokens,
    _DEBUG,
    _pixel_array,
    _token,
    _corners,
    _digest,
    send_image,
)

__all__ = [
    "_tokens",
    "_DEBUG",
    "_pixel_array",
    "_token",
    "_corners",
    "_digest",
    "send_image",
]
