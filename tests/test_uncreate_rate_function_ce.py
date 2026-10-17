"""Regression: ``Uncreate`` must unwind like manim CE -- eased, not linear.

Report: wiki ``03-动画/强调与提示`` ``assets/RTM output/02-圈注与聚焦.mp4``
-- "圆形uncreate方向错误，聚焦动画播放错误" (the closing half of
``Circumscribe(fade_in=True)`` is an ``Uncreate``), plus its sibling page
``03-动画/创建与擦除`` ``02-反向擦除`` which plays ``Uncreate`` on its own.

Root cause
----------
manim CE (``manim/animation/creation.py``)::

    class Uncreate(Create):
        def __init__(self, mobject, reverse_rate_function=True, remover=True,
                     **kwargs):
            super().__init__(mobject,
                             reverse_rate_function=reverse_rate_function,
                             introducer=False, remover=remover, **kwargs)

so the default ``rate_func`` stays ``Animation``'s **smooth**, and CE applies
it reversed in ``Animation.get_sub_alpha``::

    if self.reverse_rate_function:
        return self.rate_func(1 - (value - lower))

=> effective progress ``smooth(1 - t)``.  RTM used to hard-code
``rate_func=lambda t: 1.0 - t`` -- a *linear* unwind -- which (a) does not
ease like CE and (b) could not be overridden by ``reverse_rate_function``.

Fix
---
``real_time_manim/animations/uncreate.py`` now forwards
``reverse_rate_function=True`` (CE's default) and leaves ``rate_func`` at the
base ``Animation`` default ``_smooth``.  ``Create.interpolate`` already
computes ``rate_func(1 - alpha)`` for that flag, i.e. exactly CE's formula.

Measured
--------
``Uncreate(Circle())._vulkan_progress`` at t = 0.0 / 0.25 / 0.5 / 0.75 / 1.0
is 1.000 / 0.891 / 0.500 / 0.109 / 0.000 (= ``smooth(1 - t)``); before the fix
it was 1.000 / 0.750 / 0.500 / 0.250 / 0.000 (linear).  Endpoints are
unchanged, so no caller sees a half-drawn shape at the start or a leftover
outline at the end.
"""

import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Circle  # noqa: E402

from real_time_manim.rate_functions import _smooth  # noqa: E402
from real_time_manim.vulkan_bind import Uncreate  # noqa: E402


def _progress_at(anim, t):
    """``_vulkan_progress`` after animating to wall-clock time ``t``."""
    anim.begin(0.0)
    anim.interpolate(t)
    return float(anim.mobject._vulkan_progress)


def test_uncreate_reverses_via_reverse_rate_function_like_ce():
    """CE's ``Uncreate`` sets ``reverse_rate_function=True`` by default."""
    anim = Uncreate(Circle())
    assert anim.reverse_rate_function is True
    # and it must NOT smuggle in a linear rate function the way it used to
    # (``rate_func = lambda t: 1.0 - t``).
    for t in (0.13, 0.37, 0.61, 0.83):
        assert _progress_at(Uncreate(Circle()), t) == pytest.approx(
            _smooth(1.0 - t), abs=1e-9)


def test_uncreate_curve_is_smooth_not_linear():
    """The old implementation was linear; CE's is eased -- they must differ."""
    mid = _progress_at(Uncreate(Circle()), 0.25)
    assert mid == pytest.approx(_smooth(0.75), abs=1e-9)
    # smooth(0.75) ~= 0.89 vs the linear 0.75 -- a real, visible difference.
    assert abs(mid - 0.75) > 0.1


def test_uncreate_starts_fully_drawn_and_ends_erased():
    """No regression on the endpoints: full shape at t=0, nothing left at t=1."""
    assert _progress_at(Uncreate(Circle()), 0.0) == pytest.approx(1.0, abs=1e-9)
    assert _progress_at(Uncreate(Circle()), 1.0) == pytest.approx(0.0, abs=1e-9)


def test_explicit_rate_func_is_kept_and_still_reversed():
    """``Uncreate(m, rate_func=...)`` keeps the caller's curve, CE-style."""
    from real_time_manim.rate_functions import _linear

    anim = Uncreate(Circle(), rate_func=_linear)
    assert anim.reverse_rate_function is True
    # linear reversed == the old hard-coded ``1 - t`` behaviour
    assert _progress_at(anim, 0.3) == pytest.approx(0.7, abs=1e-9)


def test_reverse_rate_function_can_be_switched_off():
    """CE forwards ``reverse_rate_function`` through ``**kwargs``; so do we."""
    anim = Uncreate(Circle(), reverse_rate_function=False)
    assert anim.reverse_rate_function is False
    assert _progress_at(anim, 0.3) == pytest.approx(_smooth(0.3), abs=1e-9)
