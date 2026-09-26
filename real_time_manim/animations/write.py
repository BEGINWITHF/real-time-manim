# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.draw_border_then_fill import DrawBorderThenFill
from real_time_manim.rate_functions import _linear


class Write(DrawBorderThenFill):
    def __init__(self, mobject, rate_func=_linear, reverse=False, run_time=None,
                 lag_ratio=None, **kwargs):
        self.reverse = reverse
        if "remover" not in kwargs:
            kwargs["remover"] = reverse
        length = 1
        if hasattr(mobject, 'submobjects'):
            length = max(1, len(mobject.submobjects))
        if run_time is None:
            run_time = 1.0 if length < 15 else 2.0
        if lag_ratio is None:
            lag_ratio = min(4.0 / max(1.0, length), 0.2)
        super().__init__(mobject, run_time=run_time, rate_func=rate_func,
                         introducer=not reverse, **kwargs)
        self.lag_ratio = lag_ratio

    def begin(self, t):
        if self.reverse:
            if hasattr(self.mobject, 'invert'):
                self.mobject.invert(recursive=True)
        super().begin(t)

    def finish(self):
        super().finish()
        if self.reverse:
            if hasattr(self.mobject, 'invert'):
                self.mobject.invert(recursive=True)
