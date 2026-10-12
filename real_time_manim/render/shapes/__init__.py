"""Shape senders: mobject -> native draw calls.

`ShapeMixin` is what `MLWindow` actually inherits; it is only an
assembly of the per-kind senders below, one module each.
"""

from real_time_manim.render.shapes.arrow import ArrowMixin
from real_time_manim.render.shapes.paths import PathMixin
from real_time_manim.render.shapes.points import PointMixin
from real_time_manim.render.shapes.primitives import PrimitiveMixin
from real_time_manim.render.shapes.stroke import StrokeMixin


class ShapeMixin(StrokeMixin, PrimitiveMixin, ArrowMixin, PointMixin, PathMixin):
    """Every shape sender, assembled in the order they were written."""


__all__ = ["ShapeMixin"]
