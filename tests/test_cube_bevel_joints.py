"""Regression test: a BEVEL-joint outline must not grow a mitre tip.

Report: wiki ``06-三维`` ``assets/RTM output/01-三维基本体-cube.mp4``
-- "白色包边末端处理不对".

Root cause (``real_time_manim/render/shapes/stroke.py``): native's line
strips always mitre their joints, and a mitre tip reaches
``half_w / sin(interior / 2)`` past the vertex.  Manim gives the faces of its
3D solids ``joint_type=LineJointType.BEVEL``
(``manim/mobject/three_dimensions.py:583``), so ManimCE -- which passes that
to Cairo's ``set_line_join`` -- stops each corner at the straight cut between
the two outer offset points.  Measured on that clip at frame 5, cube corner
(1385.4, 584.1): RTM's white stroke runs to x=1394 (a ~8 px tip for the
face's 48 degree corner) while CE stops at x=1389 and has pure background
beyond it -- 68 px of extra white in 6 clusters, every one of them a
silhouette corner of the cube.

Fix: for a ``BEVEL`` mobject the closed contour is stroked as one two-point
strip per edge (native only mitres joints, and a 2-point strip has none, so
each edge ends with a butt cap at the vertex) plus one ``AddPolygon``
triangle per CONVEX corner -- exactly the region a bevel fills and the two
quads do not.

Headless: drives the sender against a stub DLL -- no GPU, no window, no
image.
"""

import math
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import LineJointType, Square  # noqa: E402

from real_time_manim.render.shapes import ShapeMixin  # noqa: E402

W, H = 1920, 1080
UNIT_PX = H / 8.0


class _Recorder:
    """Stands in for the native DLL and keeps every submitted call."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


class _Probe(ShapeMixin):
    """The sender assembly MLWindow inherits, without a window."""

    def __init__(self):
        self.dll = _Recorder()
        self.win_w, self.win_h = W, H

    @staticmethod
    def _dbg_emit(tag, text):
        pass


def _submit(joint):
    probe = _Probe()
    sq = Square(side_length=2, stroke_width=8, fill_opacity=1.0)
    sq.joint_type = joint
    probe._send_polygon(sq, sq.get_vertices(), alpha=1.0)
    return probe.dll.calls


def _corners(calls):
    tris = [args for name, args in calls if name == "AddPolygon" and args[9] == 3]
    return tris


def test_bevel_contour_is_stroked_edge_by_edge():
    """No joint means no mitre: every strip is exactly one edge long."""
    calls = _submit(LineJointType.BEVEL)
    strips = [args for name, args in calls if name == "AddLineStrip"]
    assert strips, "the square's outline was not stroked at all"
    assert all(a[2] == 2 for a in strips), (
        "a BEVEL contour was stroked as one strip (n=%s); its joints would "
        "be mitred and push a white tip out of every corner"
        % [a[2] for a in strips])
    assert len(strips) >= 4, len(strips)


def test_bevel_corner_gets_its_cut_triangle_outside_the_shape():
    """One triangle per corner, sitting on the OUTER side of the corner."""
    calls = _submit(LineJointType.BEVEL)
    tris = _corners(calls)
    assert tris, "no bevel triangles were emitted: the corners are notched"
    strips = [args for name, args in calls if name == "AddLineStrip"]
    # `_stroke_layers` widens the native quad (core + fractional edge), and
    # the mitre/bevel offset in draw_line.c is that native width halved.
    half_widths = {a[3] * 0.5 + 0.5 for a in strips}
    centre = (W / 2.0, H / 2.0)
    for args in tris:
        pts = [(args[10][i], args[10][i + 1]) for i in range(0, 6, 2)]
        apex = pts[0]                      # AddPolygon was fed the corner first
        # the corner of a side-2 square centred in the frame
        assert max(abs(apex[0] - centre[0]),
                   abs(apex[1] - centre[1])) == pytest.approx(UNIT_PX, abs=1.0)
        # the two outer offset points sit half a stroke further out
        for other in pts[1:]:
            d = math.hypot(other[0] - apex[0], other[1] - apex[1])
            assert d in half_widths, (d, half_widths, other, apex)
        # ... and the triangle itself is OUTSIDE the square, i.e. it is the
        # bevel fill and not a wedge shaved off the shape
        cx = sum(p[0] for p in pts) / 3.0
        cy = sum(p[1] for p in pts) / 3.0
        assert max(abs(cx - centre[0]), abs(cy - centre[1])) > UNIT_PX + 0.5, (
            "the bevel triangle %s sits inside the square" % (pts,))


def test_auto_joint_keeps_the_mitred_closed_strip():
    """Non-regression: the default joint is still Cairo's mitre."""
    calls = _submit(LineJointType.AUTO)
    strips = [args for name, args in calls if name == "AddLineStrip"]
    assert len(strips) == 2, [a[2] for a in strips]   # one per width layer
    assert {a[2] for a in strips} == {5}, [a[2] for a in strips]
    assert not _corners(calls), "an AUTO square must not get bevel triangles"


def test_a_stroked_square_without_a_joint_type_is_untouched():
    """Non-regression: the default joint type still behaves as before."""
    probe = _Probe()
    sq = Square(side_length=2, stroke_width=8, fill_opacity=1.0)
    assert not hasattr(sq, "joint_type") or sq.joint_type is LineJointType.AUTO
    probe._send_polygon(sq, sq.get_vertices(), alpha=1.0)
    strips = [a for n, a in probe.dll.calls if n == "AddLineStrip"]
    assert len(strips) == 2 and {a[2] for a in strips} == {5}
