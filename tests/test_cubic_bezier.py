"""A sub-8-point cubic path must be tessellated, not chorded.

Report R10-1: `ArcsAndCurves` "the last shape in the first row is wrong" -- that
shape is

    bezier = CubicBezier(-1.0 * LEFT, -0.4 * LEFT + 0.9 * UP,
                         0.4 * RIGHT - 0.9 * UP, 1.0 * RIGHT).move_to(...)

and manim 0.21 stores it as exactly FOUR points:

    (1.000, -0.000)  (0.400, 0.900)  (0.400, -0.900)  (1.000, 0.000)

i.e. one cubic segment (anchors + two handles).  Measured, screen space,
854x480:

    smooth curve of those points   27 x 31 px     -> CE renders 31 x 34 px
    control hull (the 4 points)    36 x 108 px    -> RTM rendered 40 x 112 px

`_send_vmobject`'s `if n < 8:` fast path (vulkan_text.py) stroked chords
straight between the raw control points, so the S/loop came out as a 3-vertex
triangle through the handles.  A 4-point VMobject is one cubic, never a polygon.

Probe (bezier_probe.py, real dispatch, DLL calls captured):

    AddLine (751.3,107.9)->(715.2,53.9)   <- p0 -> p1
    AddLine (715.2,53.9)->(715.2,161.9)   <- p1 -> p2
    AddLine (715.2,161.9)->(751.3,107.9)  <- p2 -> p3

Tests are Pure Python: they capture the DLL calls, no GPU, no ffmpeg, no DTW.
"""
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import CubicBezier, LEFT, RIGHT, UP, VMobject
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# The scene renders at 854x480, so a manim unit is h/8 = 60 screen pixels.
W, H = 1920, 1080
UNIT = H / 8.0

# The scene's exact mobject, and where it sits on screen.
SCENE_BEZIER = CubicBezier(-1.0 * LEFT, -0.4 * LEFT + 0.9 * UP,
                           0.4 * RIGHT - 0.9 * UP, 1.0 * RIGHT)
# +-0.2586 is the extremum of y(t) = 2.7 t (1-t) (1-2t): the handles at +-0.9
# never reach it, so the curve is 0.5172 units tall against a 1.8 unit hull.
CURVE_HALF_Y = 0.2586
HULL_HALF_Y = 0.9


class _Recorder(object):
    """Records every DLL call by name; returns 0 like the real stub."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _points(calls):
    """Point cloud of every primitive a send submitted, in screen pixels.

    Uses the documented native layouts: AddBezierPath takes xyz triples with the
    count in arg[1], AddLineStrip xy pairs with the count in arg[2], AddPolygon
    pairs with the count in arg[9]/verts in arg[10], AddLine four coordinates.
    Reading them as anything else yields nonsense bboxes (see tip_layout.py).
    """
    pts = []
    for name, args in calls:
        if name == "AddLine":
            pts.append((float(args[0]), float(args[1])))
            pts.append((float(args[2]), float(args[3])))
        elif name == "AddLineStrip":
            flat = list(args[0])
            n = int(args[2])
            stride = len(flat) // n if n else 0
            for i in range(n):
                pts.append((float(flat[stride * i]), float(flat[stride * i + 1])))
        elif name == "AddBezierPath":
            flat = list(args[0])
            n = int(args[1])
            stride = len(flat) // n if n else 0
            for i in range(n):
                pts.append((float(flat[stride * i]), float(flat[stride * i + 1])))
        elif name == "AddPolygon":
            raw = args[10]
            n = int(args[9])
            for i in range(n):
                pts.append((float(raw[2 * i]), float(raw[2 * i + 1])))
    return pts


def _capture(mob, w=W, h=H):
    """Send `mob` through the real dispatch; return (counts, point list)."""
    renderer = vb.MLWindow(w, h)
    rec = _Recorder()
    real_dll = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real_dll
        renderer.close()
    counts = {}
    for name, _args in rec.calls:
        counts[name] = counts.get(name, 0) + 1
    return counts, _points(rec.calls)


def _scene_bezier():
    """A fresh copy of the scene's mobject, where the scene puts it."""
    m = SCENE_BEZIER.copy()
    m.move_to(5.4 * RIGHT + 2.2 * UP)
    return m


