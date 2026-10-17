"""Gap regression tests: Animation accessors, Wait knobs, lifecycle, Scene.time.

Maps onto the wiki's open-gap list (RTM-Wiki):

* **A1** -- RTM's own ``Animation`` implemented ``set_rate_func`` only; every
  other chainable accessor raised ``AttributeError`` on call
  (``03-动画/通用/01-生命周期与公共参数``).
* **A2** -- ``Wait(stop_condition=...)``: the keyword used to vanish into
  ``**kwargs`` and the condition was evaluated 0 times
  (``03-动画/等待与变速/01-等待速率与变速``).  The constructor now keeps it and
  a forward timeline render evaluates it once per frame and truncates.
* **A3** -- ``Wait(frozen_frame=True)`` must hold the picture (no updater pass
  anywhere inside the wait) and be counted the way CE freezes a frame.
* **A4** -- ``Scene.pause`` is ``wait(..., frozen_frame=True)``: a frozen
  frame, not an ordinary stepping wait (``03-动画/通用/02-play与wait参数``).
* **A5** -- ``Scene.wait_until(cond, max_time)`` must evaluate ``cond`` per
  frame and end early (``01-场景与相机/场景/03-播放与等待``).
* **A8** -- ``Scene.tear_down`` was never called: the record lifecycle ran
  ``setup()`` + ``construct()`` only (``01-场景与相机/场景/01-Scene基础``).
* **A9** -- ``Scene.time`` stayed ``0.0`` for a whole scene because RTM emits
  frames itself and never advanced the renderer clock (same page).
* **A30** -- the wiki's Succession-with-Wait sample counts 204 frames where CE
  counts 205 (``03-动画/组合编排/assets/README``): asserted here that the
  timeline's counting *rule* is CE's ``np.arange`` rule, i.e. any remaining
  gap comes from the duration ``animations/succession.py`` hands it, not from
  the counting.

Pure Python: stub windows for every timeline path; one tiny hidden window for
the end-to-end lifecycle/``Scene.time`` check (no encoding, no ffmpeg, no
visible window).
"""
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np
import pytest

import real_time_manim  # noqa: F401  -- installs the BUNDLED manim + compat shims
                        # (must precede every ``from manim import ...``: the
                        # system manim from site-packages would otherwise claim
                        # ``sys.modules["manim"]`` first and every module that
                        # relies on the bundle's patched behaviour fails).

from manim import Mobject, Scene, Square, Wait as ManimWait
from manim.animation.animation import Animation as ManimAnimation
from manim.animation.composition import Succession as ManimSuccession

from real_time_manim.animations.base import Animation as RtmAnimation
from real_time_manim.animations.wait import Wait as RtmWait
from real_time_manim.record import scene_lifecycle
from real_time_manim.timeline import Timeline, ce_frame_count, resolve_static_wait
from real_time_manim.window.play import PlayMixin, TARGET_FPS

DT = 1.0 / TARGET_FPS


# ---------------------------------------------------------------------------
# stubs (no DLL, no GPU)
# ---------------------------------------------------------------------------

class StubScene:
    """The bits the timeline touches: mobjects, updaters, family walk."""

    def __init__(self):
        self.mobjects = []
        self.updaters = []

    def add(self, mob):
        self.mobjects.append(mob)

    def get_mobject_family_members(self):
        members = []
        for root in self.mobjects:
            members.extend(root.get_family())
        return members


class StubWindow:
    """A window that draws nothing: counts drawn frames, remembers screenshots."""

    dll = None

    def __init__(self):
        self.frames = 0
        self.shots = []

    def sync(self, scene):
        pass

    def tick(self):
        self.frames += 1
        return True

    def request_readback(self):
        pass

    def screenshot(self, path):
        self.shots.append(path)
        return True


class StubRunWindow:
    """What ``PlayMixin._run_timeline`` needs (live path, no recording)."""

    _fast_record = False

    def __init__(self):
        self.scene = StubScene()

    def _capture_frame(self):
        pass


class StubRunTimeline:
    """Counts rendered frames for ``_run_timeline``."""

    def __init__(self, duration):
        self.duration = duration
        self._entries = []
        self.render_calls = 0

    def render_at(self, t, **kwargs):
        self.render_calls += 1
        return True


