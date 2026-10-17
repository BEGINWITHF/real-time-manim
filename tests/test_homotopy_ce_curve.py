# -*- coding: utf-8 -*-
"""Homotopy must deform the CURVE, not just its four anchors (CE parity).

Background -- wiki `03-动画/移动与旋转/02-沿路径与同态变换-homotopy`
(`assets/RTM code/02-沿路径与同态变换.py`, scene `HomotopyDemo`):

    def wave(x, y, z, t):
        return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)
    win.play(Homotopy(wave, rect, run_time=2.0, rate_func=linear))

The rectangle spans x in [-2.2, 2.2], i.e. 1.5 wavelengths of that wave.  RTM's
``Homotopy`` used to run the function over the raw control points, so the two
handles of the top edge -- which manim puts ON the straight edge at
x = +/-0.733 -- were moved to the wave's value *there*, i.e. to the opposite
side of the anchors from where the curve needs them.  The cubic then collapsed
to a nearly straight chord: measured on the rendered clip the centre column of
the rectangle never moved (top edge pinned at y=148 at 480x270 while Manim CE
swings 114..183), mean|diff| 2.303 with 42/210 bad frames -- the worst clip of
the folder.

manim CE does not work that way.  ``VMobject.apply_function`` -- which CE's
``Homotopy.interpolate_submobject`` calls every frame -- first pulls every
bezier handle to ``pre_function_handle_to_anchor_scale_factor`` (0.01) of its
distance from its anchor, applies the function to all points, then pushes the
handles back out by ``1 / factor``.  The handle therefore carries the image of
a point 1 % along the edge, extrapolated 100x, and the stroked curve follows
the homotopy of the *curve*.

These tests pin RTM's ``Homotopy`` to CE's own numbers and, independently of
manim, that the deformed curve really swings instead of flattening.

Run with::

    python -X utf8 -m pytest tests/test_homotopy_ce_curve.py -q
"""

import numpy as np
import pytest

from manim import Mobject, Rectangle, Circle, Square, YELLOW, DOWN, linear

import real_time_manim.animations.homotopy as rtm_homotopy
from real_time_manim.vulkan_bind import Homotopy

RUN_TIME = 2.0


def wave(x, y, z, t):
    """The wiki's homotopy function, verbatim."""
    return (x, y + 0.45 * np.sin(2.2 * x + 2.0 * np.pi * t), z)


def rtm_deformed(factory, alpha, **kwargs):
    mob = factory()
    anim = Homotopy(wave, mob, run_time=RUN_TIME, rate_func=linear, **kwargs)
    anim.begin(0.0)
    anim.interpolate(alpha * RUN_TIME)
    return np.asarray(mob.points, dtype=float).copy()


def ce_deformed(factory, alpha, **kwargs):
    from manim.animation.movement import Homotopy as CeHomotopy
    mob = factory()
    anim = CeHomotopy(wave, mob, run_time=RUN_TIME, rate_func=linear, **kwargs)
    anim.begin()
    anim.interpolate(alpha)
    return np.asarray(mob.points, dtype=float).copy()


def wiki_rectangle():
    return (Rectangle(width=4.4, height=1.6, color=YELLOW)
            .set_fill(YELLOW, 0.35).shift(DOWN * 1.2))


