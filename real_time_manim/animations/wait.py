# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation
from real_time_manim.rate_functions import _linear


class Wait(Animation):
    def __init__(
        self,
        run_time=1.0,
        rate_func=None,
        **kwargs,
    ):
        super().__init__(None, run_time=run_time, rate_func=rate_func or _linear, **kwargs)

    def interpolate(self, alpha):
        self.rate_func(alpha)
