# -*- coding: utf-8 -*-
"""A remover must not leave the mobject in "erased" render state.

RTM's draw channels (``_vulkan_progress``, the bounds window, the partial tag,
``_letter_alphas``, the animated-opacity registry) exist only for the renderer;
a CE mobject carries none of them, and ``ShowPartial.clean_up_from_scene``
restores the whole path.  RTM's removers used to end with the channel parked at
"hidden" and never release it, so showing the SAME mobject again later drew
nothing:

* ``Uncreate(Square)`` left ``_vulkan_progress = 0.0`` -- a following
  ``FadeIn(Square)`` submitted zero shape calls;
* ``Unwrite(Text)`` left ``_letter_alphas = {0: 0.0, ...}`` -- a following
  ``add``/``Write`` was blank;
* ``FadeOut`` left the opacity registry at 0.0.

Pure Python -- no GPU work needed for the channel assertions.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim                                     # noqa: F401
    from manim import Square, Text
    from real_time_manim.animations import FadeIn, FadeOut, Uncreate, Unwrite
    from real_time_manim.animations.base import (get_anim_opacity,
                                                 release_hidden_channels)
except Exception as e:                                          # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


def _run(anim):
    anim.begin(0.0)
    anim.interpolate(0.5)
    anim.interpolate(1.0)
    anim.finish()
    return anim


def test_uncreate_releases_the_draw_channel():
    sq = Square(side_length=1.0, fill_opacity=1.0)
    _run(Uncreate(sq, run_time=1.0))
    assert getattr(sq, "_vulkan_progress", 1.0) == 1.0, (
        "a finished Uncreate must leave the shape drawable whole again")
    assert not getattr(sq, "_vulkan_points_partial", False)
    assert not hasattr(sq, "_vulkan_progress_upper")


def test_unwrite_releases_letter_alphas():
    txt = Text("abc")
    _run(Unwrite(txt, run_time=1.0))
    assert not hasattr(txt, "_letter_alphas"), (
        "a finished Unwrite must not pin the glyphs at alpha 0")


def test_fade_out_releases_the_opacity_registry():
    sq = Square(side_length=1.0, fill_opacity=1.0)
    _run(FadeOut(sq, run_time=1.0))
    assert get_anim_opacity(sq) == pytest.approx(1.0), (
        "a finished FadeOut must not leave the mobject faded out: re-adding it "
        "has to show it whole, like CE")


def test_release_is_idempotent_and_covers_the_family():
    from manim import Circle, VGroup
    grp = VGroup(Square(side_length=1.0, fill_opacity=1.0),
                 Circle(radius=0.5, fill_opacity=1.0))
    grp._vulkan_progress = 0.0
    grp._letter_alphas = {0: 0.0, 1: 0.0}
    for sub in grp:
        sub._vulkan_progress = 0.0
        sub._vulkan_points_partial = True
    release_hidden_channels(grp)
    release_hidden_channels(grp)              # idempotent
    for sub in [grp] + list(grp):
        assert getattr(sub, "_vulkan_progress", 1.0) == 1.0
        assert not getattr(sub, "_vulkan_points_partial", False)
    assert not hasattr(grp, "_letter_alphas")
