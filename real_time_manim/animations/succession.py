# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim.mobject.mobject import _AnimationBuilder
from real_time_manim.animations.wait import Wait


class Succession(Animation):
    def __init__(self, *animations, rate_func=None, **kwargs):
        from manim.mobject.mobject import _AnimationBuilder
        resolved = []
        for a in animations:
            if isinstance(a, _AnimationBuilder):
                resolved.append(a.build())
            else:
                resolved.append(a)
        self.animations = resolved
        total = sum(a.run_time for a in self.animations)
        kwargs.pop('run_time', None)
        super().__init__(run_time=total, rate_func=rate_func, **kwargs)
        self._begun = set()

    def begin(self, t):
        super().begin(t)
        self._begun = set()

    def interpolate(self, t):
        elapsed = t - self.start_time
        total = self.run_time
        if total > 0:
            raw_alpha = max(0.0, min(1.0, elapsed / total))
            mapped_alpha = self.rate_func(raw_alpha)
            elapsed = mapped_alpha * total
        cumulative = 0.0
        for i, a in enumerate(self.animations):
            end = cumulative + a.run_time
            is_manim = type(a).__module__.startswith('manim')
            if a.run_time > 0:
                active = elapsed >= cumulative and elapsed < end
            else:
                active = elapsed >= cumulative and i not in self._begun
            if active:
                if i not in self._begun:
                    if is_manim:
                        a.begin()
                    else:
                        a.begin(t)
                    self._begun.add(i)
                if is_manim:
                    sub_alpha = (elapsed - cumulative) / a.run_time if a.run_time > 0 else 1.0
                    sub_alpha = max(0.0, min(1.0, sub_alpha))
                    a.interpolate(sub_alpha)
                else:
                    a.interpolate(t)
                return
            cumulative = end
        if self.animations:
            last_idx = len(self.animations) - 1
            if last_idx not in self._begun:
                is_manim = type(self.animations[last_idx]).__module__.startswith('manim')
                if is_manim:
                    self.animations[last_idx].begin()
                else:
                    self.animations[last_idx].begin(t)
                self._begun.add(last_idx)
            is_manim = type(self.animations[last_idx]).__module__.startswith('manim')
            if is_manim:
                self.animations[last_idx].interpolate(1.0)
            else:
                self.animations[last_idx].interpolate(t)

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
