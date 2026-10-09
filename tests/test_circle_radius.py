"""A `Circle` must not change the radius RTM draws it with while it rotates.

Reported (user): "AnimationCompositionGroups中的橙色圆形在fade out之前有一瞬间
非正常的膨胀" -- the GOLD circle in
``Succession(Create, Rotate, FadeOut)`` inflates for an instant right before the
FadeOut.

Mechanism, measured on manim itself (`%TEMP%\\circle_layout.py`) and on the two
rendered videos (`%TEMP%\\gold_diag.py`, `%TEMP%\\slice_diag.py`):

    fresh Circle      n=32  width=1.100000  width*60=66.0000   d_min=0.550000
    Rotate alpha=0.556      n=32  width=1.137870  width*60=68.2719   d_min=0.550000
    Rotate alpha=0.778      n=32  width=1.100000  width*60=66.0000   d_min=0.550000

``Mobject.width`` is the bounding box of **every** point in ``mob.points``,
including the off-curve bezier handles, and for a manim circle those handles sit
at ``d = 0.569015`` while the on-curve anchors stay at ``d = 0.550000``.
``Rotate`` is a ``Transform``: ``interpolate_mobject`` sweeps the whole control
polygon around, so once every 45 deg a handle lines up with the x axis and

    width = 2 * 0.569015 = 1.138030   (vs 1.100000 = 2 * 0.55)

-- a **3.46 % bulge of the control polygon while the drawn curve never moves**
(``d_min``/``d_max`` are constant at 0.550000/0.569015 on every frame; CE's
rendered ring is a constant 68 px bbox for frames 37..44).

``_send_circle`` drew ``sr = (mob.width / 2) * (h/8)`` -- i.e. it followed the
handles, not the curve.  66.000 -> 68.272 px of radius, and with the stroke on
top the rendered ring went 70 px -> 72 px for the two frames where a handle
crosses the axis (measured: RTM bbox h = 68,68,68,69,**72,72**,68,69,68 over
frames 37..45 while CE's is 68 on every one of them).

This file pins the invariant the sender must keep: **the radius it emits is the
on-curve radius**, which is what manim strokes.  Pure Python, no ffmpeg, no DTW.
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
    from manim import GOLD, DOWN, PI, RIGHT, Circle, Rotate
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)

RADIUS = 0.55          # the circle under test
SCALE = 480 / 8.0      # h / 8 -- `_send_circle`'s scale_y
EXPECTED = RADIUS * SCALE      # 33.0 px
TOL = 0.05             # px; a rasteriser may not be exact, a 3.46% bulge is not
N_STEPS = 61


@pytest.fixture(scope="module")
def renderer():
    try:
        r = vb.MLWindow(854, 480)
    except Exception as e:  # pragma: no cover
        pytest.skip("Vulkan window unavailable: %s" % e)
    yield r
    try:
        r.close()
    except Exception:
        pass


def walk_rotate():
    """Run one `Rotate` and yield the sampled state at every alpha.

    Yields ``(width, on_curve_radius, emitted_radius_or_None)``.
    """
    circle = Circle(radius=RADIUS, color=GOLD).shift(RIGHT * 4.2 + DOWN * 0.4)
    anim = Rotate(circle, angle=PI / 2, run_time=0.3)
    anim.begin()
    for i in range(N_STEPS + 1):
        anim.interpolate(i / N_STEPS)
        pts = np.asarray(circle.points, dtype=float)
        ctr = np.asarray(circle.get_center(), dtype=float)
        d = np.linalg.norm(pts[:, :2] - ctr[:2], axis=1)
        oncurve = float(np.linalg.norm(
            np.asarray(circle.get_start(), dtype=float)[:2] - ctr[:2]))
        yield float(circle.width), oncurve, float(d.min()), float(d.max()), circle


def test_control_polygon_bulges_but_the_curve_does_not(renderer):
    """Mechanism pin: manim's own numbers, independent of any RTM code.

    If this ever stops being true the root cause documented in this file is
    stale, and the sender fix must be re-derived rather than simply kept.
    """
    widths, oncurve, dmins, dmaxs = [], [], [], []
    for w, oc, lo, hi, _c in walk_rotate():
        widths.append(w)
        oncurve.append(oc)
        dmins.append(lo)
        dmaxs.append(hi)
    # the control polygon really does swell (this is manim, not RTM)
    assert max(widths) - min(widths) > 2.0 * RADIUS * 0.03, (
        "control polygon no longer bulges; re-derive the root cause "
        "(min width=%r max width=%r)" % (min(widths), max(widths)))
    # ... while the curve, and manim's own path start, never move
    assert max(oncurve) - min(oncurve) < 1e-9, (
        "on-curve radius moved (min=%r max=%r)" % (min(oncurve), max(oncurve)))
    assert oncurve[0] == pytest.approx(RADIUS, abs=1e-9)
    assert max(dmins) - min(dmins) < 1e-9
    assert max(dmaxs) - min(dmaxs) < 1e-9


def test_send_circle_radius_follows_the_curve_not_the_handles(renderer):
    """The reported bug: no frame may emit a radius other than the true one."""
    orig = renderer.dll.AddCircle
    rec = []

    def _cap(*a):
        rec.append(float(a[2]))              # AddCircle(x, y, r, ...)
        return 0

    renderer.dll.AddCircle = _cap
    try:
        for _w, _oc, _lo, _hi, circle in walk_rotate():
            renderer._send_circle(circle, 1.0, 854, 480, 0.0, None)
    finally:
        renderer.dll.AddCircle = orig

    assert rec, "_send_circle emitted no AddCircle"
    worst = max(rec, key=lambda r: abs(r - EXPECTED))
    assert abs(worst - EXPECTED) <= TOL, (
        "circle radius follows the bezier control handles instead of the curve: "
        "emitted radii min=%.4f max=%.4f, expected %.4f (+/- %.2f) px; "
        "worst frame %.4f (+%.2f%%).  During Rotate the control polygon's "
        "bounding box grows 1.100000 -> 1.137870 because an off-curve handle "
        "sweeps onto the x axis; the drawn curve stays at r=0.55."
        % (min(rec), max(rec), EXPECTED, TOL, worst,
           100.0 * (worst - EXPECTED) / EXPECTED))
