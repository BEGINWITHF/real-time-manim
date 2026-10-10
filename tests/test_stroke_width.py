"""Every stroke primitive must emit a quad whose ink equals manim's target.

Background (measured, `stroke_probe.py` on two `width`-bucket scenes):

    BracesAndLabels             ink x1.27   lit>55 x1.63   missing 87 px
    ApplyTransformAnimations    ink x1.23   lit>55 x1.68   missing  0 px

`missing = 0` means CE's ink is a strict subset of RTM's: RTM simply draws the
same strokes wider, it does not put ink in the wrong place.  100% of the excess
sits within 2 px of CE's ink.

Why: native renders a quad of `width + 1` px
     (native/draw/draw_line.c: half_thick = thick * 0.5f + 0.5f)
so passing `round(px)` straight through draws `round(px) + 1` px where manim
draws `px`.  For the default stroke_width=2 at 480p that is 2 px against 1.2 px.

`de309df` fixed `_send_line` and `_send_arrow` with "an integer core plus
fractional edges": a `core`-wide quad at full alpha plus a `core+1`-wide quad
at alpha `frac`, which composites to exactly `px` of ink.  The remaining stroke
primives still use the old `max(1, round(px))`.

This test is a pure-Python red/green loop -- no GPU, no ffmpeg, no DTW, no
compare_auto.  It captures the emitted `AddLine` calls, replays native's
`width + 1` coverage model over a fine perpendicular grid and asserts that

    ink  = integral of composited alpha   == px
    lit  = measure where alpha > 55/255   == px   (within raster snap)

so a regression turns this red in milliseconds instead of a 40-minute render.
"""
import inspect
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Arc, Arrow, Circle, DashedLine, Ellipse, Line, Rectangle, Square
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

# compare_auto's ink threshold, restated here on purpose (this file must not
# import compare_auto): a pixel below it is not "ink" for the coverage detector.
LIT = 55.0 / 255.0
# 1080p60 is the only supported format (MLWindow enforces it) ->
# px = stroke_width * 0.01 * (1080/8)
PX_PER_SW = 1.35
TOL_INK = 0.15   # px of ink
TOL_LIT = 0.50   # px of lit extent (any rasteriser must snap to the pixel grid)


def _key(a):
    """A segment identity: the four endpoints, independent of width/alpha."""
    return tuple(round(float(v), 3) for v in a[:4])


def segments(calls):
    """Group captured calls into per-segment layer stacks.

    Grouping is purely geometric -- layers of one segment share endpoints, the
    next segment does not -- so the grouping never depends on the layer rule
    under test.  Returns a list of [(width, alpha), ...] in emission order.
    """
    out = []
    for a in calls:
        k = _key(a)
        if out and out[-1][0] == k:
            out[-1][1].append((a[4], a[5]))
        else:
            out.append([k, [(a[4], a[5])]])
    return [layers for _k, layers in out]


def native_model(layers, step=0.005):
    """Replay native's quad rasterisation for ONE segment's layer stack.

    Native's quad is `width + 1` px wide (draw_line.c), centred on the stroke,
    and layers composite in push order:  out = a_top + out * (1 - a_top).
    """
    if not layers:
        return 0.0, 0.0
    quad_w = [w + 1.0 for w, _a in layers]
    half = max(quad_w) / 2.0
    xs = np.arange(-half - 1.0, half + 1.0, step)
    cov = np.zeros_like(xs)
    for w, a in layers:
        band = np.abs(xs) <= (w + 1.0) / 2.0
        cov[band] = a + cov[band] * (1.0 - a)
    ink = float(cov.sum()) * step
    lit = float((cov > LIT).sum()) * step
    return ink, lit


