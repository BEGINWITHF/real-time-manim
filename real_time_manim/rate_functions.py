import math


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def _smooth(t, inflection=10.0):
    error = _sigmoid(-inflection / 2)
    val = (_sigmoid(inflection * (t - 0.5)) - error) / (1 - 2 * error)
    return max(0.0, min(1.0, val))


def _linear(t):
    return t


def _rush_into(t, inflection=10.0):
    return 2.0 * _smooth(t / 2.0, inflection)


def _rush_from(t, inflection=10.0):
    return 2.0 * _smooth(t / 2.0 + 0.5, inflection) - 1.0


def _there_and_back(t, inflection=10.0):
    if t < 0.5:
        new_t = 2.0 * t
    else:
        new_t = 2.0 * (1.0 - t)
    return _smooth(new_t, inflection)


def _slow_into(t):
    return math.sqrt(1.0 - (1.0 - t) * (1.0 - t))


def _double_smooth(t):
    if t < 0.5:
        return 0.5 * _smooth(2.0 * t)
    else:
        return 0.5 * (1.0 + _smooth(2.0 * t - 1.0))


def _wiggle(t, wiggles=2):
    val = math.sin(wiggles * math.pi * t)
    return _there_and_back(t) * val


def _lingering(t):
    return _squish_rate_func(lambda x: x, 0, 0.8)(t)


def _exponential_decay(t, half_life=0.1):
    return 1.0 - math.exp(-t / half_life)


def _squish_rate_func(func, a, b):
    def result(t):
        return func((t - a) / (b - a))
    return result


# ManimCE's public rate functions ride along, so ``real_time_manim``'s own
# ``rate_functions`` module is a superset of the upstream one:
# ``rate_functions.smooth`` works whether the caller came from RTM's internals
# (which use the ``_``-prefixed copies above) or from user code that just wants
# ``from real_time_manim import rate_functions``.
# ``real_time_manim/__init__`` binds this module under the name ``rate_functions``
# so it never collides with the copy re-exported by the bundled ManimCE.
from manim.utils.rate_functions import *   # noqa: F401,F403
from manim.utils.rate_functions import __dict__ as _manim_rate_functions_dict

__all__ = [name for name in _manim_rate_functions_dict if not name.startswith("_")]
