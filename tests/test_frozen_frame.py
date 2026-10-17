"""Feature/regression: ``frozen_frame`` must actually freeze (wiki 03-播放与等待).

manim's ``Wait(run_time, stop_condition, frozen_frame)``:

* ``frozen_frame=True``  -> CE's ``freeze_current_frame``: ONE picture repeated,
  with NO updater pass anywhere inside the wait (``pause()`` is this).
* ``frozen_frame=False`` -> the wait steps like a normal animation: updaters
  keep running every frame.
* ``frozen_frame=None``  -> auto: static iff no always_update / scene updater /
  stop_condition / time-based mobject updater (``should_update_mobjects``).

Before this fix RTM honoured the flag only in the frame *count*
(``resolve_static_wait``/``ce_frame_count``) and ``Timeline.render_at`` drove
updaters straight through the wait, so ``self.pause(2)`` in a scene with
updaters kept moving -- the wiki documented frozen_frame as "don't pass it".

Also covers BUG_REPORT L6: RTM's own ``Wait`` (not a manim subclass) now goes
through the same resolution, and its ``stop_condition``/``frozen_frame``
keywords are stored instead of vanishing into ``**kwargs``.

Pure Python: stub window/scene, no DLL, no GPU.
"""
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import pytest

from manim import Square, Wait as ManimWait

from real_time_manim.animations.wait import Wait as RtmWait
from real_time_manim.window.play import PlayMixin, TARGET_FPS
from real_time_manim.timeline import (
    Timeline,
    ce_frame_count,
    resolve_static_wait,
)


class StubScene:
    """The bits the frozen path touches: mobjects, updaters, family walk."""

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
    def sync(self, scene):
        pass

    def tick(self):
        return True


def _scene_with_counter():
    """A scene holding one square whose updater records every driver call."""
    scene = StubScene()
    sq = Square()
    ticks = []
    sq.add_updater(lambda m, dt: ticks.append(dt))
    scene.add(sq)
    return scene, ticks


def _timeline(scene, *anims, starts=None):
    tl = Timeline(StubWindow(), scene)
    if starts is None:
        starts = [0.0] * len(anims)
    for anim, start in zip(anims, starts):
        tl.add(anim, start)
    tl.finalize()
    return tl


# ---------------------------------------------------------------------------
# RTM's Wait carries the knobs
# ---------------------------------------------------------------------------

def test_rtm_wait_stores_stop_condition_and_frozen_frame():
    """The kwargs used to fall into **kwargs and disappear."""
    w = RtmWait(2.0, stop_condition=lambda: True)
    assert w.stop_condition is not None
    assert w.is_static_wait is None        # auto: resolved later

    f = RtmWait(2.0, frozen_frame=True)
    assert f.is_static_wait is True
    assert f.stop_condition is None

    g = RtmWait(2.0, frozen_frame=False)
    assert g.is_static_wait is False


def test_rtm_wait_rejects_static_with_condition():
    """CE's Wait raises; RTM's must too."""
    with pytest.raises(ValueError):
        RtmWait(1.0, stop_condition=lambda: True, frozen_frame=True)


# ---------------------------------------------------------------------------
# Resolution + counting accept RTM's Wait (BUG_REPORT L6)
# ---------------------------------------------------------------------------

def test_resolve_static_wait_accepts_rtm_wait():
    """Plain scene -> static; scene with a time-based updater -> stepped."""
    plain = StubScene()
    w = RtmWait(0.3)
    resolve_static_wait(plain, [w])
    assert w.is_static_wait is True

    moving, _ = _scene_with_counter()
    w2 = RtmWait(0.3)
    resolve_static_wait(moving, [w2])
    assert w2.is_static_wait is False


def test_ce_frame_count_frozen_for_rtm_wait():
    """``Wait(0.3)`` @15fps: manim writes 4 frames, the stepper wrote 5."""
    frozen = RtmWait(0.3)
    frozen.is_static_wait = True
    assert ce_frame_count([frozen], 0.3, 15) == 4

    stepped = RtmWait(0.3)
    stepped.is_static_wait = False
    assert ce_frame_count([stepped], 0.3, 15) == 5


# ---------------------------------------------------------------------------
# The feature: a frozen wait holds the picture
# ---------------------------------------------------------------------------

def test_frozen_wait_drives_no_updaters():
    """The reported case: pause()/frozen_frame=True must NOT step updaters."""
    scene, ticks = _scene_with_counter()
    wait = ManimWait(0.5, frozen_frame=True)
    resolve_static_wait(scene, [wait])          # explicit True wins
    tl = _timeline(scene, wait)

    n = ce_frame_count([wait], 0.5, TARGET_FPS)
    for k in range(n):
        tl.render_at(k / TARGET_FPS)
    assert n > 0
    assert ticks == [], ticks                    # picture held for the whole wait