class Recorder:
    def __init__(self):
        self.calls = []


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow()
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def send_capture(renderer, mob, meth_name):
    """Call `_send_<meth>` with the right signature and record AddLine calls."""
    rec = Recorder()
    orig_line = renderer.dll.AddLine
    orig_dash = getattr(renderer.dll, "AddDashedLine", None)

    def _cap(*a):
        # AddLine(x1, y1, x2, y2, width, r, g, b, alpha)
        rec.calls.append(tuple(a[0:4]) + (float(a[4]), float(a[8])))
        return 0

    def _cap_dash(*a):
        # AddDashedLine(x1, y1, x2, y2, width, r, g, b, dash, gap, alpha)
        rec.calls.append(tuple(a[0:4]) + (float(a[4]), float(a[10])))
        return 0

    renderer.dll.AddLine = _cap
    if orig_dash is not None:
        renderer.dll.AddDashedLine = _cap_dash
    meth = getattr(renderer, meth_name)
    # `meth` is a bound method, so `self` is already gone from the signature.
    params = list(inspect.signature(meth).parameters)
    known = {
        "mob": mob, "a": 1.0, "w": 1920, "h": 1080, "rot": 0.0,
        "parent_offset": None, "rot_override": None,
    }
    args = []
    for p in params:
        if p not in known:
            raise AssertionError("%s has an unhandled parameter %r" % (meth_name, p))
        args.append(known[p])
    try:
        meth(*args)
    finally:
        renderer.dll.AddLine = orig_line
        if orig_dash is not None:
            renderer.dll.AddDashedLine = orig_dash
    return rec.calls


# (mobject factory, renderer method, stroke_width used)
CASES = [
    ("Line",       lambda: Line([-2, 0, 0], [2, 0, 0], stroke_width=2), "_send_line"),
    ("Arrow",      lambda: Arrow([-2, 0, 0], [2, 0, 0], stroke_width=2), "_send_arrow"),
    ("Square",     lambda: Square(side_length=2, stroke_width=2), "_send_square"),
    ("Rectangle",  lambda: Rectangle(width=3, height=2, stroke_width=2), "_send_rectangle"),
    ("Circle",     lambda: Circle(radius=1, stroke_width=2), "_send_circle"),
    ("Ellipse",    lambda: Ellipse(width=3, height=2, stroke_width=2), "_send_ellipse"),
    ("Arc",        lambda: Arc(radius=1, stroke_width=2), "_send_arc"),
    ("DashedLine", lambda: DashedLine([-2, 0, 0], [2, 0, 0], stroke_width=2),
     "_send_dashed_line"),
]


@pytest.mark.parametrize("name,factory,meth", CASES, ids=[c[0] for c in CASES])
def test_stroke_ink_matches_manim(renderer, name, factory, meth):
    mob = factory()
    calls = send_capture(renderer, mob, meth)
    assert calls, "%s emitted no AddLine stroke" % name

    px = PX_PER_SW * 2.0          # stroke_width=2 -> 1.2 px at 480p
    segs = segments(calls)
    assert segs, "%s produced no segment groups" % name

    bad = []
    for i, layers in enumerate(segs):
        ink, lit = native_model(layers)
        if abs(ink - px) > TOL_INK or abs(lit - px) > TOL_LIT:
            bad.append((i, ink, lit, layers))
    assert not bad, (
        "%s: %d/%d segments mis-drawn (target %.3f px of ink AND of lit "
        "extent); first bad segment #%d ink=%.3f lit=%.3f layers=%s"
        % (name, len(bad), len(segs), px, bad[0][0], bad[0][1], bad[0][2],
           [(w, round(a, 3)) for w, a in bad[0][3]]))


def test_native_quad_is_width_not_width_plus_one(renderer):
    """Document the native contract this file models.

    `draw_line.c` builds a quad of `width + 1` px.  If that ever changes, every
    expectation above silently changes with it, so pin it with a direct probe:
    a width-0 quad must be exactly one pixel wide.
    """
    calls = [(0, 1.0)]
    ink, lit = native_model(calls, step=0.01)
    assert ink == pytest.approx(1.0, abs=0.02), "width=0 quad should be 1 px wide"
