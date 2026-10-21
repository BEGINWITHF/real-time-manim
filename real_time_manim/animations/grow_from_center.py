# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.grow_arrow import GrowArrow
from real_time_manim.animations.base import resolve_mobject


class GrowFromCenter(GrowArrow):
    """Grow a mobject from its own centre.

    The fill/stroke bookkeeping lives in :meth:`GrowArrow.begin` /
    :meth:`GrowArrow.finish` alone.  This class used to keep its own
    ``_orig_fill`` / ``_orig_stroke`` as **lists** while the inherited
    ``GrowArrow.finish`` read them as **dicts** keyed by ``id(sub)``, so any
    filled mobject crashed at clean-up with
    ``AttributeError: 'list' object has no attribute 'get'`` -- and the same
    list was fed to ``GrowArrow.interpolate``'s ``.get`` when ``point_color``
    was set, crashing mid-animation.  Delegate the whole colour/grow channel
    setup to the parent and only override the grow ORIGIN.

    ``GrowArrow`` names its first argument ``arrow``; CE's name is ``mobject``,
    so both spellings are accepted here.
    """

    def __init__(self, mobject=None, point_color=None, run_time=1.0, **kwargs):
        if mobject is None and "arrow" in kwargs:
            mobject = kwargs.pop("arrow")
        mobject = resolve_mobject(mobject, kwargs, "GrowFromCenter", alias=None)
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def begin(self, t):
        GrowArrow.begin(self, t)
        mob = self.mobject
        self._grow_point = mob.get_center()
        mob._grow_point = self._grow_point
