import math
import numpy as np
from functools import partialmethod
from manim import VGroup, Group, Rectangle, Circle, YELLOW, Text

TAU = 2.0 * math.pi
from real_time_manim.rate_functions import (
    _smooth, _linear, _double_smooth, _there_and_back,
)

# Shared state/helpers live in real_time_manim.state (so the renderer no longer
# depends on this package); re-exported here so existing imports keep working.
from real_time_manim.state import (
    DEFAULT_ANIMATION_RUN_TIME,
    DEFAULT_ANIMATION_LAG_RATIO,
    TARGET_FPS,
    FRAME_DURATION,
    set_anim_opacity,
    get_anim_opacity,
    set_anim_rotation,
    get_anim_rotation,
    set_anim_rotation_delta,
    get_anim_rotation_delta,
    clear_anim_rotation_delta,
)


class Animation:
    _original__init__ = None

    def __init__(
        self,
        mobject=None,
        lag_ratio=DEFAULT_ANIMATION_LAG_RATIO,
        run_time=DEFAULT_ANIMATION_RUN_TIME,
        rate_func=None,
        reverse_rate_function=False,
        name=None,
        remover=False,
        suspend_mobject_updating=True,
        introducer=False,
        **kwargs,
    ):
        self.mobject = mobject
        self.lag_ratio = lag_ratio
        self._run_time = run_time
        self.rate_func = rate_func if rate_func is not None else _smooth
        self.reverse_rate_function = reverse_rate_function
        self.name = name
        self.remover = remover
        self.suspend_mobject_updating = suspend_mobject_updating
        self.introducer = introducer
        self.start_time = 0.0
        self.finished = False

    @classmethod
    def set_default(cls, **kwargs):
        if cls._original__init__ is None:
            cls._original__init__ = cls.__init__
        if kwargs:
            cls.__init__ = partialmethod(cls.__init__, **kwargs)
        else:
            cls.__init__ = cls._original__init__

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '_original__init__' not in cls.__dict__:
            cls._original__init__ = cls.__init__

    @property
    def run_time(self):
        return self._run_time

    @run_time.setter
    def run_time(self, value):
        self._run_time = value

    def __str__(self):
        return self.name or f"{type(self).__name__}({self.mobject})"

    def __repr__(self):
        return self.__str__()

    def begin(self, t=None):
        if t is None:
            import time as _time
            t = _time.time()
        self.start_time = t

    def finish(self):
        self.finished = True

    def interpolate(self, t):
        alpha = (t - self.start_time) / self.run_time if self.run_time > 0 else 1.0
        alpha = max(0.0, min(1.0, alpha))
        if self.reverse_rate_function:
            alpha = 1.0 - alpha
        self.interpolate_mobject(alpha)

    def interpolate_mobject(self, alpha):
        pass

    def get_sub_alpha(self, alpha, index, num_submobjects):
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        raw_sub_alpha = max(0.0, min(1.0, value - lower))
        return self.rate_func(raw_sub_alpha)

    def set_rate_func(self, func):
        self.rate_func = func

    def clean_up_from_scene(self, scene):
        pass

    def get_all_mobjects(self):
        if self.mobject is not None:
            return [self.mobject]
        return []