def _band():
    """The screen y band the scene's smooth curve occupies (from move_to)."""
    m = _scene_bezier()
    cx = W / 2.0 + m.get_center()[0] * UNIT
    cy = H / 2.0 - m.get_center()[1] * UNIT
    return cx, cy, CURVE_HALF_Y * UNIT, HULL_HALF_Y * UNIT


def test_scene_cubic_bezier_stays_inside_the_curve_not_the_hull():
    """Red before the fix: the stroke reached the control hull corners.

    The hull is 1.8 units tall (108 px), the curve 0.5172 units (31 px): the
    emitted geometry must lie in the curve's band, +-4 px of slop for the
    sampling step, and must not climb into the handle space above/below it.
    """
    counts, pts = _capture(_scene_bezier())
    assert len(pts) >= 2, "nothing was emitted: %r" % counts
    cx, cy, half_curve, half_hull = _band()
    ys = [p[1] for p in pts]
    height = max(ys) - min(ys)
    # The hull is 108 px tall; the curve 31 px.  0.7 unit (42 px) separates them
    # with room to spare on both sides.
    assert height <= 0.7 * UNIT, (
        "the CubicBezier was stroked as its control polygon: emitted geometry "
        "is %.0f px tall (curve %.0f px, hull %.0f px) -- a 4-point VMobject is "
        "one cubic segment, not a triangle" % (height, 2 * half_curve, 2 * half_hull))
    assert min(ys) >= cy - half_curve - 4.0, (
        "the stroke climbs into the handle space above the curve "
        "(top %.1f px, curve top %.1f px)" % (min(ys), cy - half_curve))
    assert max(ys) <= cy + half_curve + 4.0, (
        "the stroke drops into the handle space below the curve "
        "(bottom %.1f px, curve bottom %.1f px)" % (max(ys), cy + half_curve))


def test_scene_cubic_bezier_does_not_reach_the_hull_corners():
    """Same defect stated as reach: no emitted vertex near a hull corner.

    The hull corners sit 0.9 units (54 px) above/below the element centre; the
    curve's extremes are 0.2586 units (15.5 px).  Reaching either corner means
    the handles were stroked as path points.
    """
    counts, pts = _capture(_scene_bezier())
    assert len(pts) >= 2, "nothing was emitted: %r" % counts
    cx, cy, _half_curve, half_hull = _band()
    reach = max(abs(p[1] - cy) for p in pts)
    assert reach <= 0.55 * UNIT, (
        "emitted vertex %.1f px from the element centre; the curve only reaches "
        "%.1f px, the control hull %.1f px" % (reach, _half_curve, half_hull))


def test_straight_small_path_keeps_one_chord():
    """Non-regression after the fix: a straight cubic must stay ONE chord.

    The tessellation is curved-segments-only, so a straight 4-point path (a
    Line's storage, a straight glyph) still costs a single chord rather than
    `samples` AddLine calls.  RED before the fix too, but for the opposite
    reason: 4 points were always chorded as p0->p1->p2->p3 = 3 chords x 2
    layers = 6 calls; the fix collapses a collinear segment to p0->p3 = 1 chord
    x 2 layers = 2 calls.
    """
    straight = CubicBezier((0.0, 0.0, 0.0), (1.0, 0.0, 0.0),
                           (2.0, 0.0, 0.0), (3.0, 0.0, 0.0))
    counts, pts = _capture(straight)
    assert counts.get("AddLine", 0) > 0, (
        "a straight 4-point path emitted no AddLine: %r" % counts)
    # 1 chord x 2 layers (fractional edge + opaque core) = 2 calls.
    assert counts.get("AddLine", 0) == 2, (
        "a straight cubic must still be ONE chord; got %d AddLine calls %r -- "
        "tessellating straight runs wastes a primitive per sample"
        % (counts.get("AddLine", 0), counts))


