"""Succession: animations played strictly one after another.

manim's ``Succession`` IS an ``AnimationGroup`` with ``lag_ratio=1``
(``animation/composition.py``), and RTM's own copy now is too.  It used to be
a standalone ``Animation`` with its own dispatch loop, which cost three wiki
gaps (``03-动画/组合编排/02-Succession顺序播放``):

* A13 -- ``lag_ratio`` was swallowed by ``**kwargs`` (the base even stored it,
  but the dispatch loop read nothing but cumulative child run_times), so a
  ``lag_ratio < 1`` overlap could never happen.
* A14 -- ``run_time`` was popped and discarded (``kwargs.pop('run_time')``);
  the total was pinned to the sum of the children's run_times.
* A30 -- the total was computed with builtin ``sum``, which on CPython >= 3.12
  uses compensated float summation: ``sum([1.0, 1.0, 0.6, 0.8])`` gives
  ``3.4`` where manim's ``np.add.accumulate`` gives ``3.4000000000000004``,
  and that whole frame is the wiki's "294 vs 295 frames" (the count comes
  from ``np.arange(0, run_time, 1/60)``, which is 204 for 3.4 and 205 for
  3.4000000000000004).  The group's schedule accumulates naively now, which
  lands on CE's side of the boundary.

Delegating to ``AnimationGroup`` also inherits its fixes: ``_group_start``
seconds-based staggering (CE's ``start[i+1] = start[i] + run_time[i] *
lag_ratio``), the run_time-vs-children-span split, the three-convention
``interpolate`` dispatch and the ``clean_up_from_scene`` recursion.
"""
from real_time_manim.animations.animation_group import AnimationGroup
from real_time_manim.rate_functions import _linear


class Succession(AnimationGroup):
    """Play animations in order; ``lag_ratio=1`` (100%) by default.

    ``lag_ratio`` below 1 makes the next animation start before the previous
    one has finished (CE semantics).  ``run_time`` (keyword, ``None`` =
    automatic) stretches or compresses the whole serial schedule onto that
    total.  ``rate_func`` defaults to ``linear``, as manim's does.
    """

    def __init__(self, *animations, lag_ratio=1, rate_func=None, **kwargs):
        # ``rate_func=None`` means "unset"; anything callable passes through
        # (the old standalone class did ``rate_func or _linear``).
        super().__init__(
            *animations,
            lag_ratio=lag_ratio,
            rate_func=rate_func if rate_func is not None else _linear,
            **kwargs,
        )
