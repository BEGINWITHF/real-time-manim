# This might not cause a bug or issue, check for other place first --TT Noted
import numpy as np

from real_time_manim.animations.grow_arrow import GrowArrow


class GrowFromPoint(GrowArrow):
    """Grow a mobject from an explicit world point.

    See :class:`GrowFromCenter`: colour/grow channels come from
    ``GrowArrow.begin`` (dicts), only the origin is overridden here.
    """

    def __init__(self, mobject, point, point_color=None, run_time=1.0, **kwargs):
        self._given_point = point
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        GrowArrow.begin(self, t)
        mob = self.mobject
        point = self._given_point
        if hasattr(point, 'get_center'):
            point = point.get_center()
        self._grow_point = np.array(point, dtype=float)
        mob._grow_point = self._grow_point
