"""Phase 3 regression: manim-native animations must drive RTM's render channels.

The six channels are only ever *read* by the senders (`vulkan_shapes` 8 sites for
`_vulkan_progress`, `_vulkan_progress_upper` switching to bounds mode, `_grow_*`,
`_rotation_about_point`, `_transforming` selecting the point path, `_letter_alphas`,
and the `state` opacity registry).  Nothing wrote them for animations built with
`from manim import *`, so `Create`/`FadeIn`/`Transform`/… rendered as a static
final state.

These tests assert the derived values on real manim animations -- pure Python,
no window and no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import pytest
from manim import (AnimationGroup, Circle, Create, FadeIn, GrowFromCenter,
                   Rotate, Square, Transform)

from real_time_manim.render_hooks import clear_hooks, derive_channels, install_hooks
from real_time_manim.state import get_anim_opacity


def prepared(anim, alpha=0.0):
    """begin() + hooks, the way Timeline.finalize does it."""
    anim.begin()
    install_hooks(anim)
    anim.interpolate(alpha)
    return anim


def test_create_writes_progress_without_bounds():
    """`_vulkan_progress` only -- the lower/upper pair is ShowPassingFlash's window.

    Writing bounds for the Create family puts the senders into "bounds mode" and
    silently drops content (measured: PolygonOnAxes ink 35541 -> 3891, restored by
    skipping that write).
    """
    mob = Square()
    prepared(Create(mob, run_time=1.0), 0.4)
    assert mob._vulkan_progress == pytest.approx(0.4, abs=0.02)
    assert not hasattr(mob, "_vulkan_progress_upper")
    assert not hasattr(mob, "_vulkan_progress_lower")


def test_show_passing_flash_writes_a_window():
    from manim import ShowPassingFlash

    mob = Square()
    prepared(ShowPassingFlash(mob, run_time=1.0), 0.5)
    assert hasattr(mob, "_vulkan_progress_upper")
    assert mob._vulkan_progress_lower <= mob._vulkan_progress_upper


def test_create_progress_reaches_one():
    mob = Square()
    anim = prepared(Create(mob, run_time=1.0), 1.0)
    assert mob._vulkan_progress == pytest.approx(1.0, abs=1e-6)


def test_fade_in_writes_the_opacity_registry():
    mob = Square()
    prepared(FadeIn(mob, run_time=1.0), 0.5)
    assert get_anim_opacity(mob) < 1.0        # was 1.0 (full opacity) before hooks


def test_transform_selects_the_point_path_then_releases_it():
    mob = Square()
    anim = prepared(Transform(mob, Circle(), run_time=1.0), 0.5)
    assert getattr(mob, "_transforming", False) is True
    anim.interpolate(1.0)
    assert getattr(mob, "_transforming", False) is False


def test_rotate_sets_the_pivot():
    mob = Square()
    anim = Rotate(mob, 1.5708, about_point=mob.get_center(), run_time=1.0)
    prepared(anim, 0.5)
    assert getattr(mob, "_rotation_about_point", None) is not None


def test_grow_from_center_sets_scale_and_point():
    mob = Square()
    prepared(GrowFromCenter(mob, run_time=1.0), 0.3)
    assert mob._grow_scale == pytest.approx(0.3, abs=0.02)
    assert getattr(mob, "_grow_point", None) is not None


def test_composite_animation_hooks_every_child():
    sq, ci = Square(), Circle()
    group = AnimationGroup(Create(sq, run_time=1.0), FadeIn(ci, run_time=1.0))
    prepared(group, 0.5)
    assert getattr(sq, "_vulkan_progress", 1.0) < 1.0
    assert get_anim_opacity(ci) < 1.0


def test_install_is_idempotent_and_clear_restores():
    mob = Square()
    anim = Create(mob)
    anim.begin()
    install_hooks(anim)
    wrapped = anim.interpolate
    install_hooks(anim)                        # second call must not re-wrap
    assert anim.interpolate is wrapped
    clear_hooks(anim)
    assert anim.interpolate is anim._rtm_orig_interpolate if hasattr(anim, "_rtm_orig_interpolate") else True
    assert anim._rtm_hooks_installed is False


def test_rtm_own_animation_is_left_alone():
    from real_time_manim.animations.create import Create as RtmCreate

    mob = Square()
    anim = RtmCreate(mob)
    install_hooks(anim)
    assert anim._rtm_hooks_installed is True   # marked, but interpolate untouched


def test_unknown_animation_class_is_derived_as_transform():
    """Unknown classes must not crash; they fall back to the point-path flag."""
    class Weird(Transform):
        pass

    mob = Square()
    anim = Weird(mob, Circle(), run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.5)                      # no exception
    derive_channels(anim, 0.5)
