"""Gap tests for RTM<->manim interop: A24, A25, A26, A27, A32.

Report pages (RTM-Wiki):

* **A24** -- manim's ``Succession``/``AnimationGroup`` could not hold RTM's
  own animations: the stale ``prepare_animation`` copies in composition.py
  raised ``TypeError: Object Wait(None) cannot be converted to an
  animation``, and manim's ``Add`` was not recognised by RTM's play pipeline
  at all (RTM only registers its own ``Add`` type into the scene).
* **A25** -- ``override_animation`` / ``use_override`` were never wired into
  RTM's own animation classes: ``vulkan_bind.FadeIn(MySquare())`` ignored a
  registered override.
* **A26** -- ``turn_animation_into_updater`` / ``cycle_animation`` died on
  RTM animations (``'Create' object has no attribute 'get_run_time'``)
  because they speak manim's alpha while RTM animations take elapsed time.
* **A27** -- ``.animate(lag_ratio=...)``: the keyword does reach the built
  animation and *does* stagger a mobject's submobjects (manim's own
  ``Animation.interpolate_mobject``), but on a mobject without submobjects it
  is inert -- RTM now warns instead of accepting it in silence.
* **A32** -- ``Broadcast``'s ``focal_point`` default is the mobject's centre
  (RTM divergence from CE's ORIGIN); explicit values, keyword *or*
  positional, are always respected.

Pure Python: stub scenes and a DLL-free PlayMixin window, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    import real_time_manim.vulkan_bind as vb          # noqa: F401  (applies patches)
    from manim import (
        ORIGIN,
        RIGHT,
        UP,
        Circle,
        Create as ManimCreate,
        FadeIn as ManimFadeIn,
        Scene,
        Square,
        VGroup,
        override_animation,
        override_animate,
    )
    from manim.animation import composition as manim_composition
    from manim.animation import speedmodifier as manim_speedmodifier
    from manim.animation.animation import Animation as ManimAnimation
    from manim.animation.composition import AnimationGroup as ManimAnimationGroup
    from manim.animation.composition import Succession as ManimSuccession
    from manim.animation.specialized import Broadcast
    from manim.animation.updaters.mobject_update_utils import (
        cycle_animation,
        turn_animation_into_updater,
    )
    import manim.animation.animation as manim_animation_module
    import manim.scene.scene as manim_scene_module

    from real_time_manim.animations import (
        Add as RtmAdd,
        AnimationGroup as RtmAnimationGroup,
        Create as RtmCreate,
        FadeIn as RtmFadeIn,
        Succession as RtmSuccession,
        Wait as RtmWait,
    )
    from real_time_manim.state import get_anim_opacity
    from real_time_manim.window import patches as rtm_patches
    from real_time_manim.window.play import PlayMixin
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


class StubScene:
    """A scene with just the surface the adapters touch."""

    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        self.mobjects.append(mob)

    def remove(self, mob):
        self.mobjects.remove(mob)

    def get_mobject_family_members(self):
        out = []
        for m in self.mobjects:
            out.extend(m.get_family())
        return out


class PlayStub(PlayMixin):
    """A play window with no DLL: the live branch of ``play()``."""

    _schedule_mode = False

    def __init__(self, scene):
        self.scene = scene
        self._fast_record = False
        self._cursor = 0.0

    def sync(self, scene):
        pass

    def tick(self):
        return True

    def _capture_frame(self):
        pass


# ---------------------------------------------------------------------------
# A24 -- manim composition classes accept RTM animations
# ---------------------------------------------------------------------------

def test_prepare_animation_is_rebound_wherever_imported_by_name():
    """composition.py / scene.py imported the ORIGINAL function by name."""
    patched = rtm_patches._patched_prepare_animation
    assert manim_composition.prepare_animation is patched
    assert manim_scene_module.prepare_animation is patched
    assert manim_speedmodifier.prepare_animation is patched
    assert manim_animation_module.prepare_animation is patched


def test_manim_succession_accepts_rtm_wait_and_add():
    """Used to raise "TypeError: Object Wait(None) cannot be converted...".

    The children come back as alpha/time adapters; the run_time is the sum.
    """
    succ = ManimSuccession(RtmWait(0.2), RtmAdd(Square()))
    assert succ.run_time == pytest.approx(0.2)
    for child in succ.animations:
        assert isinstance(child, rtm_patches._RtmAnimationAdapter)
        assert isinstance(child, ManimAnimation)      # manim machinery sees one


def test_manim_succession_drives_rtm_children_on_alpha_clock():
    """A nested RTM FadeIn must stay out of the scene, then fade on its slot.

    manim's Succession drives children with ``begin()`` / ``interpolate(alpha)``
    -- the adapter converts both to RTM's time semantics.
    """
    dot = Circle(radius=0.2)
    scene = StubScene()
    succ = ManimSuccession(RtmWait(0.2), RtmFadeIn(dot, run_time=0.4))

    succ._setup_scene(scene)                 # what _setup_anim_scene does
    succ.begin()
    assert dot not in scene.get_mobject_family_members(), (
        "the FadeIn's mobject was pre-added at play start instead of at its slot")

    succ.interpolate(0.2)                    # 0.2 * 0.6 s = 0.12 s -> Wait slot
    assert dot not in scene.get_mobject_family_members()

    succ.interpolate(0.5)                    # 0.30 s -> mid-FadeIn
    assert dot in scene.get_mobject_family_members()
    mid = get_anim_opacity(dot)
    assert 0.0 < mid < 1.0, mid

    succ.interpolate(1.0)
    succ.finish()                            # the timeline finishes plays too
    assert get_anim_opacity(dot) == pytest.approx(1.0)


def test_manim_animationgroup_drives_rtm_create():
    """The adapter honours the group's alpha clock (0.5 -> half progress)."""
    sq = Square()
    group = ManimAnimationGroup(RtmCreate(sq, run_time=1.0))
    group.begin()
    group.interpolate(0.5)
    assert 0.0 < getattr(sq, "_vulkan_progress", 0.0) < 1.0
    group.interpolate(1.0)
    group.finish()
    assert sq._vulkan_progress == pytest.approx(1.0)


