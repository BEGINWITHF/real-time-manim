"""Composition gaps A10-A14 / A22 / A30: AnimationGroup & Succession.

Wiki references (``RTM-Wiki\\03-动画\\组合编排`` and ``03-动画\\淡入淡出``):

* **A10** -- ``AnimationGroup(..., run_time=...)`` raised ``TypeError``: the
  total duration was computed internally and ``**kwargs`` passed it to
  ``Animation.__init__`` a second time.  Now accepted, CE style: run_time
  overrides the automatic total and the WHOLE child schedule is stretched
  onto it (``_children_span`` stays the children's own span).
* **A11** -- ``AnimationGroup(group=...)`` was swallowed by ``**kwargs``.
  Now accepted: the container becomes ``.group`` / ``.mobject`` (manim sets
  ``self.mobject = self.group``) and answers ``get_all_mobjects()``.
* **A12** -- ``synchronize_with_wall_clock=...`` was swallowed.  RTM is
  frame-driven (TARGET_FPS/FRAME_DURATION) and its timeline must stay a pure
  function of time for ``render_at``/seek/record, so ``True`` is now rejected
  with a clear ``ValueError`` instead of being dropped; ``False`` is a no-op.
* **A13** -- RTM's own ``Succession`` ignored ``lag_ratio``; ``< 1`` overlaps
  were impossible.  ``Succession`` is now (as in manim) an ``AnimationGroup``
  with ``lag_ratio=1``, so ``start[i+1] = start[i] + run_time[i] * lag_ratio``
  applies.
* **A14** -- ``Succession(run_time=...)`` was popped and discarded.  Now
  honoured: it stretches/compresses the serial schedule (manim semantics).
* **A30** -- ``Succession`` with a ``Wait`` child counted 204 frames where CE
  counts 205 (wiki 组合编排/assets: 294 vs 295).  Root cause: the total was
  built with builtin ``sum`` (compensated on CPython >= 3.12 -> ``3.4``)
  while manim's ``np.add.accumulate`` gives ``3.4000000000000004``, and the
  frame count ``len(np.arange(0, run_time, 1/60))`` is 204 vs 205 across that
  boundary.  The schedule now accumulates naively, like CE.
* **A22** -- a page-swap ``AnimationGroup(FadeOut(old), FadeIn(n1, n2))``
  never showed the fade-in targets ("载体未进场景").  Verified end to end
  here through the real ``PlayMixin.play`` timeline (stub window, no DLL),
  plus the two structural holes the play-side walker's ONE-level recursion
  still had: nested groups, and manim's ``_setup_scene`` hook (which RTM's
  group did not implement at all).

Windowless: stub scene/window only -- no Vulkan, no ffmpeg.
"""
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

try:
    from manim import Circle, Group, Scene, Square, UP
    from real_time_manim.rate_functions import _smooth
    from real_time_manim.animations.animation_group import AnimationGroup
    from real_time_manim.animations.base import get_anim_opacity
    from real_time_manim.animations.create import Create
    from real_time_manim.animations.fade_in import FadeIn
    from real_time_manim.animations.fade_out import FadeOut
    from real_time_manim.animations.succession import Succession
    from real_time_manim.animations.add import Add
    from real_time_manim.animations.wait import Wait
    from real_time_manim.window.play import PlayMixin
    from real_time_manim.timeline import ce_frame_count
except Exception as e:                                  # pragma: no cover
    pytest.skip("manim/RTM unavailable: %s" % e, allow_module_level=True)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def _two_creates(lag=0.5, run_time=None):
    """Two 1.0 s RTM Creates in a group, begun on a zero-based clock."""
    a, b = Square(), Square()
    kwargs = {"lag_ratio": lag}
    if run_time is not None:
        kwargs["run_time"] = run_time
    grp = AnimationGroup(Create(a, run_time=1.0),
                         Create(b, run_time=1.0), **kwargs)
    grp.begin(0.0)
    return grp, a, b


def _progress(mob):
    return getattr(mob, "_vulkan_progress", None)


class StubScene:
    """Minimal scene for ``_setup_scene`` / presentation walks."""

    def __init__(self):
        self.mobjects = []

    def add(self, mob):
        if mob not in self.mobjects:
            self.mobjects.append(mob)

    def get_mobject_family_members(self):
        members = []
        for root in self.mobjects:
            members.extend(root.get_family())
        return members


class StubWindow(PlayMixin):
    """Just enough for ``PlayMixin._ensure_animated_present``."""

    def __init__(self, scene):
        self.scene = scene