# --------------------------------------------------------------------------- #
# CE parity
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("factory,label", [
    (wiki_rectangle, "Rectangle"),
    (lambda: Square(side_length=2).shift(DOWN), "Square"),
    (lambda: Circle(radius=1.2).shift(DOWN), "Circle"),
])
@pytest.mark.parametrize("alpha", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_homotopy_points_match_manim_ce(factory, label, alpha):
    """RTM must produce exactly the points manim CE produces.

    Red before the fix: the handles differ (RTM put them at the raw wave value,
    CE extrapolates them 100x), e.g. at alpha 0.5 the Rectangle's first handle
    reads -0.85 in RTM against 0.208 in CE.
    """
    got = rtm_deformed(factory, alpha)
    want = ce_deformed(factory, alpha)
    assert got.shape == want.shape, (
        "%s: point count differs from CE (%s vs %s)" % (label, got.shape, want.shape))
    assert np.allclose(got, want, atol=1e-9), (
        "%s alpha=%.2f: RTM's Homotopy no longer matches manim CE's.\n"
        "RTM y: %s\nCE  y: %s"
        % (label, alpha, np.round(got[:, 1], 4).tolist(),
           np.round(want[:, 1], 4).tolist()))


def test_homotopy_pivot_kwargs_match_manim_ce():
    """``apply_function_kwargs`` must keep CE's pivot semantics too."""
    kw = {"apply_function_kwargs": {"about_point": [1.0, -2.0, 0.0]}}
    got = rtm_deformed(wiki_rectangle, 0.35, **kw)
    want = ce_deformed(wiki_rectangle, 0.35, **kw)
    assert np.allclose(got, want, atol=1e-9), (
        "about_point homotopy diverged from CE:\nRTM y: %s\nCE  y: %s"
        % (np.round(got[:, 1], 4).tolist(), np.round(want[:, 1], 4).tolist()))


# --------------------------------------------------------------------------- #
# the shape itself: the curve must swing
# --------------------------------------------------------------------------- #

def cubic_points(p0, p1, p2, p3, samples=201):
    ts = np.linspace(0.0, 1.0, samples)[:, None]
    return ((1 - ts) ** 3 * p0 + 3 * (1 - ts) ** 2 * ts * p1
            + 3 * (1 - ts) * ts ** 2 * p2 + ts ** 3 * p3)


def top_edge_curve(pts, samples=201):
    """The stroked top edge: the cubic through the first four points."""
    return cubic_points(*[np.asarray(pts[i], dtype=float) for i in range(4)],
                        samples=samples)


def y_at_x(curve, x=0.0):
    i = int(np.argmin(np.abs(curve[:, 0] - x)))
    return float(curve[i, 1])


@pytest.mark.parametrize("alpha", [0.25, 0.75])
def test_deformed_curve_swings_instead_of_flattening(alpha):
    """The centre of the top edge must actually move.

    At alpha 0.25 / 0.75 the wave peaks at x = 0, so the drawn curve has to be
    ~0.5+ units away from the straight edge it started on.  With the old raw
    control-point mapping the handles counter-swing the anchors and the cubic
    stays within 0.05 units of its chord -- the "deformation barely moves" bug.
    """
    pts = rtm_deformed(wiki_rectangle, alpha)
    curve = top_edge_curve(pts)
    y0 = y_at_x(curve)
    # the rectangle's top edge starts at y = -0.4 (width 4.4, height 1.6,
    # shifted DOWN * 1.2)
    assert abs(y0 - (-0.4)) > 0.5, (
        "the deformed top edge at x=0 is only %.3f units from its rest "
        "position -- the homotopy no longer bends the curve" % y0)

    # the same mapping WITHOUT the handle dance is the pre-fix behaviour
    raw = np.asarray(wiki_rectangle().points, dtype=float)
    rtm_homotopy.apply_homotopy_to_points(
        raw, lambda x, y, z: wave(x, y, z, alpha), factor=None)
    raw_curve = top_edge_curve(raw)
    assert abs(y_at_x(raw_curve) - (-0.4)) < 0.15, (
        "the raw control-point mapping now bends the curve by more than "
        "expected (%.3f); this test's control case is stale"
        % y_at_x(raw_curve))


def test_handles_are_extrapolated_not_evaluated_at_the_handle():
    """The CE mechanism itself: the handle is NOT the wave value at its x.

    For the wiki rectangle at alpha 0.5 CE's first top handle sits at
    y = 0.208 (the wave's value at x = 0.733 would be -0.85).  Pinning the sign
    keeps the collapse/expand dance from silently reverting to the raw map.
    """
    pts = rtm_deformed(wiki_rectangle, 0.5)
    anchor_dy = pts[0][1] - (-0.4)
    handle_dy = pts[1][1] - (-0.4)
    assert anchor_dy > 0.4, "anchor did not follow the wave"
    assert handle_dy > anchor_dy, (
        "the handle landed at %+.3f while its anchor moved %+.3f -- it looks "
        "like the handles are being evaluated raw again instead of collapsed "
        "and extrapolated like manim CE does" % (handle_dy, anchor_dy))


# --------------------------------------------------------------------------- #
# non-bezier mobjects keep the plain mapping
# --------------------------------------------------------------------------- #

def test_point_cloud_mobject_keeps_the_plain_mapping():
    """A mobject with points but no bezier layout gets the raw map (as CE)."""
    mob = Mobject()
    mob.points = np.array([[0.0, 0.0, 0.0], [1.0, -1.2, 0.0], [2.0, 0.5, 0.0]])
    anim = Homotopy(wave, mob, run_time=RUN_TIME, rate_func=linear)
    anim.begin(0.0)
    anim.interpolate(0.25 * RUN_TIME)
    got = np.asarray(mob.points, dtype=float)
    expect = np.array([wave(*p, 0.25) for p in
                       np.array([[0.0, 0.0, 0.0], [1.0, -1.2, 0.0], [2.0, 0.5, 0.0]])])
    assert np.allclose(got, expect, atol=1e-9)


def test_interpolate_does_not_mutate_the_snapshot():
    """Every frame re-derives from the snapshot (no cumulative drift)."""
    mob = wiki_rectangle()
    snap = np.asarray(mob.points, dtype=float).copy()
    anim = Homotopy(wave, mob, run_time=RUN_TIME, rate_func=linear)
    anim.begin(0.0)
    for _ in range(5):
        anim.interpolate(0.5 * RUN_TIME)
    assert np.allclose(mob.points, rtm_deformed(wiki_rectangle, 0.5), atol=1e-9)
    anim.finish()
    assert np.allclose(mob.points, snap, atol=1e-9)
