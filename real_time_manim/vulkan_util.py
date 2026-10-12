"""Compatibility shim: coordinate + colour helpers moved to ``real_time_manim.render.util``.

The old import path stays importable; it only re-exports what the
old module defined.
"""

# ruff: noqa: F401  -- this module IS a re-export surface.

from real_time_manim.render.util import (
    manim_to_screen,
    rotate_point,
    point_path_bounds,
    get_fill_rgb,
    get_fill_rgb_raw,
    _shade_one,
    _unit_normal,
    _corner_normal,
    shaded_fill_rgb,
    shaded_fill_gradient,
    get_stroke_rgb,
    get_stroke_w,
    get_opacity,
)

__all__ = [
    "manim_to_screen",
    "rotate_point",
    "point_path_bounds",
    "get_fill_rgb",
    "get_fill_rgb_raw",
    "_shade_one",
    "_unit_normal",
    "_corner_normal",
    "shaded_fill_rgb",
    "shaded_fill_gradient",
    "get_stroke_rgb",
    "get_stroke_w",
    "get_opacity",
]