def _timeline(scene, *anims, starts=None):
    tl = Timeline(StubWindow(), scene)
    if starts is None:
        starts = [0.0] * len(anims)
    for anim, start in zip(anims, starts):
        tl.add(anim, start)
    tl.finalize()
    return tl


def _scene_with_counter():
    """A scene holding one square whose updater records every driver call."""
    scene = StubScene()
    sq = Square()
    ticks = []
    sq.add_updater(lambda m, dt: ticks.append(dt))
    scene.add(sq)
    return scene, ticks


def _captured_wait(call):
    """Run ``call`` against a Scene whose ``play`` records instead of rendering."""
    scene = Scene()
    captured = []
    scene.play = lambda *anims, **kwargs: captured.extend(anims)
    call(scene)
    assert len(captured) == 1, captured
    return captured[0]


# ---------------------------------------------------------------------------
# A1 -- manim's chainable Animation API
# ---------------------------------------------------------------------------

def test_a1_chainable_accessors_exist_and_behave():
    """set_run_time/set_name/get_* are implemented, chainable and take effect."""
    a = RtmAnimation(Square(), run_time=1.5, name="orig")

    assert a.set_run_time(2.5) is a
    assert a.get_run_time() == 2.5
    assert a.run_time == 2.5

    f = lambda x: x
    assert a.set_rate_func(f) is a
    assert a.get_rate_func() is f
    assert a.rate_func is f

    assert a.set_name("renamed") is a
    assert str(a) == "renamed"


def test_a1_introducer_and_remover_flags():
    plain = RtmAnimation(Square())
    assert plain.is_introducer() is False
    assert plain.is_remover() is False
    assert RtmAnimation(Square(), introducer=True).is_introducer() is True
    assert RtmAnimation(Square(), remover=True).is_remover() is True


def test_a1_copy_is_independent_of_the_original():
    """manim's ``Animation.copy`` is a deepcopy: mutating one must not leak."""
    a = RtmAnimation(Square(), run_time=1.0, name="orig")
    b = a.copy()

    assert b is not a
    assert b.mobject is not a.mobject          # its own copy of the mobject
    b.set_run_time(9.0).set_name("copy")
    assert a.get_run_time() == 1.0
    assert str(a) == "orig"


# ---------------------------------------------------------------------------
# A2 -- Wait(stop_condition=...) is stored and evaluated on a forward render
# ---------------------------------------------------------------------------

def test_a2_wait_keeps_stop_condition_and_rejects_frozen_pair():
    w = RtmWait(2.0, stop_condition=lambda: True)
    assert w.stop_condition is not None
    assert w.is_static_wait is None            # auto: resolved by the timeline

    with pytest.raises(ValueError):            # manim raises the same
        RtmWait(1.0, stop_condition=lambda: True, frozen_frame=True)


def test_a2_forward_render_ends_on_the_frame_the_condition_fires(monkeypatch,
                                                                tmp_path):
    """A forward ``render_mp4`` writes only the frames up to the firing one."""
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return calls["n"] >= 3

    scene = StubScene()
    wait = RtmWait(0.5, stop_condition=cond)
    resolve_static_wait(scene, [wait])
    assert wait.is_static_wait is False        # a condition waits dynamically
    tl = _timeline(scene, wait)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    tl.render_mp4(str(tmp_path / "out.mp4"), fps=TARGET_FPS)

    full = ce_frame_count([wait], 0.5, TARGET_FPS)
    assert full == 30                          # the untruncated schedule
    assert len(tl.window.shots) == 3, tl.window.shots   # fired after frame 3
    assert calls["n"] == 3                     # one evaluation per drawn frame


def test_a2_forward_render_runs_full_length_when_condition_never_fires(
        monkeypatch, tmp_path):
    scene = StubScene()
    wait = RtmWait(0.5, stop_condition=lambda: False)
    resolve_static_wait(scene, [wait])
    tl = _timeline(scene, wait)

    monkeypatch.setattr(subprocess, "run", lambda *a, **k: None)
    tl.render_mp4(str(tmp_path / "out.mp4"), fps=TARGET_FPS)

    assert len(tl.window.shots) == ce_frame_count([wait], 0.5, TARGET_FPS)


