import math

from real_time_manim.animations.grow_arrow import GrowArrow
from real_time_manim.animations.grow_from_center import GrowFromCenter


class SpinInFromNothing(GrowFromCenter):
    """Grow from the centre while spinning in.

    ``_grow_rot`` is a per-frame draw channel, so it has to be *deleted* when
    the animation ends or the mobject stays rotated forever (the play path now
    calls ``finish()`` for RTM animations; see ``window/play.py``).  Colour
    bookkeeping is the parent chain's (``GrowFromCenter`` -> ``GrowArrow``),
    which uses ``id(sub)``-keyed dicts.
    """

    def __init__(self, mobject, angle=math.pi / 2, point_color=None, run_time=1.0, **kwargs):
        self._spin_angle = angle
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def interpolate(self, t):
        GrowArrow.interpolate(self, t)
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        self.mobject._grow_rot = self._spin_angle * alpha

    def finish(self):
        super().finish()
        if hasattr(self.mobject, '_grow_rot'):
            del self.mobject._grow_rot
