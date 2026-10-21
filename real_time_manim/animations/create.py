# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation, resolve_mobject


class Create(Animation):
    def __init__(self, mobject=None, run_time=1.0, lag_ratio=1.0, **kwargs):
        mobject = resolve_mobject(mobject, kwargs, "Create")
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio, **kwargs)

    def begin(self, t):
        super().begin(t)
        # The native sender splits one container progress across its children
        # using a HARD-CODED lag ratio of 1.0 before this fix, so
        # ``Create(vgroup, lag_ratio=0.0)`` was pixel-identical to
        # ``lag_ratio=1.0``.  Stamp the animation's own ``lag_ratio`` on the
        # mobject for the paint walk (``window/paint.py``) and let
        # ``release_split`` clear it when the play ends.
        try:
            self.mobject._vulkan_lag_ratio = float(self.lag_ratio)
        except Exception:
            pass

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        alpha = self.rate_func(alpha)
        try:
            self.mobject._vulkan_lag_ratio = float(self.lag_ratio)
        except Exception:
            pass
        self.mobject._vulkan_progress = alpha