def test_nested_manim_add_registers_and_reveals_on_its_slot():
    """manim's Add inside an RTM Succession: hidden until the slot runs."""
    from manim import Add as ManimAdd

    dot = Circle(radius=0.2)
    succ = RtmSuccession(RtmWait(0.2), ManimAdd(dot))

    mobs = PlayStub(Scene())._extract_add_mobjects(succ)
    assert mobs == [dot]
    assert dot._rtm_deferred_add is True
    assert get_anim_opacity(dot) == 0.0      # registered hidden

    succ.begin(0.0)
    succ.interpolate(0.3)                    # past the 0.2 s Wait -> Add slot
    assert get_anim_opacity(dot) == pytest.approx(1.0)


def test_top_level_manim_add_is_registered_by_play():
    """``win.play(manin.Add(x))`` used to die on the run_time validation.

    manim's Add is now recognised as an RTM Add everywhere in the play
    pipeline: excluded from the timed animations (so a 0 s run_time no longer
    fails CE's aggregate check) and registered into the scene instead.
    """
    from manim import Add as ManimAdd

    assert issubclass(ManimAdd, RtmAdd)      # re-based onto RTM's Add

    dot = Circle(radius=0.2)
    win = PlayStub(Scene())
    win.play(ManimAdd(dot))
    assert dot in win.scene.mobjects
    assert get_anim_opacity(dot) == pytest.approx(1.0)
    assert dot._rtm_deferred_add is False


def test_manim_add_carries_the_flat_mobjects_list():
    """RTM's extractor reads ``.mobjects``; manim's Add only had ``mobject``."""
    from manim import Add as ManimAdd

    a, b = Square(), Square().shift(RIGHT)
    add = ManimAdd(a, b)
    assert add.mobjects == [a, b]


def test_changespeed_wraps_rtm_group_through_the_adapter():
    """ChangeSpeed keeps working: it drives the adapter, which drives the
    group on a wall-clock origin (the group's own wrapper detector)."""
    from manim import ChangeSpeed, linear

    group = RtmAnimationGroup(RtmCreate(Square(), run_time=1.0))
    wrapper = ChangeSpeed(group, speedinfo={0.0: 1.0, 1.0: 1.0},
                          rate_func=linear)
    assert isinstance(wrapper.anim, rtm_patches._RtmAnimationAdapter)
    wrapper.begin()
    assert group.start_time > 1e6, "expected a wall-clock origin"
    wrapper.interpolate(0.5)
    wrapper.interpolate(1.0)
    wrapper.finish()        # also resets ChangeSpeed.is_changing_dt (class flag)


