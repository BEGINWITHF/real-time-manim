"""A glyph's fill alpha must be its OWN rgba alpha, not a forced 1.0.

Report R10-3: `GraphMobjects` "the vertices flicker abnormally before they
appear".  Measured, 854x480, region around `undirected` (the first of the three
FadeIn'd graphs), lit = luma > 55:

    frame   CE lit/ink        RTM lit/ink
      0       0 /    0          481 / 566   <- one-frame flash
      1       0 /    3            0 /   0
      2       0 / 1208            0 / 994

and the same one-frame flash exactly one frame before EACH of the three FadeIns
(frames 0 / 9 / 18: RTM lit 481 / 284 / 459, CE lit 0 at all three).  Only the
six vertex labels flash -- never the dots or the edges.

Probe (flicker_probe.py, real dispatch, DLL calls captured):

    after FadeIn.begin() + interpolate(0):
      LabeledDot    fill=0.000 stroke=0.000     <- correctly invisible
      MathTex       fill=0.000 stroke=0.000
      MathTexPart   fill=0.000 stroke=1.000     <- phantom (0 points)
      VMobjectFromSVGPath fill=0.000 stroke=0.000
      Line (edges)  fill=0.000 stroke=0.000
      glyph fill_rgbas = [[0., 0., 0., 0.]]     get_color() = #FFFFFF
      emitted: AddBezierPath x6, args[9] (fill_alpha) = 1.0, show_fill = 1

Root cause, `vulkan_text.py` `_send_vmobject`:

    if fr == 0 and fg == 0 and fb == 0:        # fill colour is black
        fr, fg, fb = mob.get_color()           # colour fallback is fine
        fa = 1.0                               # <-- throws the real alpha away

The glyphs' fill colour is literally black, so every fade step took that
branch.  `fa` is the mobject's measured fill opacity (0 while FadeIn has it
faded out), and forcing it to 1.0 made `fill_alpha = min(1, fa * a)` = 1.0
with `a = 1.0` (RTM's `_anim_opacity` registry defaults to 1.0; manim's FadeIn
communicates opacity through `fill/stroke_rgbas`, not through that registry).
The colour then comes from `get_color()`, which returns the STROKE colour
(#FFFFFF) while fill_opacity is exactly 0 -- hence a full-bright WHITE digit.
On frames 1..N fill_opacity > 0 so `get_color()` returns the fill colour
(black) and the same bug draws an invisible black digit, which is why only
frame 0 was visibly wrong.

Pure Python: captures the DLL calls, no GPU, no ffmpeg, no DTW.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import BLUE, LEFT, UP, FadeIn, Graph
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


def _scene_graph():
    """The scene's first graph (scenes/05_mobject_classes.py, `undirected`)."""
    return Graph(
        [1, 2, 3, 4, 5, 6],
        [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)],
        labels=True,
        layout="circular",
        layout_scale=1.5,
        vertex_config={"radius": 0.12, "color": BLUE},
    ).scale(0.85)


class _Recorder(object):
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _call(*args, **kwargs):
            self.calls.append((name, args))
            return 0
        return _call


def _capture(mob):
    renderer = vb.MLWindow(854, 480)
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
    return counts, rec.calls


def _faded(alpha):
    """The scene's graph posed at `alpha` of its FadeIn."""
    graph = _scene_graph()
    anim = FadeIn(graph)
    anim.begin()
    anim.interpolate(alpha)
    return graph


def _glyph_alphas(graph):
    """The measured fill rgba alpha of every VMobjectFromSVGPath label glyph."""
    out = []

    def walk(m):
        if type(m).__name__ == "VMobjectFromSVGPath":
            out.append(float(m.get_fill_rgbas()[:, 3].max()))
        for s in m.submobjects:
            walk(s)

    walk(graph)
    return out


def test_glyph_fill_alpha_equals_its_own_rgba_alpha():
    """Red before the fix at alpha 0, 0.25 and 0.5: `fa` was forced to 1.0.

    `AddBezierPath` layout (vulkan_text.py:642):

        arr, n, sri,sgi,sbi, stroke_w, fri,fgi,fbi, fill_alpha,
        progress, 0, show_fill, a

    so fill_alpha must be ``min(1, own_rgba_alpha * a)`` -- the same rule the
    stroke side already follows (`stroke_alpha = min(1, so * a)`).
    """
    for alpha in (0.0, 0.25, 0.5, 1.0):
        graph = _faded(alpha)
        want = _glyph_alphas(graph)
        counts, calls = _capture(graph)
        bez = [a for n, a in calls if n == "AddBezierPath"]
        assert bez, "alpha %s: no glyph was sent at all: %r" % (alpha, counts)
        assert len(bez) == len(want), (
            "alpha %s: %d glyph paths for %d glyphs" % (alpha, len(bez), len(want)))
        for i, (args, rgba_a) in enumerate(zip(bez, want)):
            a = float(args[13])
            got = float(args[9])
            expect = min(1.0, rgba_a * a)
            assert abs(got - expect) < 1e-4, (
                "alpha %s, glyph %d: fill_alpha %.4f but its own fill rgba alpha "
                "is %.4f and the chain alpha is %.4f (expected %.4f) -- "
                "`_send_vmobject` overwrote the measured alpha with 1.0 when the "
                "fill colour is black" % (alpha, i, got, rgba_a, a, expect))


def test_fade_in_alpha_zero_requests_no_fill():
    """The flash itself: at FadeIn alpha 0 nothing may ask native to fill.

    `show_fill = 1 if fill_alpha > 0.01` (vulkan_text.py:596) -- so a correct
    alpha clears it, and the stroke is off anyway (stroke_w = 0 for a LaTeX
    glyph).  Anything left drawn here is the one-frame flicker.
    """
    graph = _faded(0.0)
    counts, calls = _capture(graph)
    offenders = [a for n, a in calls
                 if n == "AddBezierPath" and (int(a[12]) != 0 or float(a[9]) > 0.01)]
    assert not offenders, (
        "%d of %d glyph paths still request a fill at FadeIn alpha 0 "
        "(first: fill_alpha=%.4f show_fill=%d) -- that is the frame-0 flash; "
        "whole emission was %r" % (len(offenders), len(calls),
                                   float(offenders[0][9]), int(offenders[0][12]),
                                   counts))
    others = dict((n, c) for n, c in counts.items() if n != "AddBezierPath")
    assert not others, (
        "at FadeIn alpha 0 the graph emitted %r -- dots and edges must be gone "
        "with it" % others)


def test_fade_in_alpha_one_still_draws_everything():
    """Non-regression: at alpha 1 the six dots, six edges and six labels stay."""
    graph = _faded(1.0)
    counts, calls = _capture(graph)
    assert counts.get("AddCircle", 0) == 6, "dots: %r" % counts
    assert counts.get("AddLine", 0) == 12, "edges (6 x 2 layers): %r" % counts
    bez = [a for n, a in calls if n == "AddBezierPath"]
    assert len(bez) == 6, "labels: %r" % counts
    assert all(int(a[12]) == 1 for a in bez), (
        "the visible labels stopped requesting a fill: %r"
        % [int(a[12]) for a in bez])
