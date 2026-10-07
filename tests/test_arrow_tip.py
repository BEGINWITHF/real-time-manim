"""Arrow heads must be the tip manim built, not a synthesised triangle.

Report #9 -- `ArrowTips` (scenes/05_mobject_classes.py:827):

    compare_auto: 4.5  CONTENT  A 0.866  B 0.266  C- 0.094  C+ 0.152
    Cink 0.155   firstBad 6   trips A,B,C[width]

Every bit of the ink difference sits in the seven arrow heads (x 205..245,
y = 105/140/173/208/246/288/325) plus the custom `_PentagonTip` arrow at
x ~690; the seven standalone tip `samples` at the top right matched CE exactly.
Ink measured in each tip zone, frame 39:

    tip class                 CE   RTM   RTM/CE
    ArrowTriangleTip          158   248    1.57   (hollow triangle)
    ArrowTriangleFilledTip    191   238    1.25
    ArrowCircleTip            137   249    1.82   (hollow circle)
    ArrowCircleFilledTip      277   249    0.90
    ArrowSquareTip            141   247    1.75   (hollow square)
    ArrowSquareFilledTip      322   248    0.77
    StealthTip                220   248    1.13

RTM's tip ink is 238-249 px for *every* shape, and ASCII panels show CE drawing
seven different heads (hollow triangle, solid triangle, hollow circle, solid
disc, hollow square, solid square, stealth) while RTM draws the same solid
triangle each time.

Why: `_send_arrow` synthesised the head itself

    head_w = head_len * 0.5
    head_verts = (sx2, sy2, hx2, hy2, hx1, hy1)
    self.dll.AddPolygon(..., 3, head_verts, progress, a, 1)

whose only inputs are `tip_length` and a hard-coded `0.5` taper, so `mob.tip`
-- the real `ArrowTip` mobject, which carries shape, size and hollow-vs-filled
-- was never read.  On top of that `vulkan_bind.py` skips the submobject walk
for `Arrow` ("Arrow is already fully handled by _send_arrow"), so the tip manim
attached was dropped and never reached the point path at all.  Measured with
`%TEMP%\arrow_probe.py`: all seven tips have their own submobject and their own
geometry (shoelace 221 / 221 / 359 / 359 / 442 / 442 / 138 px), while the
synthesised head is a 220 px triangle for every one of them.

The same probe also pinned a second defect: `Arrow.get_end()` is the *tip's*
tip, so the old `get_end() - tip_length` shaft end is only right when the tip
happens to be exactly `tip_length` long -- for `ArrowSquareFilledTip` the line
stops at 1.855 but the shaft was drawn to 2.000 (8.7 px too far).

Pure Python: captures the DLL calls, no GPU, no ffmpeg, no DTW.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import real_time_manim.vulkan_bind as vb
    from manim import (Arrow, ArrowCircleFilledTip, ArrowCircleTip,
                       ArrowSquareFilledTip, ArrowSquareTip,
                       ArrowTriangleFilledTip, ArrowTriangleTip, StealthTip)
    from real_time_manim.vulkan_util import manim_to_screen
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

W, H = 1920, 1080
TIP_CLASSES = [ArrowTriangleTip, ArrowTriangleFilledTip, ArrowCircleTip,
               ArrowCircleFilledTip, ArrowSquareTip, ArrowSquareFilledTip,
               StealthTip]
SHAFT_CALLS = ("AddLine", "AddDashedLine")


class Recorder(object):
    """Records every DLL call by name; returns 0 like the real stub."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(W, H)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def capture(renderer, mob):
    """Send `mob` through the real dispatch; return [(dll_name, args), ...]."""
    rec = Recorder()
    real = renderer.dll
    renderer.dll = rec
    try:
        renderer._send(mob)
    finally:
        renderer.dll = real
    return rec.calls


def arrow(tip_cls):
    return Arrow(start=np.array([0.0, 0.0, 0.0]),
                 end=np.array([2.6, 0.0, 0.0]),
                 tip_shape=tip_cls, color="#0000FF")


def sig(calls):
    """A signature of everything drawn, coordinates rounded to 0.1 px.

    Call *counts* alone cannot tell the seven shapes apart (they only separate
    hollow from filled), so the geometry itself is what identifies a head.
    """
    out = []
    for name, args in calls:
        nums = []
        for v in args:
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                nums.append(round(float(v), 1))
                continue
            try:
                nums.extend(round(float(x), 1) for x in v)
            except Exception:
                pass
        out.append((name, tuple(nums)))
    return tuple(out)


def _verts(flat, n, stride):
    """First two coordinates of each vertex, honouring the array's stride.

    The head primitives do not agree on a layout: `AddBezierPath` carries
    x/y/z triples (48 floats for 16 points), `AddLineStrip` carries x/y pairs
    (72 for 36), and `AddPolygon` carries the vertex count alongside the
    array.  Reading them all as pairs silently interleaves x with z and yields
    a bbox like (0, 568, 0, 568) -- measured while writing this test.
    """
    return [(float(flat[stride * i]), float(flat[stride * i + 1]))
            for i in range(n)]