class FakeWin(PlayMixin):
    """A whole ``win.play`` without a DLL: stubs the draw/tick side only."""

    _schedule_mode = False
    _fast_record = False
    _fast_record_fps = 60

    def __init__(self, scene):
        self.scene = scene
        self._cursor = 0.0
        self.dll = None
        self.frames = 0
        self.samples = []               # (opacity_ya, ya_in_scene) per frame

    def sync(self, scene):
        ya = getattr(self, "_probe", None)
        if ya is not None:
            self.samples.append(
                (get_anim_opacity(ya),
                 ya in scene.mobjects or
                 any(ya in r.get_family() for r in scene.mobjects)))

    def tick(self):
        self.frames += 1
        return True

    def _capture_frame(self):
        pass

    def screenshot(self, path):
        return path


def _present(anims):
    win = StubWindow(StubScene())
    PlayMixin._ensure_animated_present(win, anims)
    return win.scene


# --------------------------------------------------------------------------- #
# A10 -- run_time in the constructor
# --------------------------------------------------------------------------- #

def test_run_time_kwarg_no_longer_raises_type_error():
    """The reported failure: run_time reached ``Animation.__init__`` twice."""
    grp = AnimationGroup(Create(Square(), run_time=1.0),
                         Create(Square(), run_time=1.0),
                         lag_ratio=0.5, run_time=1.8)
    assert grp.run_time == pytest.approx(1.8)


def test_run_time_stretches_the_child_schedule():
    """CE: run_time overrides the total; children keep their own span.

    Two 1.0 s children with lag 0.5 have a 1.5 s span; over run_time=1.8 the
    span is mapped onto the whole run_time, so at t=0.9 (half) both children
    are partway through and at t=1.8 both are finished.
    """
    grp, a, b = _two_creates(lag=0.5, run_time=1.8)
    assert grp.run_time == pytest.approx(1.8)
    assert grp._children_span == pytest.approx(1.5)

    grp.interpolate(0.9)                       # half of run_time
    pa, pb = _progress(a), _progress(b)
    assert pa is not None and 0.0 < pa < 1.0, pa
    assert pb is not None and 0.0 < pb < 1.0, pb
    assert pa > pb, "the lagged child must trail the first one"

    grp.interpolate(1.8)                       # the full run_time
    assert _progress(a) == pytest.approx(1.0)
    assert _progress(b) == pytest.approx(1.0)


def test_run_time_none_keeps_the_automatic_total():
    """Backward compat: no run_time -> max end of the child schedule."""
    grp, _a, _b = _two_creates(lag=0.5)
    assert grp.run_time == pytest.approx(1.5)
    assert grp.run_time == pytest.approx(grp._children_span)


def test_attribute_assignment_still_stretches():
    """The wiki workaround ``ag.run_time = 1.8`` must keep working."""
    grp, a, b = _two_creates(lag=0.5)
    grp.run_time = 1.8
    assert grp.run_time == pytest.approx(1.8)
    grp.interpolate(1.8)                       # stretched to the new end
    assert _progress(a) == pytest.approx(1.0)
    assert _progress(b) == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# A11 -- group=
# --------------------------------------------------------------------------- #

def test_group_kwarg_is_accepted_as_the_container():
    """manim: ``self.mobject = self.group`` and ``get_all_mobjects()``."""
    keeper = Square()
    sq1, sq2 = Square(), Square()
    container = Group(sq1, sq2)
    grp = AnimationGroup(Create(sq1), Create(sq2), group=container)
    assert grp.group is container
    assert grp.mobject is container
    assert list(grp.get_all_mobjects()) == [sq1, sq2]


def test_group_container_is_presented_to_the_scene():
    """The explicit container reaches the scene through the play-side walk."""
    sq1, sq2 = Square(), Square()
    container = Group(sq1, sq2)
    grp = AnimationGroup(Create(sq1), Create(sq2), group=container)
    scene = _present([grp])
    assert container in scene.mobjects


def test_default_has_no_container():
    """Backward compat: without ``group=`` nothing changes."""
    sq = Square()
    grp = AnimationGroup(Create(sq))
    assert grp.mobject is None
    assert list(grp.get_all_mobjects()) == [sq]


# --------------------------------------------------------------------------- #
# A12 -- synchronize_with_wall_clock
# --------------------------------------------------------------------------- #

def test_synchronize_with_wall_clock_true_is_rejected():
    """Not silently swallowed: a clear error explaining the frame-driven clock."""
    with pytest.raises(ValueError) as exc:
        AnimationGroup(Create(Square()),
                       synchronize_with_wall_clock=True)
    msg = str(exc.value)
    assert "synchronize_with_wall_clock" in msg
    assert "wall clock" in msg or "墙钟" in msg


