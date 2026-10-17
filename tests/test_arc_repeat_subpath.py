"""An open arc must never be bridged by a chord when its points repeat.

Report: wiki ``02-Mobject通用/04b-缩放旋转与变形-进阶``
``04b-缩放旋转与变形-进阶-repeat_rev.mp4`` -- "错误的在红花结束时将arc补成封闭图形".

Root cause
----------
``real_time_manim/render/shapes/paths.py::_stroke_points_polyline`` tessellated
the WHOLE point array as one continuous cubic run and, for every cubic after
the first, dropped its first sample ("the shared endpoint is not repeated").
That assumption breaks wherever two consecutive curves do not share an anchor:
the skipped anchor and the previous curve's end then become one straight EDGE
of the polyline, i.e. a chord.

The sample does ``arc.reverse_points()`` then ``arc.repeat(2)``, and manim's
``VMobject.repeat`` appends a second copy of the points
(``np.append(a1, a2)``), so curve 8 starts at the arc's START while curve 7
ended at its END.  CE does not bridge that gap: ``Camera`` splits the path with
``vmobject.get_subpath_split_indices_from_points(points, n_dims=2)`` and emits
``ctx.new_sub_path()`` + ``move_to`` per run
(``camera/camera.py:715-760``).

Fix
---
``_stroke_points_subpaths`` splits the tessellation at exactly those anchors
(same tolerance rule as CE: ``consider_points_equals_2d``, i.e. ``rtol 1e-5`` /
``atol tolerance_for_point_equality``) and ``_send_arc`` strokes one polyline
per subpath, cutting the global progress window across them the way
``_send_polygon`` already does for a Polygram's vertex groups.

Measurement
-----------
Before the fix, driving ``Arc(radius=1.5, start_angle=0, angle=TAU*0.7)`` plus
``repeat(2)`` through ``_send_arc`` (960x540, stub DLL) emitted ONE
``AddLineStrip`` per width layer whose longest step between consecutive
samples was **165.5 px** -- (448.7, 366.3) -> (581.3, 270.0), the chord that
closes the 252 deg arc.  The wiki diff against the CE twin measured exactly
that chord: 171 differing pixels in bbox x[224..290] y[134..182] (480x270),
peak 208, 0 px on frames 0-29 (before ``repeat``) and 171 px from frame 30 on.

After the fix: two runs of 153 samples each (the arc drawn twice, exactly as
CE draws two subpaths), longest step **2.9 px** -- the plain tessellation step
of the curve itself.

Run with::

    python -X utf8 -m pytest tests/test_arc_repeat_subpath.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

from manim import Arc, TAU

from real_time_manim import camera_state
from real_time_manim.render.shapes import ShapeMixin


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Sender(ShapeMixin):
    """A ShapeMixin host with no window behind it (pure coordinate tests)."""

    win_w, win_h = 960, 540

    def __init__(self):
        self.dll = _Recorder()

    @staticmethod
    def _dbg_emit(*args, **kwargs):                     # pragma: no cover
        pass


@pytest.fixture(autouse=True)
def _flat_camera():
    """Neutral viewport, restored afterwards (the tooling shares this state)."""
    prev = camera_state.get_viewport()
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(prev)


def _strips(calls):
    out = []
    for name, a in calls:
        if name != "AddLineStrip":
            continue
        coords, n = a[0], int(a[2])
        pts = [(float(coords[i * 2]), float(coords[i * 2 + 1]))
               for i in range(n)]
        out.append(pts)
    return out


def _longest_step(pts):
    """Longest jump between consecutive points of an (x, y) pair list."""
    return max(((pts[i + 1][0] - pts[i][0]) ** 2
                + (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
               for i in range(len(pts) - 1))


def _longest_step_flat(flat):
    """Same for a ``x0,y0,x1,y1,...`` run, which is what the tessellator emits."""
    return max(((flat[i + 2] - flat[i]) ** 2
                + (flat[i + 3] - flat[i + 1]) ** 2) ** 0.5
               for i in range(0, len(flat) - 2, 2))


def _arc():
    return Arc(radius=1.5, start_angle=0, angle=TAU * 0.7, color="yellow")


def test_repeat_splits_the_arc_into_two_runs():
    """The repeated point array yields two open runs, no bridging chord."""
    sender = _Sender()
    arc = _arc()
    before = sender._stroke_points_subpaths(
        arc.get_points(), 960, 540, None, 0.0, 480.0, 270.0, arc)
    assert len(before) == 1, "a plain Arc must stay ONE subpath"

    arc.repeat(2)
    runs = sender._stroke_points_subpaths(
        arc.get_points(), 960, 540, None, 0.0, 480.0, 270.0, arc)
    assert len(runs) == 2, (
        "repeat(2) must produce two runs (CE splits the path there), got %d"
        % len(runs))
    for run in runs:
        assert _longest_step_flat(run) < 10.0, (
            "a run still jumps %0.1f px between consecutive samples -- that is "
            "the closing chord" % _longest_step_flat(run))
    # both runs are the SAME arc: same start and end on screen
    assert list(runs[0][:2]) == pytest.approx(list(runs[1][:2]), abs=1e-6)
    assert list(runs[0][-2:]) == pytest.approx(list(runs[1][-2:]), abs=1e-6)


def test_send_arc_emits_no_chord_after_repeat():
    """End to end through `_send_arc`: the 165 px step must be gone."""
    sender = _Sender()
    arc = _arc()
    arc.repeat(2)
    sender._send_arc(arc, 1.0, 960, 540, 0.0, None)
    strips = _strips(sender.dll.calls)
    assert strips, "the repeated arc emitted nothing"
    for pts in strips:
        step = _longest_step(pts)
        assert step < 10.0, (
            "_send_arc stroked a %0.1f px jump: the repeated arc was closed "
            "into one shape by a chord from its end back to its start" % step)


def test_send_arc_before_repeat_is_unchanged():
    """Non-regression: the plain arc keeps one strip per width layer.

    The split only fires on a real anchor discontinuity, so every arc that
    rendered correctly before the fix submits byte-identical geometry.
    """
    sender = _Sender()
    sender._send_arc(_arc(), 1.0, 960, 540, 0.0, None)
    strips = _strips(sender.dll.calls)
    assert len(strips) == 2, (
        "expected one strip per width layer (core + band), got %d"
 % len(strips))
    for pts in strips:
        assert len(pts) >= 100, len(pts)
        assert _longest_step(pts) < 10.0


def test_split_rule_matches_ce():
    """The split indices are CE's own (`get_subpath_split_indices_from_points`)."""
    arc = _arc()
    arc.repeat(2)
    points = np.asarray(arc.get_points(), dtype=float)
    sender = _Sender()
    runs = sender._stroke_points_subpaths(
        points, 960, 540, None, 0.0, 480.0, 270.0, arc)
    getter = getattr(arc, "get_subpath_split_indices_from_points", None)
    if getter is None:                                  # pragma: no cover
        pytest.skip("manim without get_subpath_split_indices_from_points")
    # CE returns an (n_subpaths, 2) array of [start, end) POINT indices
    splits = np.asarray(getter(points, n_dims=2), dtype=int)
    assert splits.shape == (len(runs), 2), (splits.tolist(), len(runs))
    assert int(splits[0][0]) == 0 and int(splits[-1][1]) == len(points)
    # the boundary sits between curve 7 and curve 8, i.e. at point 32
    assert int(splits[0][1]) == 32 and int(splits[1][0]) == 32, splits.tolist()
