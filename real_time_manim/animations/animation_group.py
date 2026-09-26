from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
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
        super().__init__(run_time=total, **kwargs)
        self._begun = set()

    def begin(self, t=None):
        if t is None:
            import time as _time
            t = _time.time()
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        total = self.run_time
        if t < 100.0:
            group_time = self.rate_func(t) * total if total > 0 else 0.0
        else:
            elapsed = t - self.start_time
            if total > 0:
                raw_alpha = max(0.0, min(1.0, elapsed / total))
                group_time = self.rate_func(raw_alpha) * total
            else:
                group_time = elapsed

        for i, a in enumerate(self.animations):
            a_start = getattr(a, '_group_start', 0.0)
            a_end = a_start + a.run_time
            is_manim = type(a).__module__.startswith('manim')

            if group_time >= a_start and group_time < a_end:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t if t >= 100.0 else time.time())
                    self._begun.add(i)
                sub_alpha = (group_time - a_start) / a.run_time if a.run_time > 0 else 1.0
                sub_alpha = max(0.0, min(1.0, sub_alpha))
                if is_manim:
                    a.interpolate(sub_alpha)
                else:
                    a._use_alpha = True
                    a.interpolate(sub_alpha)
            elif group_time >= a_end:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t if t >= 100.0 else time.time())
                    self._begun.add(i)
                if is_manim:
                    a.interpolate(1.0)
                else:
                    a._use_alpha = True
                    a.interpolate(1.0)

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
