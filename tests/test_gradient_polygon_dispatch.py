# -*- coding: utf-8 -*-
"""A gradient fill on a SMALL polygon must not be flattened by AddPolygon.

Item (a) of the batch-C render handoff: "小渐变多边形仍是单色".

Root cause
----------
``window/paint.py`` routed a ``Polygon``/``Polygram`` to native's ``AddPolygon``
unless it carried more than ``NATIVE_MAX_POLYGON_VERTS`` (64) vertices.
``AddPolygon`` takes ONE ``r,g,b`` and no gradient axis (``native/platform.h``),
so a fill CE paints as a ``cairo.LinearGradient`` over
``get_gradient_start_and_end_points()`` arrived as one flat colour.  The
multi-stop gradient machinery added for the wiki area page
(``render/util.py::shaded_fill_gradient``) lives on the BEZIER sender, so only
the over-64-vertex ``get_area`` polygons ever reached it -- any smaller
gradient polygon (a short ``get_area`` x_range, a ``Polygon``/``Rectangle``
with ``set_color((c1, c2))``) stayed flat.

Fix
---
``render/util.py::fill_gradient_stops`` answers "is this fill a ramp?" and the
polygon dispatch sends every ramp down the bezier path, exactly like the
over-64-vertex branch it sits next to.  Flat fills keep ``AddPolygon``.

Measurement
-----------
Synthetic twin (``tools/_probe_gradient_poly.py`` / the scene it documents),
``RegularPolygon(5).scale(2.2).set_color((RED, BLUE))`` -- 5 vertices, 2 stops --
recorded by RTM and by the pip ManimCE renderer, frame 60, row y=269/540:

    x       RTM before        CE                  RTM after
    364     (250,99,84) flat  (135,167,179) ramp   (136,168,178) ramp
    592     (250,99,84) flat  (204,125,122) ramp   (205,125,122) ramp

whole clip vs CE:  mean|diff| 5.7354 -> 0.3784, frames over the 4.0 threshold
80/90 -> 0/90, peak per-pixel error 128 -> (edge pixels only).

Run with::

    python -X utf8 -m pytest tests/test_gradient_polygon_dispatch.py -q
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402
import pytest  # noqa: E402

from manim import BLUE, GREEN_B, GREEN_D, RED, RegularPolygon  # noqa: E402

from real_time_manim import camera_state  # noqa: E402
from real_time_manim.render.shapes import ShapeMixin  # noqa: E402
from real_time_manim.render.text import TextMixin  # noqa: E402
from real_time_manim.render.util import (  # noqa: E402
    fill_gradient_stops,
    shaded_fill_gradient,
)
from real_time_manim.window.paint import PaintMixin  # noqa: E402


class _Recorder(object):
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Host(PaintMixin, TextMixin, ShapeMixin):
    """The real paint dispatcher with no window behind it."""

    win_w, win_h = 960, 540

    def __init__(self):
        self.dll = _Recorder()

    @staticmethod
    def _dbg_emit(*args, **kwargs):                     # pragma: no cover
        pass

    @staticmethod
    def _dbg_arrow(*args, **kwargs):                    # pragma: no cover
        pass


@pytest.fixture(autouse=True)
def _flat_camera():
    prev = camera_state.get_viewport()
    camera_state.set_viewport(None)
    yield
    camera_state.set_viewport(prev)


def _ramp_polygon(n=5, colors=(RED, BLUE)):
    """An n-vertex polygon whose fill carries one row per colour."""
    poly = RegularPolygon(n).scale(2.2).set_color(colors).set_opacity(1.0)
    assert len(poly.get_vertices()) <= 64, "this test is about SMALL polygons"
    return poly


def test_fill_gradient_stops_is_the_ramp_predicate():
    """The helper says "ramp" only for a genuinely multi-stop fill."""
    assert fill_gradient_stops(_ramp_polygon()) is not None
    flat = RegularPolygon(5).set_fill(RED, opacity=1.0)
    assert fill_gradient_stops(flat) is None, "one row is a flat fill"
    equal = RegularPolygon(5)
    equal.fill_rgbas = np.array([[0.1, 0.2, 0.3, 1.0]] * 4)
    assert fill_gradient_stops(equal) is None, "all-equal rows are flat"
    assert fill_gradient_stops(object()) is None, "no fill at all"
    # and the ramp it reports is the raw stops, in order
    poly = _ramp_polygon()
    stops = fill_gradient_stops(poly)
    assert np.allclose(stops, np.asarray(poly.get_fill_rgbas(), dtype=float))


def test_small_gradient_polygon_goes_down_the_bezier_path():
    """Red before the fix: a 5-vertex ramp was sent to AddPolygon, flat."""
    poly = _ramp_polygon()
    host = _Host()
    host._send(poly, 0.0, parent_alpha=1.0)

    polys = [a for n, a in host.dll.calls if n == "AddPolygon"]
    assert not polys, (
        "the gradient polygon was submitted to AddPolygon, which carries one "
        "colour and no gradient axis (native/platform.h) -- the ramp CE paints "
        "with cairo.LinearGradient came out flat")
    beziers = [a for n, a in host.dll.calls if n == "AddBezierPath"]
    assert beziers, "the gradient polygon submitted nothing at all"
    args = beziers[0]
    fill1 = tuple(int(v) for v in args[6:9])
    fill2 = tuple(int(v) for v in args[14:17])
    axis = tuple(float(v) for v in args[17:21])
    grad = shaded_fill_gradient(poly, 960, 540)
    assert grad is not None
    assert fill1 == grad[0] and fill2 == grad[1], (fill1, fill2, grad[:2])
    assert fill1 != fill2, "both stops are the same colour: the fill is flat"
    assert (axis[0], axis[1]) != (axis[2], axis[3]), (
        "degenerate gradient axis %r" % (axis,))
    assert int(args[12]) == 1, "the fill must be shown"


def test_flat_small_polygon_keeps_add_polygon():
    """Non-regression: a flat-filled polygon is not routed anywhere new."""
    poly = RegularPolygon(5).scale(2.2).set_fill(RED, opacity=1.0)
    host = _Host()
    host._send(poly, 0.0, parent_alpha=1.0)
    names = [n for n, _a in host.dll.calls]
    assert "AddPolygon" in names, names
    assert "AddBezierPath" not in names, (
        "a flat polygon took the bezier path -- every Square/Rectangle/"
        "arrow tip in every scene would pay for the gradient fix")


def test_big_gradient_polygon_still_takes_the_bezier_path():
    """The over-64-vertex rule keeps working next to the new one."""
    from manim import Axes, BLUE_C, GREEN

    ax = Axes(x_range=[-3, 3, 1], y_range=[-2, 6, 1], x_length=9, y_length=5.5)
    quad = ax.plot(lambda x: 0.5 * x ** 2 - 0.5, color=BLUE_C)
    area2 = ax.get_area(quad, x_range=(-1.5, 1.5),
                        bounded_graph=ax.plot(lambda x: 3, color=GREEN),
                        color=(BLUE_C, GREEN), opacity=0.6)
    assert len(area2.get_vertices()) > 64
    host = _Host()
    host._send(area2, 0.0, parent_alpha=1.0)
    names = [n for n, _a in host.dll.calls]
    assert "AddPolygon" not in names, names
    assert "AddBezierPath" in names, names


def test_multi_stop_fill_gradient_survives_the_helper_refactor():
    """`_multi_stop_fill_gradient` now calls `fill_gradient_stops`."""
    from real_time_manim.render.util import manim_to_screen

    poly = _ramp_polygon(5, (GREEN_B, GREEN_D))
    grad = shaded_fill_gradient(poly, 960, 540)
    assert grad is not None
    c1, c2, p1, p2 = grad
    stops = np.asarray(poly.get_fill_rgbas(), dtype=float)
    assert c1 == tuple(int(round(float(v) * 255)) for v in stops[0][:3])
    assert c2 == tuple(int(round(float(v) * 255)) for v in stops[-1][:3])
    gp1, gp2 = poly.get_gradient_start_and_end_points()
    want1 = manim_to_screen(gp1[0], gp1[1], 960, 540, gp1[2])
    want2 = manim_to_screen(gp2[0], gp2[1], 960, 540, gp2[2])
    assert p1 == pytest.approx(want1, abs=1e-6), (p1, want1)
    assert p2 == pytest.approx(want2, abs=1e-6), (p2, want2)
    assert p1 != p2, "a degenerate axis would make native divide by |g|^2"
