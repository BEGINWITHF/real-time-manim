# -*- coding: utf-8 -*-
"""`path_center` / `path_extent` must equal manim's own critical points.

The senders used to call `mob.get_center()` / `get_bottom()` / `get_top()`, each
of which chains every family member's bezier ANCHORS into a Python tuple, turns
it back into an array, and repeats that per dimension (~98 us for a Text root,
~191 us for bottom+top; measured).  The helpers compute the same bounds from the
same strided slices in place, so every caller can swap them in without moving a
pixel -- which is what this pins, on the values the callers actually read.

Pure Python: no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from real_time_manim import Circle, Square, Text               # noqa: E402
from real_time_manim.render.util import path_center, path_extent  # noqa: E402


def _samples():
    txt = Text("bench", font_size=24)
    mobs = [Square(), Circle(), Square(side_length=2.0).shift([1.3, -2.1, 0]),
            Circle(radius=0.37).shift([-2.0, 1.0, 0]), txt]
    mobs.extend(txt.submobjects)                 # glyphs: a family of their own
    return mobs


def test_center_matches_get_center():
    for mob in _samples():
        assert tuple(path_center(mob)) == tuple(mob.get_center()), mob


def test_extent_matches_get_bottom_and_get_top():
    for mob in _samples():
        lo, hi = path_extent(mob)
        assert lo[1] == mob.get_bottom()[1], mob       # the y the callers read
        assert hi[1] == mob.get_top()[1], mob


def test_extent_is_none_without_points_and_center_falls_back():
    from real_time_manim import Mobject

    empty = Mobject()
    assert path_extent(empty) is None
    assert tuple(path_center(empty)) == tuple(empty.get_center())


def test_moving_a_mobject_moves_the_extent():
    # The helpers must not be a stale snapshot of anything: moving the mobject
    # (which is all an animation does) has to show up immediately.
    sq = Square()
    lo0, hi0 = path_extent(sq)
    sq.shift([3.0, 1.0, 0.0])
    lo1, hi1 = path_extent(sq)
    assert lo1[0] == lo0[0] + 3.0 and hi1[1] == hi0[1] + 1.0
    assert tuple(path_center(sq)) == tuple(sq.get_center())
