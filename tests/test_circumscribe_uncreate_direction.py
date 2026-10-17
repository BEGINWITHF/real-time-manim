"""Regression: ``Circumscribe(fade_in=True)`` un-creates the frame BACKWARD.

Report: wiki ``03-动画/强调与提示`` ``assets/RTM output/02-圈注与聚焦.mp4``
-- "圆形uncreate方向错误，聚焦动画播放错误".

ManimCE's ``Circumscribe.__init__`` calls ``frame.reverse_direction()`` in
its ``elif fade_in:`` branch, before building
``Succession(FadeIn(frame), Uncreate(frame))``, so the closing ``Uncreate``
erases the circle BACKWARD -- from where the fade-in ended.  RTM's copy
(``real_time_manim/animations/circumscribe.py``) did not reverse anything,
so its ``Uncreate`` ate the circle from the opposite end.

Measured on that clip at f300 (Uncreate at ~0.69 of its window): the signed
(RTM - CE) luma map had RTM-only ink along the top and upper-right arc
(3 o'clock -> 12 o'clock, the PREFIX of a non-reversed path) and CE-only ink
on the lower right (3 o'clock -> ~5:47), which is the prefix of the reversed
one -- the two rings were mirror images about the 3 o'clock radius.  Both
engines agree on how much of the circle is left; only the SIDE differed.

FIXED: ``real_time_manim/animations/circumscribe.py`` now calls
``frame.reverse_direction()`` in that branch, exactly like CE, so
``test_fade_in_reverses_the_frame_like_manim_ce`` -- formerly ``xfail`` --
passes and guards the fix.
"""

import os
import sys

import numpy as np
import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import Circle, Square  # noqa: E402

from real_time_manim.vulkan_bind import Circumscribe  # noqa: E402


def _turn_sign(points):
    """Sign of the second difference: which way the contour runs."""
    a = np.asarray(points, dtype=float)
    v1 = a[1][:2] - a[0][:2]
    v2 = a[2][:2] - a[1][:2]
    cross = float(v1[0] * v2[1] - v1[1] * v2[0])
    return 1.0 if cross >= 0 else -1.0


def test_a_plain_circle_and_a_circumscribe_frame_run_the_same_way():
    """Non-regression: ``fade_out`` (the Create half) must NOT be reversed."""
    cs = Circumscribe(Square(side_length=1.0), shape=Circle, fade_out=True,
                      run_time=1.0)
    assert _turn_sign(cs._frame.points) == _turn_sign(Circle().points)


def test_fade_in_reverses_the_frame_like_manim_ce():
    cs = Circumscribe(Square(side_length=1.0), shape=Circle, fade_in=True,
                      run_time=1.0)
    assert _turn_sign(cs._frame.points) == -_turn_sign(Circle().points)
