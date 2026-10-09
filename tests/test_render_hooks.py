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

    The *value* is manim's eased bound rather than the raw alpha: `Create` runs
    with ``rate_func=smooth``, so 0.4 -> 0.2658.  See
    `test_progress_follows_manims_own_eased_bound` for why the raw alpha was wrong.
    """
    mob = Square()
    anim = prepared(Create(mob, run_time=1.0), 0.4)
    _lo, up = anim._get_bounds(anim.get_sub_alpha(0.4, 0, 1))   # manim's decision
    assert mob._vulkan_progress == pytest.approx(up)
    assert mob._vulkan_progress == pytest.approx(0.2658, abs=0.02)
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


def test_composite_children_keep_their_own_sub_alpha():
    """A composite must not re-derive its children from the GROUP's alpha.

    manim's ``AnimationGroup.interpolate`` already drives every started child
    with that child's *own* sub_alpha (composition.py:188-191), and
    ``install_hooks`` has wrapped each child, so those calls write correct
    channels.  The group's hook then called ``derive_channels(group, alpha)``
    *afterwards*; a composite matches no ``_RULES`` bucket, so it fell through
    to ``for sub in _children(anim): derive_channels(sub, alpha)`` and
    overwrote every child with the group's alpha.

    Two visible consequences, both reported on the demo suite:
      * ``Succession(Create, Rotate, FadeOut)`` on one circle: at group alpha
        0.5 the Create child had finished (sub_alpha 1.0) but was written back
        to 0.5, leaving the circle half-drawn while it should have been complete
        and rotating -- reported as "the orange circle's animation is wrong"
        (AnimationCompositionGroups).
      * a child whose start time has not been reached is never interpolated by
        manim at all, yet was still derived at the group's alpha, so it showed
        up before its turn.

    Lagged ``lag_ratio=0.4`` over three 1.0 s children gives
    starts [0, 0.4, 0.8], max_end_time 1.8, so group alpha 0.3 -> group time
    0.54 -> sub_alphas 0.54, 0.14 and child 2 unstarted.

    The channel is then *eased* from each child's own sub_alpha by that child's
    ``rate_func`` (see `test_progress_follows_manims_own_eased_bound`), so the
    assertions compare against manim's own bound and also prove the value is not
    the group's alpha.
    """
    a, b, c = Square(), Square(), Square()
    group = AnimationGroup(Create(a, run_time=1.0), Create(b, run_time=1.0),
                           Create(c, run_time=1.0), lag_ratio=0.4)
    group.begin()
    install_hooks(group)
    group.interpolate(0.3)

    for child, anim, sub_alpha in ((a, group.animations[0], 0.54),
                                   (b, group.animations[1], 0.14)):
        _lo, up = anim._get_bounds(anim.get_sub_alpha(sub_alpha, 0, 1))
        assert child._vulkan_progress == pytest.approx(up)
        _lo0, up0 = anim._get_bounds(anim.get_sub_alpha(0.3, 0, 1))
        assert child._vulkan_progress != pytest.approx(up0, abs=1e-3), (
            "child re-derived from the GROUP's alpha")
    # never begun by manim: must still hold its install-time start state
    assert c._vulkan_progress == pytest.approx(0.0, abs=1e-6)


def test_rtm_own_animation_is_left_alone():
    from real_time_manim.animations.create import Create as RtmCreate

    mob = Square()
    anim = RtmCreate(mob)
    install_hooks(anim)
    assert anim._rtm_hooks_installed is True   # marked, but interpolate untouched


def test_show_increasing_subsets_reveals_whole_submobjects():
    """`ShowIncreasingSubsets` must not be routed to the partial-draw channel.

    manim reveals submobjects by **binary whole-shape opacity**:
    ``index = int(floor(rate_func(alpha) * n))``, then ``set_opacity(1)`` for the
    prefix below ``index`` and ``set_opacity(0)`` for the rest
    (creation.py:527-541).  ``VMobject.set_opacity`` -> ``set_fill``/`set_stroke``
    writes ``fill_rgbas``/``stroke_rgbas``, which every sender already reads.

    ``_vulkan_progress`` means something entirely different: *partial path
    drawing*.  On a container ``vulkan_bind`` distributes it as
    ``sub_progress = clamp(p * N - i)`` (vulkan_bind.py:1339-1344), so feeding
    alpha 0.5 to a 3-shape group draws shape 1 **half** and leaves it visible,
    where CE has it entirely invisible.  That is the reported "some shapes are
    incomplete" (PartialAndSubsetAnimations).
    """
    from manim import ShowIncreasingSubsets, Triangle, VGroup

    grp = VGroup(Square(), Circle(), Triangle())
    anim = ShowIncreasingSubsets(grp, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.5)

    # partial-draw must NOT be engaged: the container keeps the default 1.0, so
    # vulkan_bind skips the clamp(p*N - i) distribution branch entirely.
    assert getattr(grp, "_vulkan_progress", 1.0) == pytest.approx(1.0)
    # CE's own contract: the reveal is binary, never fractional.
    assert [round(s.fill_opacity, 3) for s in grp] == [1.0, 0.0, 0.0]


def test_progress_follows_manims_own_eased_bound():
    """`_vulkan_progress` must carry manim's bound, not the raw alpha.

    manim applies ``rate_func`` and ``reverse_rate_function`` inside
    ``get_sub_alpha`` (animation.py:364-391) *before* ``_get_bounds``, and
    ``ShowPartial.interpolate_submobject`` then feeds that eased value to
    ``pointwise_become_partial``.  `_write_progress` called ``_get_bounds(alpha)``
    with the raw alpha instead, so the channel disagreed with the geometry manim
    had already cut -- measured with `probe_rate.py`: Create(Circle) off by 0.18
    and Uncreate(Circle) off by a full 1.00 (the two run in opposite directions).
    """
    from manim import Circle, Create, Uncreate

    for factory, alphas in ((Create, (0.25, 0.5, 0.75)),
                            (Uncreate, (0.0, 0.25, 0.75))):
        for alpha in alphas:
            anim = factory(Circle())
            anim.begin()
            install_hooks(anim)
            anim.interpolate(alpha)
            sub = anim.get_sub_alpha(alpha, 0, 1)
            _lo, up = anim._get_bounds(sub)        # manim's own decision
            assert anim.mobject._vulkan_progress == pytest.approx(up), (
                "%s at alpha %.2f: channel %.4f, manim %.4f"
                % (factory.__name__, alpha,
                   anim.mobject._vulkan_progress, up))


def test_uncreate_starts_full_not_empty():
    """The first frame of `Uncreate` must show the whole shape.

    Reported on AnimationCreationBasics (\"the circle's create animation is
    wrong\"): box-isolated circle ink, frame 25 = CE **589**, RTM **0**.
    manim starts `Uncreate` at bound 1.0 (``reverse_rate_function``), while the
    raw-alpha channel wrote 0.0, which the Circle dispatch turns into "draw
    nothing" (``vulkan_bind.py:1503`` only routes 0 < progress < 1 to the point
    path, and `_send_circle` returns on ``progress <= 0``).
    """
    from manim import Circle, Uncreate

    anim = Uncreate(Circle())
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.0)
    assert anim.mobject._vulkan_progress == pytest.approx(1.0)


def test_point_path_is_tagged_as_already_cut():
    """manim's truncated geometry must be tagged so the point path does not cut it twice.

    `_send_vmobject` walks ``mob.get_points()`` from 0 to ``_vulkan_progress``
    -- but for manim's own Create/Uncreate those points have *already* been
    shortened to manim's bound, so the sender drew ``progress * geometry``
    instead of ``geometry`` (measured: Uncreate rises to a mid-animation peak
    and falls back to 0, which only a product can produce).  The tag lets the
    point path draw the cut geometry whole while the native/attribute senders
    keep reading the channel.
    """
    from manim import Circle, Create

    anim = Create(Circle())
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.5)
    assert getattr(anim.mobject, "_vulkan_points_partial", False) is True


def test_point_path_bounds_draw_the_cut_geometry_whole():
    """`point_path_bounds` returns (0, 1) once the points are already manim-cut.

    Untagged mobjects keep today's behaviour so RTM's own animations -- which
    never truncate the points and carry their partial state in the channel
    alone (`animations/create.py:15`) -- still compose the way they did.
    """
    from real_time_manim.vulkan_util import point_path_bounds

    from manim import Circle

    mob = Circle()
    mob._vulkan_progress = 0.4
    assert point_path_bounds(mob) == pytest.approx((0.0, 0.4))

    mob._vulkan_points_partial = True
    assert point_path_bounds(mob) == pytest.approx((0.0, 1.0))

    # an explicit bounds window (ShowPassingFlash) is an intentional clip and
    # must win over a stale tag from an earlier animation
    mob._vulkan_progress_lower = 0.25
    mob._vulkan_progress_upper = 0.75
    assert point_path_bounds(mob) == pytest.approx((0.25, 0.75))


def test_spiral_in_is_not_routed_to_the_progress_channel():
    """`SpiralIn` moves, rotates and fades **whole** shapes (creation.py:473-489).

    It never draws a partial path, so it has no business writing
    ``_vulkan_progress``; see `test_show_increasing_subsets_reveals_whole_submobjects`
    for the mechanism that turns that channel into incomplete shapes.
    """
    from manim import SpiralIn, Triangle, VGroup

    grp = VGroup(Square(), Circle(), Triangle())
    anim = SpiralIn(grp, run_time=1.0)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.5)
    assert getattr(grp, "_vulkan_progress", 1.0) == pytest.approx(1.0)


def test_add_text_letter_by_letter_is_a_binary_prefix():
    """`AddTextLetterByLetter` must reveal a **binary prefix**, not a fade.

    manim (creation.py:527-541) computes
    ``index = int(int_func(rate_func(alpha) * n))``, then ``set_opacity(1)``
    for the first `index` glyphs and ``set_opacity(0)`` for the rest: a glyph
    is either fully there or not there at all.

    RTM instead handed every glyph the same *continuous* alpha from
    `get_sub_alpha` -- with `lag_ratio == 0` that formula collapses to
    ``rate_func(alpha)`` for every index -- so `_send_text_write` faded the
    whole word in at once (invisible <= 0.001, filled at >= 0.8) instead of
    typing it.
    """
    from manim import AddTextLetterByLetter, Text

    txt = Text("Reveal")
    anim = AddTextLetterByLetter(txt, run_time=0.7, time_per_char=0.05)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.25)

    drawn = [s.fill_opacity > 0.5 for s in txt.submobjects]   # manim's verdict
    channel = [txt._letter_alphas.get(i, 0.0) > 0.5
               for i in range(len(txt.submobjects))]           # RTM's verdict
    assert 0 < sum(drawn) < len(drawn), "probe invalid: manim revealed nothing/part"
    assert channel == drawn


def test_untype_unreveals_a_binary_prefix():
    """`RemoveTextLetterByLetter`/`UntypeWithCursor` must remove a binary prefix.

    Both set ``reverse_rate_function=True`` (creation.py:614 and :835), and
    manim applies it in ``interpolate_mobject`` as ``value = 1 - rate_func(alpha)``
    before ``index = int(int_func(value * n))`` (creation.py:527-541), so the
    word starts full and loses one glyph at a time.

    manim's ``get_sub_alpha`` does handle the reversal, so RTM's *value* is
    right for index 0 -- but because manim's ``DEFAULT_ANIMATION_LAG_RATIO`` is
    0 the formula yields the **same continuous number for every glyph**, so
    `_send_text_write` fades all of them together (fill_alpha = (v-0.3)*2) where
    CE pops a whole prefix.  At alpha 0.25 CE still shows 5 solid glyphs while
    RTM shows 6 near-solid ones and nothing at alpha 0.25's own 0.25 level.

    Reported as "typing animation logic error" (TextRevealAnimations, measured
    first_bad=38 = inside UntypeWithCursor's window, C+ 0.31 = RTM drawing
    glyphs CE had already removed, B 0.471 = CE ink RTM never reaches).
    """
    from manim import RemoveTextLetterByLetter, Text

    txt = Text("Reveal")
    anim = RemoveTextLetterByLetter(txt, run_time=0.7, time_per_char=0.05)
    anim.begin()
    install_hooks(anim)
    anim.interpolate(0.25)

    drawn = [s.fill_opacity > 0.5 for s in txt.submobjects]
    channel = [txt._letter_alphas.get(i, 0.0) > 0.5
               for i in range(len(txt.submobjects))]
    assert 0 < sum(drawn) < len(drawn), "probe invalid: manim revealed nothing/part"
    assert channel == drawn
    # the direction is genuinely reversed: at alpha 0.25 most glyphs are still up
    assert sum(drawn) > len(drawn) / 2


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
