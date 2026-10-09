"""A Polygram's disjoint vertex groups must be drawn as separate subpaths.

Background
----------
manim's ``Polygram`` is "a generalized Polygon, allowing for **disconnected**
sets of edges": it stores one closed subpath per vertex group, while
``get_vertices()`` flattens them into a single list.

`_send_polygon` used to join that flat list end to end, so every edge *between*
two groups was invented and the closing edge of each group was lost.  Measured
on the demo suite's ``08_geometry.PolygramFamily`` (last frame, RTM against CE
1920x1080, both hexagrams are two triangles):

    Polygram         region mean diff 5.93   ink CE 6977 px vs RTM 6122 px
    RegularPolygram  region mean diff 10.25  ink CE 8133 px vs RTM 7583 px

while Polygon, Star, ConvexHull -- one vertex group each -- already matched.
The rendered purple "Polygram" was a zigzag with two horizontal bars where CE
draws a hexagram, i.e. the shape was never drawn correctly.

These tests pin both halves: a multi-group Polygram submits exactly the edges
manim's own ``get_vertex_groups()`` describes (nothing more, nothing less), and
a single-group polygon keeps submitting its own closed outline.

Pure Python -- captures the DLL calls, no GPU work, no ffmpeg::

    python -X utf8 -m pytest tests/test_polygram_groups.py -q
"""

import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import numpy as np
    from manim import Polygon, Polygram, RegularPolygram, Star

    import real_time_manim.vulkan_bind as vb
    from real_time_manim.vulkan_util import manim_to_screen
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# the demo scene's figures (scenes/08_geometry.py, class PolygramFamily)
def hexagram_polygram():
    return Polygram(
        [(-0.7, -0.5, 0), (0.7, -0.5, 0), (0, 0.6, 0)],
        [(-0.7, 0.5, 0), (0.7, 0.5, 0), (0, -0.6, 0)],
    )


def regular_hexagram():
    return RegularPolygram(num_vertices=6, density=2, radius=0.85)


def plain_polygon():
    return Polygon(
        [-0.8, -0.6, 0], [0.7, -0.7, 0], [0.9, 0.5, 0],
        [-0.4, 0.8, 0], [-1.0, 0.2, 0],
    )


def _capture(mob):
    """Send `mob` through the real dispatch; return (segments, polygons, size).

    `segments` is a set of unordered rounded point pairs -- the distinct edges
    native was asked to stroke -- and `polygons` the raw AddPolygon arg tuples.
    """
    renderer = vb.MLWindow(854, 480)
    lines, polys = [], []
    renderer.dll.AddLine = lambda *a: lines.append(a)
    renderer.dll.AddPolygon = lambda *a: polys.append(a)
    try:
        renderer._send(mob)
        size = (renderer.win_w, renderer.win_h)
    finally:
        renderer.close()

    segments = set()
    for line in lines:
        x0, y0, x1, y1 = line[:4]
        segments.add(frozenset({_round(x0, y0, size), _round(x1, y1, size)}))
    return segments, polys, size


def _round(x, y, size):
    return (round(float(x), 3), round(float(y), 3))


def _screen(pt, size):
    w, h = size
    x, y = manim_to_screen(float(pt[0]), float(pt[1]), w, h,
                           float(pt[2]) if len(pt) > 2 else 0.0)
    return (round(x, 3), round(y, 3))


def _expected_edges(mob, size):
    """The edges manim itself describes, one closed loop per vertex group."""
    edges = set()
    for group in mob.get_vertex_groups():
        pts = [_screen(p, size) for p in group]
        for a, b in zip(pts, pts[1:] + pts[:1]):
            edges.add(frozenset({a, b}))
    return edges


def _groups(mob):
    return [np.asarray(g) for g in mob.get_vertex_groups()]


# --------------------------------------------------------------------------- #
# tests
# --------------------------------------------------------------------------- #

def test_the_scene_hexagram_really_is_two_groups():
    """Precondition: what this bug is about still holds in manim."""
    groups = _groups(hexagram_polygram())
    assert len(groups) == 2, (
        "manim's Polygram no longer stores two vertex groups; this test's "
        "premise is gone (got %d)" % len(groups))
    assert len(hexagram_polygram().get_vertices()) == 6, (
        "get_vertices() must flatten the two triangles into one list, which is "
        "exactly what _send_polygon used to join end to end")


def test_polygram_submits_only_its_own_edges():
    """Red before the fix: two cross-group edges, one missing closing edge."""
    mob = hexagram_polygram()
    segments, _, size = _capture(mob)
    expected = _expected_edges(mob, size)

    assert len(expected) == 6, "the hexagram must describe 6 real edges"
    assert segments == expected, (
        "a two-group Polygram was stroked as ONE closed polyline: %d missing "
        "%s / %d invented %s"
        % (len(expected - segments), sorted(expected - segments)[:4],
           len(segments - expected), sorted(segments - expected)[:4]))


def test_regular_polygram_hexagram_submits_only_its_own_edges():
    """RegularPolygram(n=6, density=2) is the same two-triangle defect."""
    mob = regular_hexagram()
    segments, _, size = _capture(mob)
    expected = _expected_edges(mob, size)
    assert len(expected) == 6
    assert segments == expected, (
        "RegularPolygram's two triangles were joined into one polyline: "
        "missing %s / invented %s"
        % (sorted(expected - segments)[:4], sorted(segments - expected)[:4]))


def test_a_single_group_polygon_is_untouched():
    """Control: one vertex group keeps its exact closed outline."""
    mob = plain_polygon()
    segments, _, size = _capture(mob)
    assert segments == _expected_edges(mob, size), (
        "a plain Polygon changed shape; the split must not fire on a "
        "single-group path")


def test_star_is_untouched():
    """Control: a Star is one group of 10 vertices, and must stay that way."""
    mob = Star(n=5, outer_radius=0.95, inner_radius=0.42)
    segments, _, size = _capture(mob)
    assert len(_groups(mob)) == 1
    assert segments == _expected_edges(mob, size)


def test_a_filled_hexagram_fills_each_triangle_separately():
    """native fans a fill from one origin, so the groups cannot share an
    AddPolygon: fanning both triangles from the hexagram's centroid fills the
    gap between them."""
    mob = hexagram_polygram()
    mob.set_fill(opacity=1.0)
    _, polys, _ = _capture(mob)
    assert len(polys) == 2, (
        "a filled two-group Polygram must submit one polygon per group, got %d"
        % len(polys))
    for poly in polys:
        # AddPolygon(x, y, r, g, b, br, bg, bb, bw, vert_count, verts, progress,
        #            alpha, close)
        assert poly[9] == 3, (
            "each submitted polygon must be one of the triangles (3 vertices), "
            "got %d -- the groups were still flattened into a single fan"
            % poly[9])
