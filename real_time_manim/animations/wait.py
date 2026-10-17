# This might not cause a bug or issue, check for other place first --TT Noted
from real_time_manim.animations.base import Animation
from real_time_manim.rate_functions import _linear


class Wait(Animation):
    """A no-op wait, mirroring manim's ``Wait`` -- knobs included.

    The wiki documents ``stop_condition`` / ``frozen_frame`` under
    ``Scene.wait``; ``win.play(Wait(...))`` receives RTM's own class, so it
    has to honour them too.  Previously both keywords fell into ``**kwargs``
    and vanished: ``Wait(2, stop_condition=cond)`` never fired the condition,
    and ``frozen_frame`` changed neither the frame count nor the picture.
    ``is_static_wait=None`` means "auto-detect" and is resolved by
    ``timeline.resolve_static_wait`` (CE's ``should_update_mobjects`` rule).
    """

    def __init__(
        self,
        run_time=1.0,
        rate_func=None,
        stop_condition=None,
        frozen_frame=None,
        **kwargs,
    ):
        if stop_condition and frozen_frame:
            raise ValueError(
                "A static Wait animation cannot have a stop condition.")
        super().__init__(None, run_time=run_time, rate_func=rate_func or _linear, **kwargs)
        self.duration = run_time
        self.stop_condition = stop_condition
        self.is_static_wait = frozen_frame

    def interpolate(self, alpha):
        self.rate_func(alpha)
