# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity
import numpy as np


class GrowArrow(Animation):
    def __init__(self, arrow, point_color=None, run_time=1.0, **kwargs):
        self.point_color = point_color
        self._orig_fill = None
        self._orig_stroke = None
        self._orig_stroke_width = None
        super().__init__(arrow, run_time=run_time, **kwargs)

    def begin(self, t):
        super().begin(t)
        mob = self.mobject
        self._grow_point = mob.get_start()

        if hasattr(mob, 'get_fill_rgbas'):
            try:
                frgbas = mob.get_fill_rgbas()
                if len(frgbas) > 0:
                    self._orig_fill = [float(frgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'get_stroke_rgbas'):
            try:
                srgbas = mob.get_stroke_rgbas()
                if len(srgbas) > 0:
                    self._orig_stroke = [float(srgbas[0][i]) for i in range(4)]
            except Exception:
                pass
        if hasattr(mob, 'stroke_width'):
            self._orig_stroke_width = mob.stroke_width

        mob._grow_scale = 0.0
        mob._grow_point = self._grow_point
        if self.point_color:
            self._pc = (self.point_color[0], self.point_color[1], self.point_color[2])
            mob.set_color(self.point_color)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        mob._grow_scale = alpha
        if self.point_color and self._orig_fill:
            fr, fg, fb = self._orig_fill[0], self._orig_fill[1], self._orig_fill[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
                mob.fill_rgbas[:, 0] = cr
                mob.fill_rgbas[:, 1] = cg
                mob.fill_rgbas[:, 2] = cb
        if self.point_color and self._orig_stroke:
            fr, fg, fb = self._orig_stroke[0], self._orig_stroke[1], self._orig_stroke[2]
            cr = self._pc[0] + (fr - self._pc[0]) * alpha
            cg = self._pc[1] + (fg - self._pc[1]) * alpha
            cb = self._pc[2] + (fb - self._pc[2]) * alpha
            if hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
                mob.stroke_rgbas[:, 0] = cr
                mob.stroke_rgbas[:, 1] = cg
                mob.stroke_rgbas[:, 2] = cb

    def finish(self):
        super().finish()
        mob = self.mobject
        if hasattr(mob, '_grow_scale'):
            del mob._grow_scale
        if hasattr(mob, '_grow_point'):
            del mob._grow_point
        if self._orig_fill and hasattr(mob, 'fill_rgbas') and len(mob.fill_rgbas) > 0:
            mob.fill_rgbas[:, 0] = self._orig_fill[0]
            mob.fill_rgbas[:, 1] = self._orig_fill[1]
            mob.fill_rgbas[:, 2] = self._orig_fill[2]
        if self._orig_stroke and hasattr(mob, 'stroke_rgbas') and len(mob.stroke_rgbas) > 0:
            mob.stroke_rgbas[:, 0] = self._orig_stroke[0]
            mob.stroke_rgbas[:, 1] = self._orig_stroke[1]
            mob.stroke_rgbas[:, 2] = self._orig_stroke[2]
        if self._orig_stroke_width is not None:
            try:
                mob.stroke_width = self._orig_stroke_width
            except Exception:
                pass
