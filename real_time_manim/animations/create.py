# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation


class Create(Animation):
    def __init__(self, mobject, run_time=1.0, lag_ratio=1.0, **kwargs):
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio, **kwargs)

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        self.mobject._vulkan_progress = alpha