def test_synchronize_with_wall_clock_false_is_a_no_op():
    """The default value must stay accepted (manim/Gl signature compat)."""
    grp = AnimationGroup(Create(Square()),
                         synchronize_with_wall_clock=False)
    assert grp.run_time == pytest.approx(1.0)


def test_succession_rejects_synchronize_with_wall_clock_too():
    """``**kwargs 同 AnimationGroup`` -- same rejection through Succession."""
    with pytest.raises(ValueError):
        Succession(Create(Square()),
                   synchronize_with_wall_clock=True)


# --------------------------------------------------------------------------- #
# A13 -- Succession reads lag_ratio
# --------------------------------------------------------------------------- #

def test_succession_default_is_strictly_serial():
    """``lag_ratio=1``: the second child starts exactly when the first ends."""
    a, b = Square(), Square()
    succ = Succession(Create(a, run_time=1.0), Create(b, run_time=1.0))
    succ.begin(0.0)
    succ.interpolate(0.99)
    assert _progress(a) == pytest.approx(_smooth(0.99), abs=1e-6)
    assert _progress(b) is None, "child 2 started before child 1 finished"
    succ.interpolate(1.5)
    assert _progress(a) == pytest.approx(1.0)
    assert _progress(b) == pytest.approx(_smooth(0.5), abs=1e-6)


def test_succession_lag_ratio_below_one_overlaps():
    """The reported gap: ``lag_ratio=0.5`` must interleave the children.

    Children 1.0 s + 1.0 s with lag 0.5 -> span 1.5 s, second child starts at
    0.5 s; at t=1.0 it is half done while the first has finished.
    """
    a, b = Square(), Square()
    succ = Succession(Create(a, run_time=1.0), Create(b, run_time=1.0),
                      lag_ratio=0.5)
    assert succ.lag_ratio == pytest.approx(0.5)
    assert succ.run_time == pytest.approx(1.5)
    succ.begin(0.0)
    succ.interpolate(1.0)
    assert _progress(a) == pytest.approx(1.0)
    assert _progress(b) == pytest.approx(_smooth(0.5), abs=1e-6), (
        "with lag 0.5 the second child must run from t=0.5 (it used to be "
        "pushed to t=1.0, i.e. no overlap at all)")


def test_succession_lag_ratio_zero_is_parallel():
    a, b = Square(), Square()
    succ = Succession(Create(a, run_time=1.0), Create(b, run_time=1.0),
                      lag_ratio=0.0)
    assert succ.run_time == pytest.approx(1.0)
    succ.begin(0.0)
    succ.interpolate(0.5)
    assert _progress(a) == pytest.approx(_progress(b), abs=1e-9)
    assert _progress(a) == pytest.approx(_smooth(0.5), abs=1e-6)


# --------------------------------------------------------------------------- #
# A14 -- Succession(run_time=...)
# --------------------------------------------------------------------------- #

def test_succession_run_time_kwarg_is_honoured():
    """Requested 4.0 s for a 2.0 s serial schedule: whole schedule stretches."""
    a, b = Square(), Square()
    succ = Succession(Create(a, run_time=1.0), Create(b, run_time=1.0),
                      run_time=4.0)
    assert succ.run_time == pytest.approx(4.0)
    assert succ._children_span == pytest.approx(2.0)
    succ.begin(0.0)

    succ.interpolate(2.0)                      # half way
    assert _progress(a) == pytest.approx(1.0), "child 1 should be done"
    assert _progress(b) == pytest.approx(0.0), (
        "child 2 must only start at half of the stretched run_time")

    succ.interpolate(4.0)                      # end
    assert _progress(b) == pytest.approx(1.0)


def test_succession_run_time_none_is_the_children_sum():
    succ = Succession(Create(Square(), run_time=1.0),
                      Create(Square(), run_time=0.5))
    assert succ.run_time == pytest.approx(1.5)


# --------------------------------------------------------------------------- #
# A30 -- frame count of Succession(…, Wait, …) matches CE
# --------------------------------------------------------------------------- #