def test_manim_animation_default_scene_is_none_not_an_attributeerror():
    """A manim composite nested in an RTM composite never learns a scene."""
    assert ManimAnimation.scene is None
    succ = ManimSuccession(RtmWait(0.05))
    succ.begin()                              # slot activation touches .scene
    succ.interpolate(1.0)


# ---------------------------------------------------------------------------
# A25 -- override_animation / use_override wired into RTM's classes
# ---------------------------------------------------------------------------

def test_rtm_fadein_honours_override_animation():
    """An override keyed on manim's FadeIn applies to RTM's FadeIn too."""

    class MySquare(Square):
        @override_animation(ManimFadeIn)
        def _fade_in_override(self, **kwargs):
            return ManimCreate(self, **kwargs)

    anim = RtmFadeIn(MySquare())
    assert isinstance(anim, ManimCreate)
    assert not isinstance(anim, RtmFadeIn)


def test_use_override_false_keeps_the_rtm_class():
    class MySquare(Square):
        @override_animation(ManimFadeIn)
        def _fade_in_override(self, **kwargs):
            return ManimCreate(self, **kwargs)

    anim = RtmFadeIn(MySquare(), use_override=False)
    assert type(anim) is RtmFadeIn


def test_override_keyed_on_rtm_class_reaches_manim_animation():
    """The counterpart fallback is symmetric: manim's FadeIn finds an
    override written against RTM's FadeIn."""

    class MySquare(Square):
        @override_animation(RtmFadeIn)
        def _fade_in_override(self, **kwargs):
            return ManimCreate(self, **kwargs)

    anim = ManimFadeIn(MySquare())
    assert isinstance(anim, ManimCreate)
    assert not isinstance(anim, ManimFadeIn)


def test_overrides_do_not_leak_to_animation_subclasses():
    """manim's rule: an override for FadeIn does not apply to FadeIn
    subclasses -- and the name-based counterpart keeps that rule."""
    from manim import FadeIn as _ManimFadeIn

    class FadeInSubclass(_ManimFadeIn):
        pass

    class MySquare(Square):
        @override_animation(_ManimFadeIn)
        def _fade_in_override(self, **kwargs):
            return ManimCreate(self, **kwargs)

    plain = MySquare()
    assert isinstance(RtmFadeIn(plain), ManimCreate)
    sub = FadeInSubclass(plain)
    assert type(sub) is FadeInSubclass       # no override for the subclass


def test_override_animate_builder_returns_the_overridden_animation():
    """``@override_animate`` through ``.animate()`` -- RTM builds whatever
    manim's builder produced, and RTM's play knows manim animations."""
    from manim import Create as _Create

    class WithContent(VGroup):
        def clear(self):
            self.remove(self[-1])

        @override_animate(clear)
        def _clear_animation(self, anim_args=None):
            return _Create(self[-1], **(anim_args or {}))

    group = WithContent(Square(), Square().shift(RIGHT))
    anim = group.animate().clear().build()
    assert type(anim).__name__ == "Create"


# ---------------------------------------------------------------------------
# A26 -- turn_animation_into_updater / cycle_animation bridge the semantics
# ---------------------------------------------------------------------------