def test_a2_live_play_path_truncates_rtm_waits_too():
    """``win.play(Wait(0.5, stop_condition=cond))`` -- RTM's own Wait class.

    The live path (``PlayMixin._run_timeline``) finds the condition on the
    animation and ends the play on the frame it fires, exactly like CE's
    renderer loop.
    """
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return calls["n"] >= 4

    wait = RtmWait(0.5, stop_condition=cond)
    resolve_static_wait(StubScene(), [wait])
    tl = StubRunTimeline(duration=0.5)
    elapsed = PlayMixin._run_timeline(StubRunWindow(), tl, [wait])

    assert tl.render_calls == 4
    assert abs(elapsed - 4 * DT) < 1e-9
    assert calls["n"] == 4


def test_a2_random_access_frames_never_poll_the_condition():
    """Seeking never evaluates the condition (wiki 03-播放与等待: forward-only)."""
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return True

    scene = StubScene()
    wait = RtmWait(0.5, stop_condition=cond)
    tl = _timeline(scene, wait)

    for t in (0.0, 0.1, 0.3, 0.49, 0.1):
        tl.render_at(t)
    assert calls["n"] == 0, calls              # full-duration schedule intact
    assert tl.window.frames == 5               # ...frames were drawn as usual


# ---------------------------------------------------------------------------
# A3 -- Wait(frozen_frame=True) really freezes
# ---------------------------------------------------------------------------

def test_a3_frozen_rtm_wait_holds_the_picture():
    scene, ticks = _scene_with_counter()
    wait = RtmWait(0.5, frozen_frame=True)
    resolve_static_wait(scene, [wait])         # explicit True wins over updaters
    assert wait.is_static_wait is True
    tl = _timeline(scene, wait)

    n = ce_frame_count([wait], 0.5, TARGET_FPS)
    assert n == int(0.5 * TARGET_FPS)          # CE's freeze rule: int(duration/dt)
    for k in range(n):
        tl.render_at(k * DT)
    assert ticks == [], ticks                  # picture held for the whole wait

    tl.render_at(0.5)                          # first frame past the window
    assert len(ticks) == 1, ticks              # stepping resumes exactly there
    assert ticks[0] == pytest.approx(DT)


def test_a3_frozen_wait_counts_with_int_while_stepped_uses_arange():
    """The int-vs-arange signature CE shows for frozen vs stepped waits."""
    frozen = RtmWait(0.3, frozen_frame=True)
    assert ce_frame_count([frozen], 0.3, 15) == 4        # int(0.3 * 15)
    stepped = RtmWait(0.3, frozen_frame=False)
    assert ce_frame_count([stepped], 0.3, 15) == 5       # arange


def test_a3_auto_resolution_is_untouched_by_explicit_flags():
    """``frozen_frame=False`` keeps stepping even in a plain scene."""
    scene = StubScene()
    wait = RtmWait(0.3, frozen_frame=False)
    resolve_static_wait(scene, [wait])
    assert wait.is_static_wait is False


# ---------------------------------------------------------------------------
# A4 -- Scene.pause is a frozen wait, Scene.wait is not
# ---------------------------------------------------------------------------

def test_a4_pause_builds_a_frozen_wait_while_wait_steps():
    pause_wait = _captured_wait(lambda scene: scene.pause(0.3))
    assert isinstance(pause_wait, ManimWait)
    assert pause_wait.run_time == 0.3
    assert pause_wait.is_static_wait is True   # frozen_frame=True wired through

    plain_wait = _captured_wait(lambda scene: scene.wait(0.3))
    assert isinstance(plain_wait, ManimWait)
    assert plain_wait.run_time == 0.3
    assert plain_wait.is_static_wait is None   # auto: scene decides

    # The behavioural difference: in a scene WITH updaters the plain wait
    # steps them (the picture moves) while the pause holds it.
    scene, ticks = _scene_with_counter()
    resolve_static_wait(scene, [pause_wait])
    assert pause_wait.is_static_wait is True
    tl = _timeline(scene, pause_wait)
    for k in range(ce_frame_count([pause_wait], 0.3, TARGET_FPS)):
        tl.render_at(k * DT)
    assert ticks == [], ticks                  # frozen: nothing moved

    scene2, ticks2 = _scene_with_counter()
    resolve_static_wait(scene2, [plain_wait])
    assert plain_wait.is_static_wait is False  # time-based updater -> step
    tl2 = _timeline(scene2, plain_wait)
    n = ce_frame_count([plain_wait], 0.3, TARGET_FPS)
    for k in range(n):
        tl2.render_at(k * DT)
    assert len(ticks2) == n, (len(ticks2), n)