def test_succession_wait_composition_counts_ce_frames():
    """Wiki 组合编排/assets: RTM 294 vs CE 295 frames (one frame short).

    The demo's serial schedule is [1.0, 1.0, 0.6, 0.8].  CE sums it with
    ``np.add.accumulate`` -> ``3.4000000000000004``, whose arange at 60 fps
    is 205 frames; the builtin-``sum`` total used before was ``3.4`` (204
    frames) -- a whole frame across the ``arange`` boundary.
    """
    runs = [1.0, 1.0, 0.6, 0.8]
    succ = Succession(
        Create(Square(), run_time=1.0), Create(Square(), run_time=1.0),
        Wait(0.6),
        Create(Square(), run_time=0.8),
    )
    total = succ.run_time
    # naive left-to-right accumulation, exactly like np.add.accumulate
    acc = 0.0
    for r in runs:
        acc = acc + r
    assert total == acc, (repr(total), repr(acc))
    assert total != 3.4, "compensated builtin sum leaked back in"
    assert math.ceil(total * 60) == 205, "CE's ceil(run_time*60)口径"
    assert ce_frame_count([succ], total, 60) == 205, (
        "RTM must count 205 frames for this composition, like CE "
        "(204 was the 294-vs-295 discrepancy)")
    # ...and the boundary this pins: a total of exactly 3.4 counts 204.
    assert ce_frame_count([succ], 3.4, 60) == 204


# --------------------------------------------------------------------------- #
# A22 -- FadeIn carriers inside the RTM AnimationGroup
# --------------------------------------------------------------------------- #

