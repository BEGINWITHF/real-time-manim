# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation


class ShowPassingFlash(Animation):
    def __init__(self, mobject, time_width=0.1, run_time=1.0, **kwargs):
        self.time_width = time_width
        super().__init__(mobject, run_time=run_time, remover=True, **kwargs)

    def begin(self, t):
        super().begin(t)
        self.mobject._vulkan_progress = 0.0

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)

        tw = self.time_width
        upper = (1 + tw) * alpha
        lower = upper - tw
        upper = min(upper, 1.0)
        lower = max(lower, 0.0)
        self.mobject._vulkan_progress_lower = lower
        self.mobject._vulkan_progress_upper = upper

    def finish(self):
        super().finish()
        self.mobject._vulkan_progress = 1.0

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        if self.mobject in scene.mobjects:
            scene.remove(self.mobject)