def head_points(name, args):
    """Vertices of a head primitive (anything that is not the shaft)."""
    try:
        if name == "AddBezierPath":
            flat, n = list(args[0]), int(args[1])
            return _verts(flat, n, len(flat) // n)
        if name == "AddLineStrip":
            flat, n = list(args[0]), int(args[2])
            return _verts(flat, n, len(flat) // n)
        if name == "AddPolygon":
            flat, n = list(args[10]), int(args[9])
            return _verts(flat, n, len(flat) // n)
    except Exception:
        return []
    return []


def head_bbox(calls):
    pts = []
    for name, args in calls:
        if name in SHAFT_CALLS:
            continue
        pts.extend(head_points(name, args))
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def shaft_end(calls):
    for name, args in calls:
        if name == "AddLine":
            return float(args[2]), float(args[3])
    return None


def test_seven_tip_shapes_draw_seven_different_heads(renderer):
    """Every `tip_shape` must change what is drawn.

    Before the fix all seven arrows emitted byte-identical call lists: the
    shaft comes from `get_start()`/`get_end()`, which do not depend on the tip,
    and the head was the same synthesised triangle for all of them.  So the
    defect shows up as exactly ONE distinct signature across the seven shapes
    (measured: 7 after the fix).
    """
    sigs = {sig(capture(renderer, arrow(c))) for c in TIP_CLASSES}
    assert len(sigs) >= 5, (
        "%d distinct drawn geometries across the seven tip_shape values -- "
        "the head does not follow `tip_shape`" % len(sigs))


def test_hollow_tip_is_stroked_and_filled_tip_is_solid(renderer):
    """`ArrowCircleTip` is an outline; `ArrowCircleFilledTip` is a disc.

    CE measures 137 px against 277 px for those two tips, i.e. one is a ring and
    the other a filled circle.  They must not be drawn the same way: the
    outline goes down the stroked path, the disc does not.
    """
    hollow = capture(renderer, arrow(ArrowCircleTip))
    filled = capture(renderer, arrow(ArrowCircleFilledTip))
    hollow_names = [n for n, _a in hollow]
    filled_names = [n for n, _a in filled]
    assert "AddLineStrip" in hollow_names, (
        "the hollow ArrowCircleTip was not stroked (calls: %s) -- an outline "
        "tip drawn as a solid shape is the report #9 defect"
        % hollow_names)
    assert "AddLineStrip" not in filled_names, (
        "the filled ArrowCircleTip was stroked instead of filled (calls: %s)"
        % filled_names)
    assert sig(hollow) != sig(filled), (
        "hollow and filled circle tips produced identical output")


def test_head_covers_the_tips_own_extent(renderer):
    """The drawn head must span the tip mobject's own box.

    `ArrowSquareFilledTip` is the discriminating case: its box is
    1.855..2.350 wide and +-(0.247) tall (measured by `arrow_probe.py`), while
    the synthesised triangle was forced to `get_end() - tip_length` = 2.000..2.350
    with a taper of `0.5 * head_len`, i.e. 71% of the tip in *both* axes.
    """
    arr = arrow(ArrowSquareFilledTip)
    calls = capture(renderer, arr)
    box = head_bbox(calls)
    assert box is not None, "no head geometry emitted at all: %s" % [n for n, _a in calls]

    tp = np.asarray(arr.tip.get_points())
    x0, y1 = manim_to_screen(float(tp[:, 0].min()), float(tp[:, 1].max()), W, H)
    x1, y0 = manim_to_screen(float(tp[:, 0].max()), float(tp[:, 1].min()), W, H)
    tip_w, tip_h = x1 - x0, y1 - y0
    head_w, head_h = box[1] - box[0], box[3] - box[2]

    assert head_w >= 0.85 * tip_w, (
        "head spans %.1f px wide but the tip mobject spans %.1f px (71%% is the "
        "synthesised triangle's share)" % (head_w, tip_w))
    assert head_h >= 0.85 * tip_h, (
        "head spans %.1f px tall but the tip mobject spans %.1f px"
        % (head_h, tip_h))
    # screen y grows downwards, so the two bounds come back swapped
    tx0, tx1 = min(x0, x1), max(x0, x1)
    ty0, ty1 = min(y0, y1), max(y0, y1)
    assert box[0] >= tx0 - 4.0 and box[1] <= tx1 + 4.0 and \
        box[2] >= ty0 - 4.0 and box[3] <= ty1 + 4.0, (
            "head bbox %s escapes the tip's own box x[%.1f..%.1f] y[%.1f..%.1f]"
            % (box, tx0, tx1, ty0, ty1))


def test_shaft_ends_at_the_lines_own_last_point(renderer):
    """`Arrow.get_end()` is the tip's tip, so it is not the shaft's end.

    The line's own last point for `ArrowSquareFilledTip` is at x=1.855; the old
    `get_end() - tip_length` rule put the shaft at x=2.000, drawing 8.7 px of
    stroke underneath the head.
    """
    arr = arrow(ArrowSquareFilledTip)
    calls = capture(renderer, arr)
    end = shaft_end(calls)
    assert end is not None, "no shaft stroke emitted: %s" % [n for n, _a in calls]

    own = np.asarray(arr.get_points())
    start = np.asarray(arr.get_start())
    line_end = own[int(np.argmax(np.linalg.norm(own - start, axis=1)))]
    want = manim_to_screen(float(line_end[0]), float(line_end[1]), W, H)

    assert abs(end[0] - want[0]) <= 1.0 and abs(end[1] - want[1]) <= 1.0, (
        "shaft ends at (%.2f, %.2f) but the line's own last point is at "
        "(%.2f, %.2f)" % (end[0], end[1], want[0], want[1]))

    tip_len = float(getattr(arr, "tip_length", 0.35))
    e = np.asarray(arr.get_end())
    old = manim_to_screen(float(e[0] - tip_len), float(e[1]), W, H)
    assert abs(end[0] - old[0]) > 3.0, (
        "shaft still ends at `get_end() - tip_length` (%.2f) -- that value is "
        "only right when the tip happens to be exactly tip_length long" % old[0])
