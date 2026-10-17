"""A multi-stop fill must reach native as a GRADIENT, not as one flat colour.

Report: wiki ``05-坐标系与图表/06-面积与黎曼矩形``
``06-面积与黎曼矩形-area.mp4`` -- "有渐变色没有正确生效".

Root cause
----------
``Axes.get_area(..., color=(C1, C2))`` ends in
``Polygon(...).set_color((C1, C2))``, whose ``fill_rgbas`` holds TWO rows --
one per gradient stop.  CE turns any multi-row ``fill_rgbas`` into a
``cairo.LinearGradient`` over ``vmobject.get_gradient_start_and_end_points()``
(``camera/camera.py:731-746``).  RTM's generic filler
(``render/text/vmobject.py``) AVERAGES those rows and paints the whole shape
one flat mid colour; native's ``AddBezierPath`` already carries a second stop
plus a gradient axis (``native/platform.h``), but
``render/util.py::shaded_fill_gradient`` only produced one for a
``shade_in_3d`` face, so ``_send_vmobject`` never passed it.

Fix
---
``shaded_fill_gradient`` now falls back to ``_multi_stop_fill_gradient``: for
any fill whose stops are not all identical it returns the first/last stop and
the screen projection of ``get_gradient_start_and_end_points()`` -- the exact
method and rule CE uses.  An all-equal (flat) fill still returns ``None``, so
every already-correct shape keeps the code path it was measured on, and the
``shade_in_3d`` branch is tried first, unchanged.

Measurement (before)
--------------------
``tools/_probe_idx17_geom.py`` on frame 220 of the wiki pair, row y=594
(1920x1080), inside the filled band (RTM's flat colour spans x 660..1259):

    x        RTM (flat)      CE (ramp)
    768      (65,116,95)     (70,114,79)    <- CE near the GREEN stop
    1056     (65,116,95)     (61,114,104)   <- CE toward the BLUE_C stop

``0.6 * mean(BLUE_C, GREEN) = 0.6 * (110,195,162) = (66,117,97)`` is exactly
RTM's constant, i.e. the gradient was replaced by its own average; peak pixel
error 80/255, 350 differing pixels per frame, mean|diff| 1.025 (258 frames).

Measurement (after)
-------------------
The same two sample points, evaluated from the returned stops and axis:
(72,116,79) and (63,117,105) -- within 3/255 of CE at both.

Run with::

    python -X utf8 -m pytest tests/test_gradient_fill_stops.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

from manim import Axes, BLUE_C, GREEN, GREEN_B, GREEN_D

from real_time_manim import camera_state
from real_time_manim.render.shapes import ShapeMixin
from real_time_manim.render.text import TextMixin
from real_time_manim.render.util import (manim_to_screen,
                                         shaded_fill_gradient)


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Host(TextMixin, ShapeMixin):
    """Everything `_send_vmobject` needs, with no window behind it."""

    win_w, win_h = 960, 540

    def __init__(self):
        self.dll = _Recorder()

    @staticmethod
    def _dbg_emit(*args, **kwargs):                     # pragma: no cover
        pass


@pytest.fixture(autouse=True)
def _flat_camera():
    prev = camera_state.get_viewport()
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(prev)


def _area_pair():
    """The wiki sample's two `get_area` polygons (06-面积与黎曼矩形)."""
    ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1], x_length=9, y_length=5.5)
    quad = ax.plot(lambda x: 0.5 * x ** 2 - 0.5, color=BLUE_C)
    area = ax.get_area(quad, x_range=(0, 2), color=(GREEN_B, GREEN_D),
                       opacity=1)
    bound = ax.plot(lambda x: 3, color=GREEN)
    area2 = ax.get_area(quad, x_range=(-1.5, 1.5), bounded_graph=bound,
                        color=(BLUE_C, GREEN), opacity=0.6)
    return area, area2


def test_get_area_gradient_is_reported():
    """Red before the fix: `shaded_fill_gradient` returned None (2D only)."""
    area, area2 = _area_pair()
    for poly, opacity in ((area, 1.0), (area2, 0.6)):
        grad = shaded_fill_gradient(poly, 960, 540)
        assert grad is not None, (
            "%s carries %d fill stops but no gradient was reported -- CE fills "
            "it with cairo.LinearGradient (camera.py:731-746), RTM painted one "
            "flat colour" % (type(poly).__name__, len(poly.fill_rgbas)))
        c1, c2, p1, p2 = grad
        stops = np.asarray(poly.fill_rgbas, dtype=float)
        assert c1 == pytest.approx(tuple(round(float(v) * 255)
                                         for v in stops[0][:3]), abs=1)
        assert c2 == pytest.approx(tuple(round(float(v) * 255)
                                         for v in stops[-1][:3]), abs=1)
        assert c1 != c2, "identical stops mean a flat fill, not a gradient"
        # the axis is CE's own pair of points, projected like the shape
        gp1, gp2 = poly.get_gradient_start_and_end_points()
        want1 = manim_to_screen(gp1[0], gp1[1], 960, 540, gp1[2])
        want2 = manim_to_screen(gp2[0], gp2[1], 960, 540, gp2[2])
        assert p1 == pytest.approx(want1, abs=1e-6), (p1, want1)
        assert p2 == pytest.approx(want2, abs=1e-6), (p2, want2)


