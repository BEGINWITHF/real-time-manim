"""Regression test: a single-family DrawBorderThenFill must not double-cut.

Report: wiki ``03-动画/创建与擦除/01-Create与画线族-border_fill.mp4`` -- "改色
时机错误".  The blue border of the orange Square was almost never drawn: at
frame 97 ManimCE inks 5970 blue pixels while RTM leaves the same pixels black,
because RTM only painted 40 % of the perimeter where CE paints 96 %.

Root cause (``render/hook_channels.py::_write_progress``): manim's
``DrawBorderThenFill.interpolate_submobject`` already CUTS the points -- phase 1
calls ``pointwise_become_partial(outline, 0, sub)`` and phase 2
``interpolate``s the full outline->starting geometry (creation.py:274-288) --
but the writer had no ``_get_bounds`` branch for it, so it fell into the
``else`` arm and stamped the raw ``alpha`` into ``_vulkan_progress`` with
``_vulkan_points_partial = False``.  ``point_path_bounds`` then returned
``(0.0, alpha)`` and the senders cut the ALREADY-cut contour a second time.

Measured drawn-contour fraction (whole outline = 972 px) against the CE
expectation ``min(1, 2 * get_sub_alpha(alpha))``:

    alpha     RTM before    RTM after     CE expect
    0.10        0.000         0.041         0.041
    0.20        0.100         0.266         0.266
    0.40        0.400         0.959         0.959
    0.60        0.600         1.000         1.000
    0.80        0.800         1.000         1.000

Fix: for a SINGLE-family DrawBorderThenFill/Write/Unwrite, mirror ``Create`` --
tag the family ``_vulkan_points_partial`` (draw the whole, already-cut path) and
set the channel to the fraction manim actually cut, ``min(1, 2 * sub_alpha)``.
A MULTI-family target (Write over a Text or VGroup, the 逐字 family) keeps the
raw-alpha channel: there ``_vulkan_progress`` is the stagger driver
``vulkan_bind`` spreads as ``clamp(p*N - i)``, and manim's per-sub eased values
cannot be expressed through it.  The tests below pin both directions.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from manim import BLUE, GREEN, ORANGE, RIGHT, Circle, Square, Text, VGroup
from manim.animation.creation import DrawBorderThenFill, Write

import real_time_manim.render.hooks as hooks


def _ce_cut_fraction(anim, alpha):
    """The contour fraction manim's DrawBorderThenFill reveals at ``alpha``.

    ``get_sub_alpha`` applies the rate function, then
    ``integer_interpolate(0, 2, sub_alpha)`` picks phase 1 (cut to
    ``2 * sub_alpha``) or phase 2 (full geometry), so the drawn fraction is
    ``min(1, 2 * sub_alpha)``.
    """
    sub_alpha = anim.get_sub_alpha(alpha, 0, 1)
    return min(1.0, 2.0 * sub_alpha)


def _drive(anim, alpha):
    hooks.install_hooks(anim)
    anim.begin()
    anim.interpolate(alpha)
    return anim.mobject


def test_single_square_border_fill_draws_the_eased_cut_not_alpha():
    """border_fill's Square must be drawn to the eased cut fraction, not ``alpha``."""
    sq = Square(side_length=1.8, color=ORANGE).set_fill(ORANGE, 1.0)
    anim = DrawBorderThenFill(sq, run_time=1.8, stroke_width=6,
                              stroke_color=BLUE, introducer=True)
    for alpha in (0.1, 0.2, 0.4, 0.6, 0.8):
        mob = _drive(anim, alpha)
        assert getattr(mob, "_vulkan_points_partial", False) is True, (
            "the already-cut contour was not tagged partial at alpha=%.2f: the "
            "senders will cut it a second time" % alpha)
        expected = _ce_cut_fraction(anim, alpha)
        got = float(mob._vulkan_progress)
        assert abs(got - expected) < 1e-6, (
            "channel %.4f != manim's cut %.4f at alpha=%.2f (raw alpha would be "
            "%.2f -- the double cut)" % (got, expected, alpha, alpha))


def test_single_circle_border_fill_tagged_partial():
    """Same rule for a Circle: its parametric sender must agree with the point path."""
    ci = Circle(radius=1.0, color=GREEN).set_fill(GREEN, 1.0)
    anim = DrawBorderThenFill(ci, run_time=1.8, stroke_width=6,
                              stroke_color=BLUE, introducer=True)
    for alpha in (0.3, 0.7):
        mob = _drive(anim, alpha)
        assert getattr(mob, "_vulkan_points_partial", False) is True
        assert abs(float(mob._vulkan_progress)
                   - _ce_cut_fraction(anim, alpha)) < 1e-6


def test_write_on_text_keeps_its_stagger_driver():
    """Non-regression: the 逐字 family keeps the raw-alpha stagger driver.

    A ``Text`` has glyph submobjects, so it is MULTI-family: ``_vulkan_progress``
    there is the stagger driver ``vulkan_bind`` spreads across glyphs, and the
    per-glyph reveal rides ``_letter_alphas``.  Rewriting the channel to the
    eased cut would retime every ``Write`` over text.
    """
    t = Text("Hello")
    anim = Write(t, run_time=1.5)
    for alpha in (0.3, 0.6):
        mob = _drive(anim, alpha)
        assert not getattr(mob, "_vulkan_points_partial", False), (
            "a Text Write was tagged partial; its glyphs must reveal through "
            "_letter_alphas, not a point-path cut")
        assert abs(float(mob._vulkan_progress) - alpha) < 1e-6, (
            "the stagger driver moved to %.4f at alpha=%.2f (expected the raw "
            "alpha) -- the 逐字 timing would change" % (mob._vulkan_progress, alpha))
        assert hasattr(mob, "_letter_alphas"), "the per-glyph map is missing"


def test_write_on_vgroup_keeps_its_stagger_driver():
    """Non-regression: a multi-square VGroup Write keeps the raw-alpha driver."""
    vg = VGroup(Square(), Square().shift(2 * RIGHT), Square().shift(4 * RIGHT))
    anim = Write(vg, run_time=1.5)
    for alpha in (0.3, 0.6):
        mob = _drive(anim, alpha)
        assert not getattr(mob, "_vulkan_points_partial", False)
        assert abs(float(mob._vulkan_progress) - alpha) < 1e-6
