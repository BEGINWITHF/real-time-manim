from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
from real_time_manim.rate_functions import _linear

# ``begin()`` with no argument stamps ``time.time()`` (seconds since 1970), so
# a start_time this large means "wall clock", not "seconds into the play".
_WALL_CLOCK_MIN = 1.0e6
import time
import numpy as np
from manim.mobject.mobject import _AnimationBuilder
from real_time_manim.animations.wait import Wait
from real_time_manim.animations.fade_in import FadeIn
from real_time_manim.animations.fade_out import FadeOut
from real_time_manim.animations.transform import Transform


class AnimationGroup(Animation):
    def __init__(self, *animations, lag_ratio=0.0, **kwargs):
        from manim.mobject.mobject import _AnimationBuilder
        resolved = []
        for a in animations:
            if isinstance(a, _AnimationBuilder):
                resolved.append(a.build())
            else:
                resolved.append(a)
        self.animations = resolved
        self.lag_ratio = lag_ratio
        for i, a in enumerate(self.animations):
            a._group_start = i * lag_ratio
        total_runs = [a._group_start + a.run_time for a in self.animations]
        total = max(total_runs) if total_runs else 0
        # manim's AnimationGroup defaults to rate_func=linear; the shared
        # Animation base defaults to smooth, which would ease the whole group
        # *on top of* every child's own easing -- a staggered FadeIn group then
        # runs off CE's clock (measured: first child at 0.06 where CE has 0.5).
        kwargs.setdefault('rate_func', _linear)
        super().__init__(run_time=total, **kwargs)
        self._begun = set()

    def begin(self, t=None):
        if t is None:
            import time as _time
            t = _time.time()
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        """Step every child to its state at time ``t``.

        Three callers, three conventions, and this class has to tell them
        apart itself:

        * the timeline passes **elapsed seconds** with ``start_time`` pinned to
          0 (``timeline.evaluate_animation``);
        * the live path passes a **wall-clock stamp**, as ``begin()`` records;
        * a manim wrapper passes manim's **normalised alpha** while our own
          ``start_time`` is still whatever ``begin()`` defaulted to --
          ``ChangeSpeed.interpolate`` does exactly
          ``self.anim.interpolate(alpha)``, and scene 59 wraps a group that
          way.

        Children are then stepped in absolute time, the way ``Succession``
        always has: RTM's animations read ``(t - start_time) / run_time``
        themselves, so handing them a normalised alpha against a wall-clock
        ``start_time`` clamped to 0 for every animation that does not opt into
        ``_use_alpha`` -- ``AnimationGroup(Create(...))`` drew nothing at all.

        The old ``t < 100`` test conflated the first and the third case, so
        the timeline's *seconds* were read as an alpha: a 2.5 s group ran its
        whole schedule inside 1.0 s and the rest of the play was frozen.
        """
        total = float(self.run_time or 0.0)
        # A wall-clock origin can only be outrun by a wrapper's alpha (0..1);
        # a time, by contrast, is never below the origin it is measured from.
        from_wrapper = self.start_time > _WALL_CLOCK_MIN and t < self.start_time
        raw = t if from_wrapper else (
            (t - self.start_time) / total if total > 0 else 0.0)
        group_time = self.rate_func(max(0.0, min(1.0, raw))) * total if total > 0 else 0.0
        origin = self.start_time

        for i, a in enumerate(self.animations):
            a_start = getattr(a, '_group_start', 0.0)
            if group_time < a_start:
                continue
            is_manim = type(a).__module__.startswith('manim')
            if i not in self._begun:
                if is_manim:
                    a.begin()                       # manim's takes no time
                else:
                    a.begin(origin + a_start)
                    # Whatever an earlier grouping set is now wrong: RTM
                    # children are driven in absolute time, not handed a
                    # normalised alpha.
                    a._use_alpha = False
                self._begun.add(i)
            if is_manim:
                sub_alpha = (group_time - a_start) / a.run_time if a.run_time > 0 else 1.0
                a.interpolate(max(0.0, min(1.0, sub_alpha)))
            else:
                # past a_end this clamps to the child's final state
                a.interpolate(origin + group_time)

    def finish(self):
        super().finish()
        for a in self.animations:
            a.finish()

    def get_all_mobjects(self):
        mobs = []
        for a in self.animations:
            mobs.extend(a.get_all_mobjects())
        return mobs

    def get_all_families_zipped(self):
        families = []
        for a in self.animations:
            families.extend(a.get_all_families_zipped())
        return families
