# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, set_anim_opacity, get_anim_opacity, get_anim_rotation, set_anim_rotation
import numpy as np
import math
from real_time_manim.rate_functions import _smooth


class Rotate(Animation):
    def __init__(
        self,
        mobject,
        angle=math.pi,
        run_time=1.0,
        rate_func=None,
        about_point=None,
        **kwargs,
    ):
        self.rot_angle = angle
        self.about_point = about_point
        super().__init__(mobject, run_time=run_time, rate_func=rate_func or _smooth, **kwargs)

    def begin(self, t):
        super().begin(t)
        self._start_rotation = get_anim_rotation(self.mobject)
        if self.about_point is not None:
            self.mobject._rotation_about_point = np.array(self.about_point, dtype=float)

    def finish(self):
        super().finish()
        if hasattr(self.mobject, '_rotation_about_point'):
            del self.mobject._rotation_about_point

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        current = self._start_rotation + self.rot_angle * alpha
        set_anim_rotation(self.mobject, current)