class _RecordingCreate(RtmCreate):
    """An RTM Create that records the times it is driven with."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_times = []

    def interpolate(self, t):
        self.seen_times.append(t - self.start_time)
        return super().interpolate(t)


def test_turn_animation_into_updater_drives_rtm_animation():
    mob = Square()
    anim = _RecordingCreate(mob, run_time=1.0)
    turn_animation_into_updater(anim)
    assert mob.updaters, "no updater was attached"

    for _ in range(7):                       # 7 * 1/60 s into a 1 s animation
        mob.update(1.0 / 60.0)
    assert anim.seen_times[0] == pytest.approx(0.0)
    assert anim.seen_times[1] == pytest.approx(1.0 / 60.0)
    assert all(0.0 <= t <= 1.0 + 1e-9 for t in anim.seen_times)

    for _ in range(60):                       # run past the end
        mob.update(1.0 / 60.0)
    assert not mob.updaters, "the updater was not popped on completion"
    assert anim.finished
    assert mob._vulkan_progress == pytest.approx(1.0)


def test_turn_animation_into_updater_snaps_zero_runtime_add():
    from manim import Add as ManimAdd

    mob = Square()
    anim = RtmAdd(mob, run_time=0.0)
    turn_animation_into_updater(anim)
    mob.update(1.0 / 60.0)
    assert not mob.updaters
    assert get_anim_opacity(mob) == pytest.approx(1.0)


def test_cycle_animation_keeps_cycling_rtm_animations():
    mob = Square()
    anim = _RecordingCreate(mob, run_time=0.5)
    cycle_animation(anim)
    for _ in range(40):                       # 0.67 s > 0.5 s run_time
        mob.update(1.0 / 60.0)
    assert mob.updaters, "a cycling updater removed itself"
    assert not anim.finished
    assert all(0.0 <= t <= 0.5 + 1e-9 for t in anim.seen_times)


def test_turn_animation_into_updater_keeps_manims_own_behaviour():
    """manim animations must fall through to the original helper."""
    mob = Square()
    anim = ManimCreate(mob, run_time=0.05)
    turn_animation_into_updater(anim)
    for _ in range(10):
        mob.update(1.0 / 60.0)
    assert not mob.updaters, "the manim path stopped completing"
    assert mob.get_num_points() > 0


# ---------------------------------------------------------------------------
# A27 -- .animate(lag_ratio=...)
# ---------------------------------------------------------------------------

def test_animate_lag_ratio_staggers_submobjects():
    """With submobjects the keyword is honoured (manim's own machinery),
    which is what RTM renders -- CE-identical."""
    group = VGroup(Square(), Square().shift(RIGHT), Square().shift(2 * RIGHT))
    anim = group.animate(lag_ratio=0.5).shift(UP).build()
    assert anim.lag_ratio == pytest.approx(0.5)
    anim.begin()
    anim.interpolate(0.35)
    ys = [float(sub.get_center()[1]) for sub in group.submobjects]
    assert ys[0] > ys[1] > ys[2], (
        "lag_ratio=0.5 must stagger the three children, got %r" % ys)


def test_animate_lag_ratio_warns_when_there_is_nothing_to_stagger():
    """A single mobject has no children: inert in CE too -- but RTM says so."""
    with pytest.warns(UserWarning, match="lag_ratio"):
        Square().animate(lag_ratio=0.5).shift(UP).build()


def test_animate_without_lag_ratio_stays_silent():
    import warnings as _warnings

    with _warnings.catch_warnings(record=True) as caught:
        _warnings.simplefilter("always")
        Square().animate(run_time=2.0).shift(UP).build()
    assert not [w for w in caught if "lag_ratio" in str(w.message)]


# ---------------------------------------------------------------------------
# A32 -- Broadcast.focal_point
# ---------------------------------------------------------------------------

def test_broadcast_default_focal_point_follows_the_mobject():
    """RTM's documented divergence from CE (ORIGIN) stays in place."""
    mob = Circle(radius=2).shift([1.0, 2.0, 0.0])
    broadcast = Broadcast(mob, n_mobs=3)
    assert list(broadcast.focal_point) == pytest.approx([1.0, 2.0, 0.0])


def test_broadcast_explicit_origin_is_respected():
    mob = Circle(radius=2).shift([1.0, 2.0, 0.0])
    broadcast = Broadcast(mob, focal_point=ORIGIN, n_mobs=3)
    assert list(broadcast.focal_point) == pytest.approx([0.0, 0.0, 0.0])


def test_broadcast_positional_focal_point_and_n_mobs_are_respected():
    """The old patch signature crashed on positional arguments:
    "takes from 2 to 3 positional arguments but 4 were given"."""
    mob = Circle(radius=2).shift([1.0, 2.0, 0.0])
    broadcast = Broadcast(mob, ORIGIN, 3)
    assert list(broadcast.focal_point) == pytest.approx([0.0, 0.0, 0.0])
    assert broadcast.n_mobs == 3


def test_broadcast_positional_none_still_defaults_to_the_mobject():
    mob = Circle(radius=2).shift([1.0, 2.0, 0.0])
    broadcast = Broadcast(mob, None)
    assert list(broadcast.focal_point) == pytest.approx([1.0, 2.0, 0.0])
