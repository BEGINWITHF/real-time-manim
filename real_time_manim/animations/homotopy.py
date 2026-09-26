# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np


class Homotopy(Animation):
    def __init__(self, homotopy, mobject, run_time=3.0, **kwargs):
        self.homotopy = homotopy
        self._orig_points = {}
        super().__init__(mobject, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        mob._transforming = True
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                try:
                    self._orig_points[id(fm)] = fm.points.copy()
                except Exception:
                    pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        if not hasattr(mob, 'family_members_with_points'):
            return

        for fm in mob.family_members_with_points():
            if id(fm) not in self._orig_points:
                continue
            orig = self._orig_points[id(fm)]
            fm.points = orig.copy()
            for i in range(len(fm.points)):
                px, py, pz = orig[i][0], orig[i][1], orig[i][2]
                nx, ny, nz = self.homotopy(px, py, pz, alpha)
                fm.points[i][0] = nx
                fm.points[i][1] = ny
                fm.points[i][2] = nz

    def finish(self):
        super().finish()
        mob = self.mobject
        mob._transforming = False
        if hasattr(mob, 'family_members_with_points'):
            for fm in mob.family_members_with_points():
                if id(fm) in self._orig_points:
                    fm.points = self._orig_points[id(fm)].copy()