def test_flat_fill_still_reports_no_gradient():
    """Non-regression: a one-stop (or all-equal) fill keeps the old path."""
    from manim import Circle, Square
    for mob in (Circle(radius=1.0), Square(side_length=2.0)):
        assert shaded_fill_gradient(mob, 960, 540) is None
    flat = Circle(radius=1.0)
    flat.set_fill(GREEN_B, opacity=0.5)          # still ONE colour
    flat.fill_rgbas = np.array([[0.1, 0.2, 0.3, 0.5]] * 3)   # equal rows
    assert shaded_fill_gradient(flat, 960, 540) is None


def test_send_vmobject_passes_the_second_stop_and_axis_to_native():
    """End to end: `AddBezierPath` must carry fr2/fg2/fb2 + a real axis."""
    _area, area2 = _area_pair()
    host = _Host()
    host._send_vmobject(area2, 1.0, 960, 540, None, 0.0)
    beziers = [a for n, a in host.dll.calls if n == "AddBezierPath"]
    assert beziers, "the area polygon submitted nothing"
    args = beziers[0]
    fill1 = tuple(int(v) for v in args[6:9])
    fill2 = tuple(int(v) for v in args[14:17])
    axis = tuple(float(v) for v in args[17:21])
    grad = shaded_fill_gradient(area2, 960, 540)
    assert fill1 == grad[0], (fill1, grad[0])
    assert fill2 == grad[1], (
        "the second stop was dropped: native received %r, the gradient's "
        "second stop is %r -- the fill would be flat" % (fill2, grad[1]))
    assert fill1 != fill2
    assert (axis[0], axis[1]) != (axis[2], axis[3]), (
        "degenerate gradient axis %r: native divides by |g|^2" % (axis,))
    assert axis == pytest.approx(grad[2] + grad[3], abs=1e-6)
    assert float(args[9]) == pytest.approx(0.6, abs=1e-6), (
        "the polygon's 0.6 opacity must ride the fill alpha", args[9])
    assert int(args[12]) == 1, "the fill must be shown"


def test_ramp_reproduces_the_ce_video_pixels():
    """The returned stops/axis reproduce CE's measured scan line.

    CE at row y=594 of the 1920x1080 twin, frames 220-250 (settled), sampled
    inside the band:  x=768 -> (70,114,79), x=1056 -> (61,114,104).
    The ramp is the two stops interpolated at the projection of that pixel and
    blended at the polygon's 0.6 opacity over black -- exactly what native's
    gradient fill computes (draw_bezier.c:333-338).
    """
    _area, area2 = _area_pair()
    grad = shaded_fill_gradient(area2, 1920, 1080)
    assert grad is not None
    c1, c2, p1, p2 = grad
    axis = np.array([p2[0] - p1[0], p2[1] - p1[1]], dtype=float)
    denom = float(np.dot(axis, axis))
    opacity = float(np.asarray(area2.fill_rgbas, dtype=float)[:, 3].max())
    # the video's own mapping: 1920x1080 over an 8-unit frame -> 135 px/unit.
    # (t is invariant if the scale is, but pin it so a config override fails
    # loudly instead of silently sampling a different pixel.)
    assert manim_to_screen(1.0, 0.0, 1920, 1080)[0] - 960.0 == pytest.approx(
        135.0, abs=1e-6)
    samples = {768: (70, 114, 79), 1056: (61, 114, 104)}
    for x, want in samples.items():
        sx, sy = manim_to_screen((x - 960.0) / 135.0, (540.0 - 594.0) / 135.0,
                                 1920, 1080, 0.0)
        t = ((sx - p1[0]) * axis[0] + (sy - p1[1]) * axis[1]) / denom
        t = min(1.0, max(0.0, t))
        got = tuple(int(round((c1[i] + (c2[i] - c1[i]) * t) * opacity))
                    for i in range(3))
        assert all(abs(got[i] - want[i]) <= 6 for i in range(3)), (
            "ramp at x=%d gives %r, CE's video has %r (t=%.3f, stops %r/%r)"
            % (x, got, want, t, c1, c2))
