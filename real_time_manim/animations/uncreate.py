# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.create import Create


class Uncreate(Create):
    def __init__(self, mobject, run_time=1.0, lag_ratio=1.0, remover=True,
                 rate_func=None, **kwargs):
        if rate_func is None:
            rate_func = lambda t: 1.0 - t
        super().__init__(mobject, run_time=run_time, lag_ratio=lag_ratio,
                         remover=remover, rate_func=rate_func, **kwargs)