def test_updaters_resume_after_the_frozen_window():
    """The frame after the wait steps exactly ONE frame of dt, not the span."""
    scene, ticks = _scene_with_counter()
    wait = ManimWait(0.5, frozen_frame=True)
    tl = _timeline(scene, wait)

    n = ce_frame_count([wait], 0.5, TARGET_FPS)
    for k in range(n):
        tl.render_at(k / TARGET_FPS)
    assert ticks == []

    tl.render_at(n / TARGET_FPS)                 # first frame past the window
    assert len(ticks) == 1, ticks
    assert abs(ticks[0] - 1.0 / TARGET_FPS) < 1e-9, ticks


def test_dynamic_wait_steps_updaters_every_frame():
    """Auto-resolved dynamic wait (updaters present): CE steps it, so does RTM."""
    scene, ticks = _scene_with_counter()
    wait = ManimWait(0.5)
    resolve_static_wait(scene, [wait])
    assert wait.is_static_wait is False          # time-based updater -> step

    tl = _timeline(scene, wait)
    n = ce_frame_count([wait], 0.5, TARGET_FPS)
    for k in range(n):
        tl.render_at(k / TARGET_FPS)
    assert len(ticks) == n, (len(ticks), n)


def test_wait_sharing_the_play_is_not_frozen():
    """CE freezes only a LONE wait; a concurrent animation means play_internal."""
    scene = StubScene()
    wait = ManimWait(0.5, frozen_frame=True)
    other = RtmWait(0.3)
    tl = _timeline(scene, wait, other)           # both at t=0
    assert tl._frozen_windows == [], tl._frozen_windows


def test_contiguous_waits_each_keep_their_own_window():
    """Schedule mode: consecutive lone waits are separate frozen windows."""
    scene = StubScene()
    w1 = ManimWait(0.5, frozen_frame=True)
    w2 = ManimWait(0.5, frozen_frame=True)
    tl = _timeline(scene, w1, w2, starts=[0.0, 0.5])
    assert len(tl._frozen_windows) == 2, tl._frozen_windows
    assert tl._frozen_at(0.4999) is True
    assert tl._frozen_at(0.5) is True            # inside w2
    assert tl._frozen_at(0.9999) is True
    assert tl._frozen_at(1.0) is False           # past both


# ---------------------------------------------------------------------------
# _run_timeline: no trailing dt=0 pass after a frozen wait
# ---------------------------------------------------------------------------

class RunStubTimeline:
    def __init__(self, duration):
        self.duration = duration
        self._entries = []
        self.render_calls = 0

    def render_at(self, t, **kwargs):
        self.render_calls += 1
        return True


class RunStubWindow:
    def __init__(self):
        self._fast_record = False
        self.scene = StubScene()

    def _capture_frame(self):
        pass


def _run_trailing_drive(monkeypatch, wait):
    """Run _run_timeline and return the dt=0 re-anchor calls it made."""
    import real_time_manim.window.play as play_mod

    calls = []
    monkeypatch.setattr(
        play_mod, "_drive_mobject_updaters",
        lambda scene, dt, *a, **k: calls.append(dt))
    tl = RunStubTimeline(duration=0.5)
    PlayMixin._run_timeline(RunStubWindow(), tl, [wait])
    return calls, tl


def test_run_timeline_skips_trailing_pass_for_frozen_wait(monkeypatch):
    """CE's frozen branch never enters play_internal -> no update_mobjects(0)."""
    wait = ManimWait(0.5, frozen_frame=True)
    calls, tl = _run_trailing_drive(monkeypatch, wait)
    assert tl.render_calls > 0                  # the wait did render
    assert calls == [], calls


def test_run_timeline_keeps_trailing_pass_for_dynamic_wait(monkeypatch):
    """Every other play (dynamic wait included) keeps the dt=0 re-anchor."""
    wait = ManimWait(0.5, frozen_frame=False)
    calls, tl = _run_trailing_drive(monkeypatch, wait)
    assert tl.render_calls > 0
    assert calls == [0.0], calls


# ---------------------------------------------------------------------------
# Schedule mode resolves waits too
# ---------------------------------------------------------------------------

class ScheduleStub(PlayMixin):
    def __init__(self):
        self.scene = StubScene()
        self._sched = []
        self._cursor = 0.0

    def _extract_add_mobjects(self, anim):
        return []

    def _ensure_animated_present(self, real, add_mobs):
        return []


def test_schedule_play_resolves_static_wait():
    """A recorded pause/wait must get is_static_wait like the live path."""
    win = ScheduleStub()
    win._schedule_play([RtmWait(0.3)], {})
    assert win._sched, win._sched
    assert win._sched[0][1].is_static_wait is True
    assert len(win._sched) == 1