def test_page_swap_group_shows_and_fades_in_its_targets_end_to_end():
    """The headline A22 bug, through the real ``PlayMixin.play`` pipeline.

    Before the fix the "换上" half never entered the scene: the fade-in
    targets stayed absent for the whole play AND the following frames (wiki
    03-动画/淡入淡出/assets: "连后面的 Wait 也不会冒出来").  Here they must be
    in the scene, start invisible, ramp up during the play and stay visible.
    """
    scene = Scene()
    old = Square().shift((-2.0, 0.0, 0.0))
    new1 = Square().shift((2.0, 0.0, 0.0))
    new2 = Circle(radius=0.4).shift((4.0, 0.0, 0.0))
    scene.add(old)

    group = AnimationGroup(FadeOut(old, shift=UP),
                           FadeIn(new1, new2), lag_ratio=0.0)
    win = FakeWin(scene)
    win._probe = new1
    win.play(group, run_time=1.2)

    assert win.samples, "the play never rendered a frame"
    first_op, first_in = win.samples[0]
    assert first_in, "the fade-in target never entered the scene (A22)"
    assert first_op == pytest.approx(0.0, abs=1e-6), (
        "FadeIn.begin must park the target at 0 at the first frame")
    mid_op, _ = win.samples[len(win.samples) // 2]
    assert 0.0 < mid_op < 1.0, "the target must FADE in, not pop: %r" % mid_op
    last_op, _ = win.samples[-1]
    assert last_op > 0.95, "the fade never completed: %r" % last_op

    # after the play the targets stay in the scene, fully visible
    for mob in (new1, new2):
        assert (mob in scene.mobjects or
                any(mob in r.get_family() for r in scene.mobjects)), (
            "%r left the scene after the play" % mob)
        assert get_anim_opacity(mob) == pytest.approx(1.0)


def test_page_swap_with_mans_fade_in_presents_targets_too():
    """The wiki demo imports ``FadeIn`` from the package (= manim's class).

    ``from real_time_manim import FadeIn`` resolves to the re-exported manim
    class; with an RTM ``AnimationGroup`` those children used to present
    nothing either (RTM's group had no ``_setup_scene`` for CE's introducer
    registration, and the play-side walk is what saves them today).
    """
    from manim.animation.fading import FadeIn as ManimFadeIn
    from manim.animation.fading import FadeOut as ManimFadeOut

    old = Square().shift((-2.0, 0.0, 0.0))
    new1 = Square().shift((2.0, 0.0, 0.0))
    new2 = Square().shift((4.0, 0.0, 0.0))
    scene = Scene()
    scene.add(old)

    group = AnimationGroup(ManimFadeOut(old, shift=UP),
                           ManimFadeIn(new1, new2), lag_ratio=0.0)
    win = FakeWin(scene)
    win._probe = None
    win.play(group, run_time=0.6)

    family = scene.get_mobject_family_members()
    assert new1 in family and new2 in family, (
        "manim FadeIn targets never entered the scene (A22)")
    # the manim child really ran (group began it through the manim branch)
    child = next(a for a in group.animations
                 if type(a).__module__.startswith("manim"))
    assert getattr(child, "starting_mobject", None) is not None


def test_nested_group_carriers_are_presented():
    """The play-side walker recurses ONE level; ``.mobjects`` closes the gap.

    ``AnimationGroup(AnimationGroup(FadeIn(new)))`` -- the inner group's
    target used to be invisible to the walker (a nested carrier gap of the
    same A22 family).
    """
    new = Square()
    outer = AnimationGroup(AnimationGroup(FadeIn(new)))
    scene = _present([outer])
    assert new in scene.mobjects, (
        "a nested group's FadeIn target was never presented: the walker "
        "reads `.mobject`/`.mobjects`, and a bare group exposed neither")


def test_carriers_are_reachable_at_any_depth_via_mobjects_property():
    """``AnimationGroup.mobjects`` flattens carriers through any nesting."""
    new1, new2 = Square(), Square()
    inner = Succession(FadeIn(new1), FadeIn(new2))
    outer = AnimationGroup(inner)
    carriers = outer.mobjects
    assert new1 in carriers and new2 in carriers


def test_setup_scene_hook_registers_introducer_children():
    """manim's ``AnimationGroup._setup_scene`` recurses; RTM had none at all.

    Any caller following manim's convention (``Scene.begin_animations``,
    ``window.scene._setup_anim_scene``) registered NOTHING for an RTM group.
    """
    new = Square()
    group = AnimationGroup(FadeIn(new))
    scene = StubScene()
    group._setup_scene(scene)
    assert new in scene.mobjects, (
        "_setup_scene must add a child's carriers when the child has no "
        "hook of its own (RTM's FadeIn)")


def test_setup_scene_recurses_into_manim_children():
    """A manim-native child keeps its own introducer registration."""
    from manim.animation.creation import Create as ManimCreate
    mob = Square()
    group = AnimationGroup(ManimCreate(mob))
    scene = StubScene()
    group._setup_scene(scene)
    assert mob in scene.mobjects


# --------------------------------------------------------------------------- #
# regressions pinned by the subclassing / scheduling changes
# --------------------------------------------------------------------------- #

def test_nested_add_extraction_still_defers_inside_succession():
    """``Succession`` now subclasses ``AnimationGroup``; keep the Add path.

    ``PlayMixin._extract_add_mobjects`` recurses into ``Succession`` /
    ``AnimationGroup`` children with ``_nested=True`` so a queued ``Add``'s
    mobject is parked at opacity 0 until its own slot runs.  The subclassing
    must not lose that: an Add nested in a Succession still comes back
    deferred, not visible from play start.
    """
    mob = Square()
    succ = Succession(Add(mob))
    got = PlayMixin._extract_add_mobjects(StubWindow(StubScene()), succ)
    assert got == [mob]
    assert getattr(mob, "_rtm_deferred_add", False) is True
    assert get_anim_opacity(mob) == 0.0


def test_succession_subclasses_the_group_and_keeps_linear_default():
    """CE: ``class Succession(AnimationGroup)`` with linear rate_func."""
    succ = Succession(Create(Square()))
    assert isinstance(succ, AnimationGroup)
    assert succ.rate_func(0.25) == pytest.approx(0.25)
    assert succ.lag_ratio == 1


def test_blink_and_circumscribe_still_build():
    """Both pass an explicit ``run_time=`` to Succession (A14 consumer)."""
    from real_time_manim.animations.blink import Blink
    from real_time_manim.animations.circumscribe import Circumscribe

    blink = Blink(Square(), time_on=0.1, time_off=0.2, blinks=2)
    # [on, off, on, off] + a final on
    assert blink.run_time == pytest.approx(0.1 + 0.2 + 0.1 + 0.2 + 0.1)

    circ = Circumscribe(Square())
    assert circ.run_time == pytest.approx(1.0)
    circ.begin(0.0)
    circ.interpolate(1.0)


def test_group_lag_starts_follow_ce_formula_with_unequal_runs():
    """``start[i+1] = start[i] + run_time[i] * lag_ratio`` (wiki line 13).

    The old ``i * lag_ratio`` only agreed with CE while every child ran for
    exactly 1.0 s: a 2.0 s child followed by a 1.0 s child at lag 0.5 starts
    its second child at 1.0 s (CE), not at 0.5 s.
    """
    a, b = Square(), Square()
    grp = AnimationGroup(Create(a, run_time=2.0), Create(b, run_time=1.0),
                         lag_ratio=0.5)
    assert grp.animations[0]._group_start == pytest.approx(0.0)
    assert grp.animations[1]._group_start == pytest.approx(1.0)
    assert grp.run_time == pytest.approx(2.0)
    grp.begin(0.0)
    grp.interpolate(0.99)                    # b has not started yet
    assert _progress(b) is None
    grp.interpolate(1.5)                     # b half done
    assert _progress(b) == pytest.approx(_smooth(0.5), abs=1e-6)