def test_stroke_layers_and_colour_are_untouched():
    """The fix may not touch `_stroke_layers` or the colour/alpha rule.

    `_stroke_layers(2.4, 1.0)` yields [(2, 0.4), (1, 1.0)] -- the fractional
    edge under the opaque core -- and that decomposition is pinned by
    de309df.  Every segment of the tessellated curve must carry it unchanged.
    """
    counts, _pts = _capture(_scene_bezier())
    renderer = vb.MLWindow(W, H)
    try:
        expected = set((w, round(a, 4)) for w, a in
                       renderer._stroke_layers(renderer._stroke_width(_scene_bezier()), 1.0))
    finally:
        renderer.close()
    assert expected, "the control mobject has no stroke at all"
    got = set()
    for name, args in _all_calls(_scene_bezier()):
        if name == "AddLine":
            got.add((int(args[4]), round(float(args[8]), 4)))
    assert got, "no AddLine was emitted: %r" % counts
    assert got == expected, (
        "the tessellation changed the stroke decomposition: %r != pinned %r"
        % (sorted(got), sorted(expected)))


def _all_calls(mob):
    renderer = vb.MLWindow(W, H)
    rec = _Recorder()
    real_dll = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real_dll
        renderer.close()
    return rec.calls


def _chords(flat, n):
    renderer = vb.MLWindow(W, H)
    try:
        return renderer._small_path_chords(flat, n)
    finally:
        renderer.close()


def test_small_path_chords_picks_the_layout_and_tessellates():
    """Unit level: which layouts exist below 8 points, and what each returns.

    * FOUR points is one cubic segment (manim stores anchors + handles), so it
      must be sampled, not chorded -- report R10-1.
    * A run of ``1 + 3k`` points is stitched through its shared anchor.
    * 5 or 6 anchors are not a cubic layout at all: there the raw points really
      are the path and must come back untouched.
    """
    # (1) one cubic: p0 (0,0) -> handles at y=-100 -> p3 (60,0).  The curve
    # reaches 0.75 * 100 = 75 px; the handles 100 px.
    cubic4 = [0.0, 0.0, 0.0,
              0.0, -100.0, 0.0,
              60.0, -100.0, 0.0,
              60.0, 0.0, 0.0]
    chords = _chords(cubic4, 4)
    assert len(chords) >= 8, (
        "a single cubic must be sampled; got %d chords (a chorded control hull "
        "would be 3)" % len(chords))
    assert max(abs(c[1]) for c in chords) <= 90.0 and \
           max(abs(c[3]) for c in chords) <= 90.0, (
        "the sampled curve reaches the handles: %r" % (chords[:3],))

    # (2) 1 + 3k, two segments sharing the anchor at (60,0).
    cubic7 = [0.0, 0.0, 0.0,
              0.0, -180.0, 0.0,
              60.0, -180.0, 0.0,
              60.0, 0.0, 0.0,
              120.0, 180.0, 0.0,
              180.0, 180.0, 0.0,
              180.0, 0.0, 0.0]
    chords7 = _chords(cubic7, 7)
    assert len(chords7) > 10, (
        "a 7-point 1+3k path must be sampled too; got %d chords" % len(chords7))
    ys = [c[1] for c in chords7] + [c[3] for c in chords7]
    assert max(abs(y) for y in ys) <= 150.0, (
        "the 1+3k path was chorded through its handles (reaches %r, curve 135)"
        % (max(abs(y) for y in ys),))

    # (3) 5 anchors: not 4k, not 1+3k -- the points ARE the path.
    raw5 = [0.0, 0.0, 0.0,
            10.0, 20.0, 0.0,
            30.0, 40.0, 0.0,
            50.0, 60.0, 0.0,
            70.0, 80.0, 0.0]
    chords5 = _chords(raw5, 5)
    assert len(chords5) == 4, (
        "a non-cubic 5-anchor path must stay its 4 raw chords; got %d"
        % len(chords5))
    for i, (x0, y0, x1, y1) in enumerate(chords5):
        assert (x0, y0) == (raw5[i * 3], raw5[i * 3 + 1])
        assert (x1, y1) == (raw5[(i + 1) * 3], raw5[(i + 1) * 3 + 1])
