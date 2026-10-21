# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.grow_arrow import GrowArrow


class GrowFromEdge(GrowArrow):
    """Grow a mobject from one of its critical points.

    See :class:`GrowFromCenter`: the colour/grow channels are the parent's
    (``GrowArrow.begin`` builds ``_orig_fill`` / ``_orig_stroke`` as dicts so
    ``GrowArrow.finish`` works), and only the origin differs.
    """

    def __init__(self, mobject, edge, point_color=None, run_time=1.0, **kwargs):
        self.edge = edge
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        GrowArrow.begin(self, t)
        mob = self.mobject
        self._grow_point = mob.get_critical_point(self.edge)
        mob._grow_point = self._grow_point
