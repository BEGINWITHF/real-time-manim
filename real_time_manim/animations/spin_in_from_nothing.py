import math
from real_time_manim.animations.grow_from_center import GrowFromCenter


class SpinInFromNothing(GrowFromCenter):
    def __init__(self, mobject, angle=math.pi / 2, point_color=None, run_time=1.0, **kwargs):
        self._spin_angle = angle
        super().__init__(mobject, point_color=point_color, run_time=run_time, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        mob = self.mobject
        mob._grow_scale = alpha
        mob._grow_rot = self._spin_angle * alpha
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
        if hasattr(self.mobject, '_grow_rot'):
            del self.mobject._grow_rot
