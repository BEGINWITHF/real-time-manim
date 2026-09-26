# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np
from manim import YELLOW
from real_time_manim.rate_functions import _there_and_back


class Indicate(Animation):
    def __init__(self, mobject, scale_factor=1.2, color=YELLOW, rate_func=None, **kwargs):
        self.scale_factor = scale_factor
        self._indicate_color = color
        self._orig_fill = None
        self._orig_stroke = None
        kwargs.pop('run_time', None)
        super().__init__(mobject, run_time=1.0, rate_func=rate_func or _there_and_back, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        self._grow_point = mob.get_center()
        mob._grow_point = self._grow_point
        if hasattr(mob, 'family_members_with_points'):
            try:
                for fm in mob.family_members_with_points():
                    frgbas = fm.get_fill_rgbas()
                    if len(frgbas) > 0 and sum(frgbas[0][:3]) > 0:
                        self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
                        break
            except Exception:
                pass
        if hasattr(mob, 'family_members_with_points'):
            try:
                for fm in mob.family_members_with_points():
                    srgbas = fm.get_stroke_rgbas()
                    if len(srgbas) > 0 and sum(srgbas[0][:3]) > 0:
                        self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
                        break
            except Exception:
                pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        pulse = 1.0 + (self.scale_factor - 1.0) * alpha
        mob._fade_scale = pulse
        mob._grow_scale = pulse

        if self._indicate_color:
            ic = self._indicate_color
            for fm in mob.family_members_with_points():
                if self._orig_fill and hasattr(fm, 'fill_rgbas') and len(fm.fill_rgbas) > 0:
                    fr, fg, fb = self._orig_fill[0], self._orig_fill[1], self._orig_fill[2]
                    cr = fr + (float(ic[0]) - fr) * alpha
                    cg = fg + (float(ic[1]) - fg) * alpha
                    cb = fb + (float(ic[2]) - fb) * alpha
                    fm.fill_rgbas[:, 0] = cr
                    fm.fill_rgbas[:, 1] = cg
                    fm.fill_rgbas[:, 2] = cb
                if self._orig_stroke and hasattr(fm, 'stroke_rgbas') and len(fm.stroke_rgbas) > 0:
                    fr, fg, fb = self._orig_stroke[0], self._orig_stroke[1], self._orig_stroke[2]
                    cr = fr + (float(ic[0]) - fr) * alpha
                    cg = fg + (float(ic[1]) - fg) * alpha
                    cb = fb + (float(ic[2]) - fb) * alpha
                    fm.stroke_rgbas[:, 0] = cr
                    fm.stroke_rgbas[:, 1] = cg
                    fm.stroke_rgbas[:, 2] = cb

    def finish(self):
        super().finish()
        mob = self.mobject
        set_anim_opacity(mob, 1.0)
        if hasattr(mob, '_fade_scale'):
            del mob._fade_scale
        if hasattr(mob, '_grow_scale'):
            del mob._grow_scale
        if hasattr(mob, '_grow_point'):
            del mob._grow_point
        if self._orig_fill:
            for fm in mob.family_members_with_points():
                if hasattr(fm, 'fill_rgbas') and len(fm.fill_rgbas) > 0:
                    fm.fill_rgbas[:, 0] = self._orig_fill[0]
                    fm.fill_rgbas[:, 1] = self._orig_fill[1]
                    fm.fill_rgbas[:, 2] = self._orig_fill[2]
        if self._orig_stroke:
            for fm in mob.family_members_with_points():
                if hasattr(fm, 'stroke_rgbas') and len(fm.stroke_rgbas) > 0:
                    fm.stroke_rgbas[:, 0] = self._orig_stroke[0]
                    fm.stroke_rgbas[:, 1] = self._orig_stroke[1]
                    fm.stroke_rgbas[:, 2] = self._orig_stroke[2]

