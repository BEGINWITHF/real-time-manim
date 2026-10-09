"""A point-path stroke must carry manim's stroke opacity as *alpha*, not colour.

Background
----------
The native pipeline blends straight-alpha:

    vulkan_init.c:633  srcColorBlendFactor = VK_BLEND_FACTOR_SRC_ALPHA
    vulkan_init.c:635  dstColorBlendFactor = VK_BLEND_FACTOR_ONE_MINUS_SRC_ALPHA
    ->  out = colour * alpha + dst * (1 - alpha)

and the bezier code already documents why the colour must never be scaled by
opacity (native/draw/draw_bezier.c:234-239):

    "Straight-alpha fill: colour stays full; opacity goes into alpha.
     Baking opacity into the colour (cr = fr * fo) made low-opacity fills
     render as BLACK instead of transparent -- the colour approached 0 while
     alpha stayed ~1."

`_send_vmobject`'s *fill* obeys that rule, but its *stroke* did not: it
submitted `colour * stroke_alpha` with a blend alpha of `a`.  Over the black
background that looks right, so the defect only shows where a fading stroke
crosses live ink.  Measured on `ApplyTransformAnimations` (report #3):

  frame 83  FadeTransform's source circle is at stroke opacity 0.154, the
            target square underneath at 0.846.  The circle is submitted as an
            OPAQUE (24,18,27) ring and, because native builds every
            AddLineStrip *after* every AddLine (vulkan_draw.c:89-90), that
            opaque ring lands on top of the square and replaces its outline
            where the two run tangent -> CE ink 442, RTM 269 (the middle of
            all four edges disappears).
  frame 85  the circle's stroke opacity has reached 0.006, `do_stroke` goes
            False, and the `_transforming` fallback then re-enabled it with
            `stroke_alpha = max(stroke_alpha, a)` where `a` is 1.0 (the
            animation registry deliberately stays 1.0 for a container
            animation, see `_is_container`) -> an OPAQUE bright ring is still
            painted over the finished square: CE ink 360, RTM 573.

Both are one defect: the point-path stroke ignores the mobject's own opacity.

Pure Python -- captures the DLL calls, no GPU work, no ffmpeg.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb
    from manim import Circle
except Exception as e:  # pragma: no cover - import guard
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


def _capture(mob):
    """Send `mob` through the real dispatch and return the captured DLL calls.

    Returns (linestrips, beziers); each entry is the raw arg tuple.
    """
    renderer = vb.MLWindow(400, 200)
    strips, beziers = [], []

    def _ls(*args):
        strips.append(args)
        return 0

    def _bez(*args):
        beziers.append(args)
        return 0

    renderer.dll.AddLineStrip = _ls
    renderer.dll.AddBezierPath = _bez
    try:
        renderer._send(mob)
    finally:
        renderer.close()
    return strips, beziers


def _fading_circle(opacity):
    """A circle that reaches `_send_vmobject` (the point path) with a stroke
    whose manim opacity is `opacity`."""
    c = Circle(radius=1.0)              # default stroke/fill colour: WHITE
    c.set_stroke(opacity=opacity)
    c.set_fill(opacity=0.0)
    c._transforming = True          # routes through the point path
    return c


def test_stroke_opacity_travels_in_the_alpha_channel():
    """Colour stays full, opacity becomes the blend alpha (straight alpha).

    Red before the fix: the colour came back premultiplied (255*0.15 = 38)
    while every vertex alpha was 1.0, i.e. an opaque grey-38 stroke -- which
    erases whatever it is drawn over instead of tinting it.
    """
    mob = _fading_circle(0.15)
    expected_rgb = tuple(round(float(v) * 255) for v in mob.get_stroke_rgbas()[0][:3])
    strips, _ = _capture(mob)
    assert strips, "expected the point path to submit a stroke"
    points, alphas, _n, _w, r, g, b, _global = strips[0]

    assert (r, g, b) == expected_rgb, (
        "stroke colour must stay full-strength; opacity belongs in the alpha, "
        "got rgb=(%d,%d,%d), want (%d,%d,%d)"
        % ((r, g, b) + expected_rgb))
    assert max(alphas) == pytest.approx(0.15, abs=0.02), (
        "vertex alpha must carry manim's stroke opacity, got %r" % max(alphas))


def test_no_forced_outline_on_a_mobject_manim_has_faded_out():
    """`_transforming` must not resurrect a stroke manim has faded to zero.

    Red before the fix: the fallback fired with `stroke_alpha = max(0, a)` and
    `a` is 1.0, so FadeTransform's vanishing source circle was still painted as
    an opaque ring over the target square (measured: frame 85 ink 573 vs CE 360).

    The fallback still exists for the case it was written for -- a morphing
    shape that *is* visible (through its fill) but carries no stroke of its own.
    """
    mob = _fading_circle(0.0)
    strips, _ = _capture(mob)
    assert not strips, (
        "a mobject with no stroke opacity and no fill opacity is invisible in "
        "manim and must stay invisible; got %d forced stroke submission(s)"
        % len(strips))


def test_visible_faded_stroke_still_draws_a_silhouette():
    """Keep the fallback's real job alive: visible fill, no stroke -> outline.

    Guards against "fix" that simply deletes the `_transforming` branch.
    """
    c = Circle(radius=1.0)
    c.set_stroke(opacity=0.0)
    c.set_fill(opacity=1.0)
    c._transforming = True
    strips, _ = _capture(c)
    assert strips, "a visible morphing shape still needs its silhouette"
    assert max(strips[0][1]) > 0.9
