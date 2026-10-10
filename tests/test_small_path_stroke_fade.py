"""A stroked path below 8 points must fade with its own stroke opacity.

Report R10-4 (batch item 1): "ArcsAndCurves -- the shape you just fixed
appears at the wrong time", i.e. the `CubicBezier` of the top row.

Measured, window x[715..760] y[85..130] (the curve sits at
`5.4 * RIGHT + 2.2 * UP`), lit = luma > 55, scene is 41 frames and
`FadeIn(top)` is run_time 0.8 s = 12 frames:

    frame        0    1    2    3    4    5    6    7    8    9   10   11   12
    CE lit       0    0    0    0    0  183  224  242  255  257  260  262  261
    RTM lit    292  292  292  292  292  292  292  292  292  292  292  292  292

CE is empty for five frames and then ramps; RTM is already at its final
value on frame 0 and never moves.

Root cause, `vulkan_text.py::_send_vmobject`, the `n < 8` stroke branch
(:451-468) -- the branch a 4-point `CubicBezier` is, being one cubic segment:

    sri = int(sr * 255 * a)          # RGB scaled by the CHAIN alpha only
    for chord: _emit_stroke(..., a)  # alpha = chain alpha only

`a = parent_alpha * get_anim_opacity(mob)` and `get_anim_opacity` is RTM's
registry defaulting to 1.0 (`state.py:25`); manim's `FadeIn` never writes it
-- the fade lives in `stroke_rgbas[:, 3]` (that is what report R10-3
established).  The branch never reads that value, while the `>= 8` branch
does: `stroke_alpha = min(1, so * a)` (vulkan_text.py:554).  So the curve was
stroked at full brightness from the first frame.

The fix multiplies the chain alpha by the stroke's own opacity for the alpha
that reaches `_emit_stroke`, leaving the RGB scaling by `a` exactly as it was
(that path is the container/progress registry, untouched), and skips the
stroke entirely when the result is invisible.

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
    from manim import LEFT, RIGHT, UP, CubicBezier, FadeIn
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


def _scene_bezier():
    """The `bezier` of ArcsAndCurves (scenes/05_mobject_classes.py:743)."""
    return CubicBezier(
        -1.0 * LEFT, -0.4 * LEFT + 0.9 * UP, 0.4 * RIGHT - 0.9 * UP, 1.0 * RIGHT
    ).move_to(5.4 * RIGHT + 2.2 * UP)


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
    """The scene's curve posed at `alpha` of its FadeIn."""
    bezier = _scene_bezier()
    anim = FadeIn(bezier)
    anim.begin()
    anim.interpolate(alpha)
    return bezier


def _stroke_opacity(bezier):
    return float(bezier.get_stroke_rgbas()[:, 3].max())


def _line_alphas(calls):
    # AddLine(x1, y1, x2, y2, w, r, g, b, a) -> alpha at index 8
    return [float(a[8]) for n, a in calls if n == "AddLine"]


def test_fade_in_alpha_zero_strokes_nothing():
    """Red before the fix: the curve was stroked at alpha 1.0 on frame 0."""
    bezier = _faded(0.0)
    counts, calls = _capture(bezier)
    lines = _line_alphas(calls)
    assert _stroke_opacity(bezier) <= 1e-6, "fixture: fade did not take"
    assert not lines, (
        "the CubicBezier was stroked at FadeIn alpha 0 (%d AddLine calls, "
        "max alpha %.3f, stroke opacity %.3f, emission %r) -- that is the "
        "'appears at the wrong time' defect: it must fade in with its own "
        "stroke_rgbas alpha, like the >=8-point branch does "
        "(stroke_alpha = min(1, so * a))"
        % (len(lines), max(lines) if lines else -1.0,
           _stroke_opacity(bezier), counts))


def test_fade_in_half_strokes_at_half():
    """Red before the fix: alpha stayed 1.0 for the whole fade."""
    bezier = _faded(0.5)
    counts, calls = _capture(bezier)
    lines = _line_alphas(calls)
    so = _stroke_opacity(bezier)
    assert lines, "no stroke at all at FadeIn alpha 0.5: %r" % counts
    assert max(lines) <= so + 0.02, (
        "stroke alpha %.3f but the mobject's own stroke opacity is only "
        "%.3f (chain alpha is 1.0) -- the `<8` branch ignored stroke_rgbas"
        % (max(lines), so))


def test_fade_in_alpha_one_strokes_at_full():
    """Non-regression: at alpha 1 the curve is stroked exactly as before."""
    bezier = _faded(1.0)
    counts, calls = _capture(bezier)
    lines = _line_alphas(calls)
    assert lines, "the curve stopped rendering entirely: %r" % counts
    assert max(lines) >= 0.98, (
        "at FadeIn alpha 1 the stroke came out at %.3f, expected ~1.0"
        % max(lines))