# ---------------------------------------------------------------------------
# A5 -- Scene.wait_until(stop_condition, max_time)
# ---------------------------------------------------------------------------

def test_a5_wait_until_carries_the_condition_and_stops_early():
    calls = {"n": 0}

    def cond():
        calls["n"] += 1
        return calls["n"] >= 3

    wait = _captured_wait(lambda scene: scene.wait_until(cond, max_time=0.5))
    assert isinstance(wait, ManimWait)
    assert wait.run_time == 0.5
    assert wait.stop_condition is cond         # the keyword reached the Wait

    tl = StubRunTimeline(duration=wait.run_time)
    elapsed = PlayMixin._run_timeline(StubRunWindow(), tl, [wait])

    full = ce_frame_count([wait], 0.5, TARGET_FPS)
    assert tl.render_calls == 3 < full         # ended early, not max_time
    assert abs(elapsed - 3 * DT) < 1e-9        # real elapsed time reported


def test_a5_wait_until_runs_the_full_max_time_when_condition_never_true():
    wait = _captured_wait(
        lambda scene: scene.wait_until(lambda: False, max_time=0.5))
    tl = StubRunTimeline(duration=wait.run_time)
    elapsed = PlayMixin._run_timeline(StubRunWindow(), tl, [wait])
    assert tl.render_calls == ce_frame_count([wait], 0.5, TARGET_FPS)
    assert elapsed is None                     # not truncated -> full schedule


# ---------------------------------------------------------------------------
# A8 -- the record lifecycle calls Scene.tear_down
# ---------------------------------------------------------------------------

class _Hooked(Scene):
    """Records lifecycle order; ``boom`` makes construct() raise."""

    boom = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.events = []

    def setup(self):
        self.events.append("setup")

    def construct(self):
        self.events.append("construct")
        if self.boom:
            raise RuntimeError("construct exploded")

    def tear_down(self):
        self.events.append("tear_down")


def test_a8_lifecycle_runs_teardown_after_construct():
    scene = _Hooked()
    scene_lifecycle(scene)
    assert scene.events == ["setup", "construct", "tear_down"]


def test_a8_lifecycle_runs_teardown_when_construct_raises():
    class Boom(_Hooked):
        boom = True

    scene = Boom()
    with pytest.raises(RuntimeError, match="construct exploded"):
        scene_lifecycle(scene)
    assert scene.events == ["setup", "construct", "tear_down"]


def test_a8_teardown_runs_once_per_lifecycle_run():
    """No double cleanup: exactly one teardown per construct."""
    scene = _Hooked()
    scene_lifecycle(scene)
    assert scene.events.count("tear_down") == 1


# ---------------------------------------------------------------------------
# A9 -- Scene.time advances with the emitted frames
# ---------------------------------------------------------------------------

def test_a9_scene_time_advances_one_frame_duration_per_frame():
    scene = Scene()
    tl = _timeline(scene, RtmWait(0.5))
    assert scene.time == 0.0

    n = 6
    for k in range(n):
        tl.render_at(k * DT)
        # CE runs the updater pass BEFORE writing the frame, so an updater
        # reading scene.time sees the time of the frames already written --
        # frame k has just been emitted, i.e. (k + 1) frames worth of time.
        assert scene.time == pytest.approx((k + 1) * DT, abs=1e-12)

    assert scene.time == pytest.approx(n * DT, abs=1e-12)


def test_a9_scene_time_accumulates_across_schedules():
    """Each play is its own Timeline; the clock must keep counting across them."""
    scene = Scene()
    for _ in range(3):
        tl = _timeline(scene, RtmWait(2 / TARGET_FPS))
        for k in range(2):
            tl.render_at(k * DT)
    assert scene.time == pytest.approx(6 * DT, abs=1e-12)


def test_a9_backwards_or_repeated_frames_do_not_advance_the_clock():
    scene = Scene()
    tl = _timeline(scene, RtmWait(0.5))
    for k in range(4):
        tl.render_at(k * DT)
    after = scene.time
    assert after == pytest.approx(4 * DT, abs=1e-12)

    tl.render_at(0.0)                          # backwards seek: never rewinds
    tl.render_at(0.0)                          # the same t again: nothing new
    assert scene.time == pytest.approx(after, abs=1e-12)

    tl.render_at(1 * DT)                       # forward again: one frame's worth
    assert scene.time == pytest.approx(after + DT, abs=1e-12)


def test_a8_a9_end_to_end_record_lifecycle():
    """Through the real record path: teardown runs and Scene.time advances."""
    from real_time_manim.window import MLWindow

    class Tracked(Scene):
        def setup(self):
            self.events = ["setup"]

        def construct(self):
            self.events.append("construct")
            win = MLWindow(1920, 1080, hidden=True)
            win.scene = self
            before = win.frame_count
            win.play(RtmWait(1.0 / 15.0))      # 4 frames @60fps
            self.emitted = win.frame_count - before
            win.close()

        def tear_down(self):
            self.events.append("tear_down")

    scene = Tracked()
    scene_lifecycle(scene)

    assert scene.events == ["setup", "construct", "tear_down"]
    assert scene.emitted > 0
    # CE adds one dt to the renderer clock for every frame it writes
    # (CairoRenderer.add_frame); RTM's timeline now does the same.
    assert scene.time == pytest.approx(scene.emitted * DT, abs=1e-9)


# ---------------------------------------------------------------------------
# A30 -- frame counting for a Succession containing a Wait
# ---------------------------------------------------------------------------

def _ce_succession():
    """The succession the wiki sample plays (1.0 + 1.0 + Wait(0.6) + 0.8)."""
    return ManimSuccession(
        ManimAnimation(Mobject(), run_time=1.0),
        ManimAnimation(Mobject(), run_time=1.0),
        ManimWait(0.6),
        ManimAnimation(Mobject(), run_time=0.8),
    )


def test_a30_timeline_counts_frames_with_ce_arange_rule():
    """CE's measured count for that play is 205 frames; reproduce it exactly.

    The timeline derives its frame count from ``np.arange(0, duration, 1/fps)``
    -- the very rule manim's ``Scene.get_time_progression`` uses -- so for the
    duration CE's own ``Succession.run_time`` reports it must answer 205.  The
    wiki's 204-vs-205 gap is therefore not a counting-rule difference: it is
    the duration ``real_time_manim/animations/succession.py`` computes
    (``sum()`` = Neumaier-accurate 3.4 vs manim's naive accumulation
    3.4000000000000004 -- 1 ULP apart, and that ULP straddles a frame
    boundary).  That file belongs to another session; nothing here changes it.
    """
    succ = _ce_succession()
    ce_duration = float(succ.run_time)
    assert ce_frame_count([succ], ce_duration, 60) == 205

    # ...and whatever duration it is handed, the timeline applies CE's rule.
    for duration in (3.4, 3.4000000000000004, ce_duration, 0.5, 1.0 / 3.0):
        expected = len(np.arange(0.0, duration, 1.0 / 60.0))
        assert ce_frame_count([succ], duration, 60) == expected, duration


def test_a30_timeline_counts_rtms_succession_with_the_same_rule():
    """RTM's Succession is counted by the same rule as CE's, whatever duration.

    Fails only if the counting rule itself drifts; the duration it is handed
    lives in ``animations/succession.py`` (see the test above).
    """
    from real_time_manim.animations.succession import Succession as RtmSuccession

    succ = RtmSuccession(
        RtmAnimation(Mobject(), run_time=1.0),
        RtmAnimation(Mobject(), run_time=1.0),
        RtmWait(0.6),
        RtmAnimation(Mobject(), run_time=0.8),
    )
    duration = float(succ.run_time)
    assert ce_frame_count([succ], duration, 60) == len(
        np.arange(0.0, duration, 1.0 / 60.0))
